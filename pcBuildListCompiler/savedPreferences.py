import requests

RAWG_API_KEY = "a8008f8d0c084fe6a24273dc4fe4ba3e"
url = "https://api.rawg.io/api"

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
        "search": gameName
    }

    response = requests.get(url,params=params)  # Makes an HTTP GET request to get the object of the game, status code, and headers (some metadata)
    if response.status_code != 200: #Error handling, makes sure that the status is 200 which indicates no errors
        return None, {"error": "Failed to fetch game list"}, 500

    results = response.json().get("results", []) #.json turns data into python dict, and pulls the list containing the game from it
    if not results:
        raise Exception("Game not Found")#Checks if the list is empty or not

    game = results[0]
    gameID = game["id"]

    infoParams = {
        "key": RAWG_API_KEY,
    }
    detail_res = requests.get(url, params = infoParams) #Fetches the detailed information for the game
    if detail_res.status_code != 200: #Error Handling
        raise Exception("error", "Failed to fetch detailed info")

    detail_data = detail_res.json() #converts from JSON to python dictionary
    requirements = {}
    for platform in detail_data.get("platforms", []): #Gets the requirements into a list
        if platform.get("requirements"):
            requirements = platform["requirements"]
            break

    gameData = {
        "gameName": gameName,
        "gameID": gameID,
        "requirements": requirements,
    }
    return gameData
