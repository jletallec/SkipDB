from flask import Flask, render_template_string, request
from db import download_skip_db_json, get_skipped_episodes, get_all_show_ids, get_show_title
from tmdb import show_id_to_tmdb_id, get_tmdb_seasons, get_tmdb_episodes, get_show_title_tmdb
from translations import TRANSLATIONS
import re

app = Flask(__name__)

title_cache = {}
seasons_cache = {}
episodes_cache = {}

@app.route("/")
def index():
    lang = request.args.get("lang", "en")
    lang_code = "fr-FR" if lang == "fr" else "en-US"
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    skip_db = download_skip_db_json()
    if not skip_db:
        return "Error downloading the database."
    shows = []
    for show_id in get_all_show_ids(skip_db):
        tmdb_id = show_id_to_tmdb_id(show_id)
        if not tmdb_id:
            continue

        # --- Titre ---
        title_key = (tmdb_id, lang_code)
        if title_key in title_cache:
            title = title_cache[title_key]
        else:
            try:
                title = get_show_title_tmdb(tmdb_id, lang=lang_code)
            except Exception:
                title = get_show_title(skip_db, show_id)
            title_cache[title_key] = title

        # --- Saisons ---
        if (tmdb_id, lang_code) in seasons_cache:
            seasons = seasons_cache[(tmdb_id, lang_code)]
        else:
            try:
                seasons = get_tmdb_seasons(tmdb_id, lang=lang_code)
            except Exception:
                continue
            seasons_cache[(tmdb_id, lang_code)] = seasons

        total_eps = 0
        skipped_eps = set(get_skipped_episodes(skip_db, show_id))
        for season in seasons:
            if season["season_number"] == 0:
                continue
            season_key = (tmdb_id, season["season_number"], lang_code)
            if season_key in episodes_cache:
                eps = episodes_cache[season_key]
            else:
                try:
                    eps = get_tmdb_episodes(tmdb_id, season["season_number"], lang=lang_code)
                except Exception:
                    continue
                episodes_cache[season_key] = eps
            total_eps += len(eps)
        percent = int((len(skipped_eps) / total_eps) * 100) if total_eps else 0
        shows.append({
            "show_id": show_id,
            "title": title,
            "total_eps": total_eps,
            "skipped_eps": len(skipped_eps),
            "missing_eps": total_eps - len(skipped_eps),
            "percent": percent
        })

    # Sort from most complete to least complete
    shows.sort(key=lambda s: s["percent"], reverse=True)
    return render_template_string("""
    <style>
    .progress-bar-bg {
      width: 120px; height: 18px; background: #eee; border-radius: 8px; display: inline-block; vertical-align: middle; margin-right: 8px;
    }
    .progress-bar-fill {
      height: 100%; background: #4caf50; border-radius: 8px 0 0 8px; display: inline-block;
    }
    .progress-bar-text {
      display: inline-block; min-width: 32px; text-align: right; font-size: 0.95em;
    }
    #search-bar {
      margin-right: 1em;
      padding: 0.3em 0.7em;
      font-size: 1em;
      border-radius: 6px;
      border: 1px solid #bbb;
    }
    </style>
    <div style="position:fixed;top:1em;right:2em;display:flex;align-items:center;gap:1em;">
      <input id="search-bar" type="text" placeholder="🔍 Recherche..." onkeyup="filterTable()" />
      <form method="get" id="langform" style="margin:0;">
        <label>{{ t.language }} :
          <select name="lang" onchange="document.getElementById('langform').submit()">
            <option value="fr" {% if lang == 'fr' %}selected{% endif %}>Français</option>
            <option value="en" {% if lang == 'en' %}selected{% endif %}>English</option>
          </select>
        </label>
      </form>
    </div>
    <h1 style="margin-top:3em;">SkipDB</h1>
    <table border=1 id="shows-table">
      <tr>
        <th>{{ t.series }}</th>
        <th>{{ t.total_eps }}</th>
        <th>{{ t.with_skip }}</th>
        <th>{{ t.without_skip }}</th>
        <th>{% if lang == 'fr' %}Progression{% else %}Progress{% endif %}</th>
      </tr>
      {% for show in shows %}
        <tr>
          <td><a href="{{ url_for('show_detail', show_id=show.show_id, lang=lang) }}">{{ show.title }}</a></td>
          <td>{{ show.total_eps }}</td>
          <td>{{ show.skipped_eps }}</td>
          <td>{{ show.missing_eps }}</td>
          <td>
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" style="width:{{ show.percent }}%;"></div>
            </div>
            <span class="progress-bar-text">{{ show.percent }}%</span>
          </td>
        </tr>
      {% endfor %}
    </table>
    <script>
    function filterTable() {
      var input = document.getElementById("search-bar");
      var filter = input.value.toLowerCase();
      var table = document.getElementById("shows-table");
      var trs = table.getElementsByTagName("tr");
      for (var i = 1; i < trs.length; i++) {
        var td = trs[i].getElementsByTagName("td")[0];
        if (td) {
          var txt = td.textContent || td.innerText;
          trs[i].style.display = txt.toLowerCase().indexOf(filter) > -1 ? "" : "none";
        }
      }
    }
    </script>
    """, shows=shows, lang=lang, t=t)

