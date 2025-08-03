def format_episode_title(title):
    if " S" in title:
        return title.split(" S")[0]
    return title

def extract_season_and_episode(episode_id):
    try:
        parts = episode_id.split(":")
        if len(parts) >= 2:
            return int(parts[1])
    except (ValueError, IndexError):
        return None

def handle_api_error(e):
    print(f"API Error: {e}")
    return None

def is_valid_tmdb_id(tmdb_id):
    return isinstance(tmdb_id, int) and tmdb_id > 0