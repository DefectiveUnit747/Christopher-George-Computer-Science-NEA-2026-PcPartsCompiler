from flask import Flask, render_template, redirect, jsonify, request
import requests
import sqlite3
from savedPreferences import *
from pcBuildListCompiler.savedPreferences import extractPreferences, saveGamePreference
from storage import Storage

app = Flask(__name__)
app.secret_key = "SuperSecretKeyTEMPORARY"
RAWG_API_KEY = "a8008f8d0c084fe6a24273dc4fe4ba3e"
url = "https://api.rawg.io/api"
getRequirementsUrl = "https://api.rawg.io/api/games"

@app.route('/')
def index():
    return redirect("/homePage") #Routes to homepage as default

@app.route("/homePage")
def homePage():
    return render_template("homePage.html") #routes to the homepage

@app.route("/homePage/mainContent")
def mainContent():
    return render_template("mainContent.html") #Routes to the main content page

@app.route("/searchForGame", methods=["GET"]) #Handles get requests
def searchForGame():
    query = request.args.get("q", "") #When typing in the search bar, extracts the actual text typed from the query string
    if not query or len(query) < 3: #Only shows results when length >= 3, limiting API requests
        return jsonify([])
    url = f"https://api.rawg.io/api/games?key={"a8008f8d0c084fe6a24273dc4fe4ba3e"}&search={query}"
    response = requests.get(url)

    if response.status_code == 200: #checks is the https request from the api is successful
        results = response.json().get("results", [])[:8] #Gets the 10 most similar results, Only 5 displayed but this is to account for some ganes who's requirements/other details not stored on the api
        for result in results:
            if not saveGamePreference(result["name"], RAWG_API_KEY, getRequirementsUrl):
                results.remove(result)

        games = [{"name": game["name"], "background_image": game.get("background_image")} for game in results[:5]] #The names of all the games in the list
        print(games)
        return jsonify(games)

@app.route("/saveGame", methods=["POST"])
def saveGame():
    try:
        data = request.get_json()
        gameName = data.get("name")
        gameData = saveGamePreference(gameName,RAWG_API_KEY, url)

        Storage.gameData = gameData

        return jsonify(gameData), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/saveValues", methods=["POST"])
def saveValues():
    data = request.get_json()
    preferences = extractPreferences(data) #Function is in the extractPreferences python file
    Storage.buildPreferences = preferences
    return jsonify(preferences), 200

@app.route("/homePage/mainContent/results")
def resultsPage():
    return render_template("results.html")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug = True)