@app.route("/show/<show_id>")
def show_detail(show_id):
    lang = request.args.get("lang", "en")
    lang_code = "fr-FR" if lang == "fr" else "en-US"
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    skip_db = download_skip_db_json()
    if not skip_db:
        return "Error while downloading the database."
    tmdb_id = show_id_to_tmdb_id(show_id)
    if not tmdb_id:
        return "Series not found"
    try:
        title = get_show_title_tmdb(tmdb_id, lang=lang_code)
    except Exception:
        title = get_show_title(skip_db, show_id)
    try:
        seasons = get_tmdb_seasons(tmdb_id, lang=lang_code)
    except Exception:
        return "TMDB Error"
    skip_dict = {}
    for entry in skip_db:
        if entry['episodeId'].startswith(show_id + ":"):
            titre = entry.get('title', '')
            match = re.search(r'[Ss](\d+)[Ee](\d+)', titre)
            if match:
                season = int(match.group(1))
                ep_num = int(match.group(2))
            else:
                match = re.search(r'(\d+)x(\d+)', titre)
                if match:
                    season = int(match.group(1))
                    ep_num = int(match.group(2))
                else:
                    season = 1
                    try:
                        ep_num = int(entry['episodeId'].split(":")[1])
                    except Exception:
                        continue
            skip_dict[(season, ep_num)] = (entry.get('start'), entry.get('end'))
    skipped_eps = set(skip_dict.keys())
    seasons_detail = []
    episodes_cache = {}
    for season in seasons:
        if season["season_number"] == 0:
            continue
        season_key = (tmdb_id, season["season_number"], lang_code)
        if season_key in episodes_cache:
            eps = episodes_cache[season_key]
        else:
            try:
                eps = get_tmdb_episodes(tmdb_id, season["season_number"], lang=lang_code)
                episodes_cache[season_key] = eps
            except Exception:
                continue
        eps_detail = []
        for ep in eps:
            ep_num = ep["episode_number"]
            season_num = season["season_number"]
            has_skip = (season_num, ep_num) in skipped_eps
            timecodes = skip_dict.get((season_num, ep_num))
            eps_detail.append({
                "num": ep_num,
                "title": ep["name"],
                "has_skip": has_skip,
                "timecodes": timecodes
            })
        seasons_detail.append({
            "season_number": season["season_number"],
            "episodes": eps_detail
        })
    return render_template_string("""
    <style>
    .modal-bg {
      display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100vw; height: 100vh;
      background: rgba(0,0,0,0.4); align-items: center; justify-content: center;
    }
    .modal-content {
      background: #fff; padding: 2em; border-radius: 10px; min-width: 250px; min-height: 80px; box-shadow: 0 2px 16px #0004;
      position: relative;
    }
    .modal-close {
      position: absolute; top: 0.5em; right: 1em; cursor: pointer; font-size: 1.5em; color: #888;
    }
    </style>
    <div style="position:fixed;top:1em;right:2em;">
      <form method="get" id="langform">
        <input type="hidden" name="lang" value="{{ lang }}">
        <label>{{ t.language }} :
          <select name="lang" onchange="document.getElementById('langform').submit()">
            <option value="fr" {% if lang == 'fr' %}selected{% endif %}>Français</option>
            <option value="en" {% if lang == 'en' %}selected{% endif %}>English</option>
          </select>
        </label>
      </form>
    </div>
    <h1>{{ title }}</h1>
    <a href="{{ url_for('index', lang=lang) }}">← {{ t.back }}</a>
    {% for season in seasons %}
      <h2>{{ t.season }} {{ season.season_number }}</h2>
      <ul>
        {% for ep in season.episodes %}
          <li>
            {{ "✅" if ep.has_skip else "❌" }}
            {{ t.episode }} {{ ep.num }} : {{ ep.title }}
            {% if ep.has_skip %}
              <button onclick="showTimecodes('{{ season.season_number }}', '{{ ep.num }}', '{{ ep.timecodes[0] }}', '{{ ep.timecodes[1] }}')">
                {% if lang == 'fr' %}Afficher{% else %}Show{% endif %}
              </button>
            {% endif %}
          </li>
        {% endfor %}
      </ul>
    {% endfor %}
    <div id="modal-bg" class="modal-bg" onclick="hideModal()">
      <div class="modal-content" onclick="event.stopPropagation()">
        <span class="modal-close" onclick="hideModal()">&times;</span>
        <div id="modal-body"></div>
      </div>
    </div>
    <script>
    function showTimecodes(season, ep, start, end) {
      var lang = "{{ lang }}";
      var html = "";
      if (lang === "fr") {
        html = "<b>Saison</b> " + season + " <b>Épisode</b> " + ep + "<br><b>Début :</b> " + start + "s<br><b>Fin :</b> " + end + "s";
      } else {
        html = "<b>Season</b> " + season + " <b>Episode</b> " + ep + "<br><b>Start:</b> " + start + "s<br><b>End:</b> " + end + "s";
      }
      document.getElementById('modal-body').innerHTML = html;
      document.getElementById('modal-bg').style.display = "flex";
    }
    function hideModal() {
      document.getElementById('modal-bg').style.display = "none";
    }
    </script>
    """, title=title, seasons=seasons_detail, lang=lang, t=t)

if __name__ == "__main__":
    app.run(debug=True)