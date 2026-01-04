from flask import Flask, render_template, redirect, jsonify, request
from savedPreferences import *
from savedPreferences import extractPreferences, saveGamePreference
from storage import Storage
import requests
from createBuildList import PcBuildCompiler
import time

app = Flask(__name__)
app.secret_key = "SuperSecretKeyTEMPORARY"
RAWG_API_KEY = "a8008f8d0c084fe6a24273dc4fe4ba3e"
url = "https://api.rawg.io/api"
getRequirementsUrl = "https://api.rawg.io/api/games"

@app.route('/')
def index():
    return redirect("/homePage")

@app.route("/homePage")
def homePage():
    return render_template("homePage.html")

@app.route("/homePage/mainContent")
def mainContent():
    return render_template("mainContent.html")

@app.route("/searchForGame", methods=["GET"])
def searchForGame():
    query = request.args.get("q", "")
    if not query or len(query) < 3:
        return jsonify([])

    url = f"https://api.rawg.io/api/games?key={RAWG_API_KEY}&search={query}"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify([])

    results = response.json().get("results", [])[:10]

    games = []
    for game in results:
        platforms = [p["platform"]["name"].lower() for p in game.get("platforms", [])]
        if not any("pc" in p for p in platforms):
            continue

        games.append({
            "name": game["name"],
            "background_image": game.get("background_image")
        })

    return jsonify(games[:5])

@app.route("/saveGame", methods=["POST"])
def saveGame():
    try:
        data = request.get_json()
        gameName = data.get("name")
        gameData = saveGamePreference(gameName)

        Storage.gameData = gameData
        return jsonify(gameData), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/saveValues", methods=["POST"])
def saveValues():
    try:
        data = request.get_json()
        preferences = extractPreferences(data)
        Storage.buildPreferences = preferences
        print(f"Saved preferences: {preferences}")
        return jsonify(preferences), 200
    except Exception as e:
        print(f"Error saving values: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/homePage/mainContent/results")
def resultsPage():
    return render_template("results.html")

@app.route("/generateBuild", methods=["POST"])
def generateBuild():
    try:
        print("=== STARTING BUILD GENERATION ===")

        # Load preferences
        budget = int(Storage.buildPreferences.get("budget", 1400))
        gpuPreference = Storage.buildPreferences.get("gpuPreference", "any")
        aestheticsWeightage = int(Storage.buildPreferences.get("aesthetics", 2))
        futureWeight = int(Storage.buildPreferences.get("futurePref", 4))
        tier = Storage.gameData.get("tier", "medium")

        gpuMapping = {
            "any": "None",
            "nvidia": "Nvidia",
            "amd": "AMD",
            "intel": "Intel"
        }
        gpuPreference = gpuMapping.get(gpuPreference.lower(), "None")

        print(f"Budget: £{budget}, GPU: {gpuPreference}, Tier: {tier}")

        builder = PcBuildCompiler(
            budget=budget,
            gpu_preference=gpuPreference,
            aesthetics_weight=aestheticsWeightage,
            future_weight=futureWeight,
            tier=tier
        )

        print("✓ builder created")
        print("Loading parts...")

        bestBuild, bestScore, bestPrice = builder.find_best_build()

        if bestBuild:
            print(f" Build found. Score: {bestScore}, Price: £{bestPrice:.2f}")

            # Convert dict of objects into dict of dicts
            jsonBuild = {
                comp: part.data
                for comp, part in bestBuild.items()
            }

            return jsonify(jsonBuild), 200

        print("No valid build found")
        return jsonify({
            "error": "No valid build found within your budget and preferences."}), 404

    except Exception as e:
        print(f"EXCEPTION in generateBuild: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)