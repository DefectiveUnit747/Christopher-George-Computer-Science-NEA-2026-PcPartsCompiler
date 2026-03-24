import requests

RAWG_API_KEY = "a8008f8d0c084fe6a24273dc4fe4ba3e"
RAWG_SEARCH_URL = "https://api.rawg.io/api/games"

def extractPreferences(data):
    preferences = {
        "budget": int(data.get("budget", 1400)),
        "efficiency": int(data.get("efficiency", 2)),
        "futurePref": int(data.get("futurePref", 4)),
        "gpuPreference": data.get("gpuPreference", "any")
    }
    return preferences

def saveGamePreference(gameName):
    params = {"key": RAWG_API_KEY, "search": gameName, "page_size": 1}
    response = requests.get(RAWG_SEARCH_URL, params=params)
    data = response.json()

    if not data.get("results"):
        return None

    gameSlug = data["results"][0]["slug"]
    print(f"Found game slug: {gameSlug}")

    detailsUrl = f"https://api.rawg.io/api/games/{gameSlug}"
    detailsParams = {"key": RAWG_API_KEY}
    detailsResponse = requests.get(detailsUrl, params=detailsParams)

    if detailsResponse.status_code != 200:
        return None

    detailsData = detailsResponse.json()

    platforms = [p["platform"]["name"].lower() for p in detailsData.get("platforms", [])]
    genres = [g["name"].lower() for g in detailsData.get("genres", [])]
    tags = [t["name"].lower() for t in detailsData.get("tags", [])]

    released = detailsData.get("released", "2000")
    release_year = int(released[:4]) if released else 2000

    if not any("pc" in p for p in platforms):
        tier = "low"
    elif any("playstation 2" in p or "playstation 3" in p or "xbox 360" in p for p in platforms):
        tier = "low"
    elif release_year < 2014:
        tier = "low"
    elif "open world" in genres or "open world" in tags:
        tier = "high"
    elif 2014 <= release_year < 2020:
        tier = "medium"
    else:
        high_genres = {"shooter", "rpg", "open world", "action-adventure"}
        tier = "high" if set(genres) & high_genres else "medium"

    print("Tier:", tier)

    return {
        "game": gameName,
        "slug": gameSlug,
        "genres": genres,
        "tags": tags,
        "platforms": platforms,
        "release_year": release_year,
        "tier": tier
    }

def determinePerformanceTier(genres):

    high = {"action", "shooter", "rpg", "adventure", "open world", "racing"}
    mid = {"strategy", "sports", "survival", "platformer", "simulation"}
    low = {"puzzle", "casual", "indie", "2d", "arcade"}

    genreSet = set(genres)

    if genreSet & high:
        return "high"
    elif genreSet & mid:
        return "medium"
    else:
        return "low"
