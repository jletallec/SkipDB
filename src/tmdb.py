import requests
import os

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY environment variable not set")

def get_tmdb_show_id(imdb_id):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    if data.get("tv_results"):
        return data["tv_results"][0]["id"]
    return None

def get_tmdb_seasons(tmdb_id, lang="en-US"):
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={TMDB_API_KEY}&language={lang}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return data.get("seasons", [])

def get_tmdb_episodes(tmdb_id, season_number, lang="en-US"):
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_number}?api_key={TMDB_API_KEY}&language={lang}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return data.get("episodes", [])

def get_show_title_tmdb(tmdb_id, lang="en-US"):
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={TMDB_API_KEY}&language={lang}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return data.get("name", "")

def show_id_to_tmdb_id(show_id):
    if show_id.startswith("tmdb:"):
        try:
            return int(show_id.split(":")[1])
        except Exception:
            return None
    elif show_id.startswith("tt"):
        return get_tmdb_show_id(show_id)
    else:
        try:
            return int(show_id)
        except Exception:
            return None