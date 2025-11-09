import urllib
import requests

RAWG_API_KEY = "a8008f8d0c084fe6a24273dc4fe4ba3e"
url = "https://api.rawg.io/api/games"

def extractPreferences(data):
    preferences = {
        "budget": data["budget"],
        "aesthetics": data["aesthetics"],
        "futurePref": data["futurePref"],
        "gpuPreference": data["gpuPreference"]
    }
    return preferences

def saveGamePreference(gameName, RAWG_API_KEY, url):
    params = {
        "key": RAWG_API_KEY, #Parameters for the key, and what to search for (the name)
        "search": gameName}

    response = requests.get(url, params=params)
    data = response.json()

    # Step 2: Get the slug of the first matching game
    if data['results']:
        game_slug = data['results'][0]['slug']
        print(f"Found game slug: {game_slug}")
    else:
        return None

    # Step 3: Get detailed info including requirements
    details_url = f'https://api.rawg.io/api/games/{game_slug}'
    details_params = {'key': RAWG_API_KEY}
    details_response = requests.get(details_url, params=details_params)
    details_data = details_response.json()

    # Step 4: Extract system requirements
    platforms = details_data.get('platforms', [])
    for platform in platforms:
        name = platform["platform"]["name"].lower()
        if name == "pc":
            requirements = platform.get('requirements', {})
            if requirements:
                recommendedRequirements = requirements.get('recommended', "N/A")
                return normaliseRequirements(recommendedRequirements)
    else:
        return None

def normaliseRequirements(requirements):
    normalisedRequirements = {}

    lineByLine = requirements.split("\n")
    for line in lineByLine:
        line = line.strip()
        if ":" not in line:
            continue

        if line.lower().startswith("processor"):
            normalisedRequirements["cpu"] = line.split(":", 1)[1].split(" or ")[0].strip()
        elif line.lower().startswith("memory") or line.lower().startswith("ram"):
            normalisedRequirements["memory"] = line.split(":", 1)[1].split(" or ")[0].strip()
        elif line.lower().startswith("graphics"):
            normalisedRequirements["graphics"] = line.split(":", 1)[1].split(" or ")[0].strip()
        elif line.lower().startswith("video"):
            normalisedRequirements["video"] = line.split(":", 1)[1].split(" or ")[0].strip()
        elif line.lower().startswith("storage") or line.lower().startswith("hard drive"):
            normalisedRequirements["storage"] = line.split(":", 1)[1].strip()

    return normalisedRequirements
