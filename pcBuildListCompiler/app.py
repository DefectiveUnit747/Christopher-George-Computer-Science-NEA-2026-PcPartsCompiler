from flask import Flask, render_template, redirect, jsonify, request
from pcBuildListCompiler.savedPreferences import *
from pcBuildListCompiler.savedPreferences import extractPreferences, saveGamePreference
from pcBuildListCompiler.createBuildList import PcBuildCompiler
import requests
from flask_apscheduler import APScheduler
from flask import Flask, render_template, redirect, jsonify, request, session

app = Flask(__name__)
app.secret_key = "SuperSecretKeyTEMPORARY"
RAWG_API_KEY = "a8008f8d0c084fe6a24273dc4fe4ba3e"
url = "https://api.rawg.io/api"
getRequirementsUrl = "https://api.rawg.io/api/games"
maintenanceMode = False

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Europe/London"

@app.before_request
def checkMaintenance():
    if maintenanceMode and request.endpoint not in ["maintenancePage", "static"]:
        return render_template("maintenance.html"), 503

@app.route("/maintenance")
def maintenancePage():
    return render_template("maintenance.html"), 503

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

    try:
        response = requests.get(url, timeout=6)
    except requests.exceptions.Timeout:
        return jsonify([])

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

        session["gameData"] = gameData
        return jsonify(gameData), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/saveValues", methods=["POST"])
def saveValues():
    try:
        data = request.get_json()
        preferences = extractPreferences(data)
        session["buildPreferences"] = preferences
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

        # Load preferences
        budget = int(session.get("buildPreferences", {}).get("budget", 1400))
        gpuPreference = session.get("buildPreferences", {}).get("gpuPreference", "any")
        efficiencyWeightage = int(session.get("buildPreferences", {}).get("efficiency", 2))
        futureWeight = int(session.get("buildPreferences", {}).get("futurePref", 4))
        tier = session.get("gameData", {}).get("tier", "medium")

        gpuMapping = {
            "any": "None",
            "nvidia": "Nvidia",
            "amd": "AMD",
            "intel": "Intel"
        }
        gpuPreference = gpuMapping.get(gpuPreference.lower(), "None")

        print(f"Budget: £{budget}, GPU: {gpuPreference}, Tier: {tier}")

        builder = PcBuildCompiler(
            budget = budget,
            gpuPreference = gpuPreference,
            efficiencyWeight = efficiencyWeightage,
            futureWeight = futureWeight,
            tier = tier
        )

        bestBuild, bestScore, bestPrice = builder.findBestBuild()

        if bestBuild:
            print(f"Build found. Score: {bestScore}, Price: £{bestPrice:.2f}")

            # Convert dict of objects into dict of dicts
            jsonBuild = {
                comp: part.data
                for comp, part in bestBuild.items()
            }

            return jsonify(jsonBuild), 200

        print("✗ No valid build found")
        return jsonify({
            "error": "No valid build found within your budget and preferences."
        }), 404

    except Exception as e:
        print(f"EXCEPTION in generateBuild: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# @scheduler.task("cron", id="weekly_scrape", week="*", day_of_week="sun", hour=2, minute=0)
def scheduledScrape():
    """Run scraper every Sunday at 2 AM - CURRENTLY DISABLED"""
    global maintenanceMode
    try:
        maintenanceMode = True
        print("Maintenance mode ENABLED - Site is down")

        from scrapingTools.scrapeComponents import scraper, computerParts

        # Drop and recreate tables
        computerParts.createDatabaseTables()

        # Run the scraper
        scraper.scrapeAllComponents()

        print("Scheduled scrape completed successfully")

    except Exception as e:
        print(f"Scheduled scrape failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        maintenanceMode = False
        print("Maintenance mode DISABLED - Site is back up")

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)