from flask import Flask, render_template, redirect, jsonify, request


from savedPreferences import *
from savedPreferences import extractPreferences, saveGamePreference
from storage import Storage
import requests
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
        import createBuildList
        print("✓ Module imported")

        # Get preferences from Storage
        budget = int(Storage.buildPreferences.get("budget", 1400))
        gpuPreference = Storage.buildPreferences.get("gpuPreference", "any")
        aestheticsWeightage = int(Storage.buildPreferences.get("aesthetics", 2))
        futureProofingWeightage = int(Storage.buildPreferences.get("futurePref", 4))
        tier = Storage.gameData.get("tier", "medium")
        print("✓ Preferences loaded")

        # Map GPU preference
        gpuMapping = {
            "any": "None",
            "nvidia": "Nvidia",
            "amd": "AMD",
            "intel": "Intel"
        }
        gpuPreference = gpuMapping.get(gpuPreference.lower(), "None")

        print(f"Budget: £{budget}, GPU: {gpuPreference}, Tier: {tier}")
        print("Calling getValidPartsFromDb...")

        # Load parts
        validPartsDict = createBuildList.getValidPartsFromDb(gpuPreference, tier, aestheticsWeightage, futureProofingWeightage)

        print("✓ getValidPartsFromDb returned")

        # Debug output
        print("\n=== PARTS AVAILABLE ===")
        total_parts = 0
        for component, parts in validPartsDict.items():
            part_count = len(parts)
            print(f"{component}: {part_count} parts")
            total_parts += part_count
            if part_count == 0:
                print(f"  ⚠️ WARNING: No {component} parts found!")

        print(f"TOTAL: {total_parts} parts across all components")
        print("=======================\n")

        if total_parts == 0:
            return jsonify({"error": "No parts available for this configuration"}), 404

        # Check missing components
        for component, parts in validPartsDict.items():
            if len(parts) == 0:
                return jsonify({
                    "error": f"No compatible {component} parts available for tier '{tier}' with GPU preference '{gpuPreference}'"
                }), 404

        print("Starting depth-first search...")

        # Reset globals
        createBuildList.bestBuild = None
        createBuildList.bestScore = 0
        createBuildList.bestPrice = 0
        startTime = time.time()
        createBuildList.depthFirstSearch(
            0, {}, 0, 0, budget, validPartsDict
        )

        print("Search complete!")
        print("--- %s seconds ---" % (time.time() - startTime))
        if createBuildList.bestBuild:
            print(f"✓ Build found! Score: {createBuildList.bestScore}, Price: £{createBuildList.bestPrice:.2f}")
            return jsonify(createBuildList.bestBuild), 200
        else:
            print("✗ No valid build found")
            return jsonify({
                "error": "No valid build found within your budget and preferences. Try increasing budget or lowering tier."
            }), 404

    except Exception as e:
        print(f"EXCEPTION in generateBuild: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)