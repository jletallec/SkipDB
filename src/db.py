import requests

def download_skip_db_json(url="https://busy-jacinta-shugi-c2885b2e.koyeb.app/download-db"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error downloading database: {e}")
        return None

def get_skipped_episodes(skip_db, show_id):
    episodes = []
    for entry in skip_db:
        if entry['episodeId'].startswith(show_id + ":"):
            try:
                ep_num = int(entry['episodeId'].split(":")[1])
                episodes.append((ep_num, entry['start'], entry['end']))
            except Exception:
                continue
    return sorted(episodes)

def get_show_title(skip_db, show_id):
    # Retourne le titre du premier épisode trouvé pour ce show_id
    for entry in skip_db:
        if entry['episodeId'].startswith(show_id + ":"):
            return entry.get('title', show_id)
    return show_id

def get_all_show_ids(skip_db):
    show_ids = set()
    for entry in skip_db:
        eid = entry['episodeId']
        if eid.startswith("tmdb:"):
            # Prend tmdb:xxxx comme show_id
            parts = eid.split(":")
            if len(parts) >= 2:
                show_ids.add(f"tmdb:{parts[1]}")
        else:
            show_ids.add(eid.split(":")[0])
    return list(show_ids)