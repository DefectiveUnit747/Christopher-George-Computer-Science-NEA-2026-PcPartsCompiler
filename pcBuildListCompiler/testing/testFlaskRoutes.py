import unittest
import logging
from unittest.mock import patch, MagicMock
import requests
from pcBuildListCompiler.app import app

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

class TestFlaskRoutes(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        logger.info(f"Torn down {self._testMethodName}")

    def testSearchForGameUnder3CharsReturnsEmptyList(self):
        response = self.client.get("/searchForGame?q=cy")
        logger.info(f"Status: {response.status_code}, Data: {response.get_json()}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def testSearchForGameExactly3CharsReturnsResults(self):
        with patch("pcBuildListCompiler.app.requests.get") as mockGet:
            mockGet.return_value.status_code = 200
            mockGet.return_value.json.return_value = {
                "results": [
                    {"name": "Cyberpunk 2077", "background_image": "http://img.com",
                     "platforms": [{"platform": {"name": "PC"}}]}
                ]
            }
            response = self.client.get("/searchForGame?q=Cyb")
            data = response.get_json()
            logger.info(f"Status: {response.status_code}, Results count: {len(data)}")
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(data), 0)

    def testSearchForGameReturnsPcOnlyResults(self):
        response = self.client.get("/searchForGame?q=Cyberpunk")
        data = response.get_json()
        logger.info(f"Status: {response.status_code}, Results: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)

    def testSearchForGameHandlesRawgTimeout(self):
        with patch("pcBuildListCompiler.app.requests.get") as mockGet:
            mockGet.side_effect = requests.exceptions.Timeout
            response = self.client.get("/searchForGame?q=Cyberpunk")
            data = response.get_json()
            logger.info(f"Status: {response.status_code}, Data: {data}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data, [])

    def testGenerateBuildReturns404WhenNoBuildFound(self):
        with patch("pcBuildListCompiler.app.PcBuildCompiler") as mockCompiler:
            mockCompiler.return_value.findBestBuild.return_value = (None, 0, 0)
            with self.client.session_transaction() as sess:
                sess["buildPreferences"] = {
                    "budget": 50, "gpuPreference": "any",
                    "efficiency": 2, "futurePref": 4
                }
                sess["gameData"] = {"tier": "medium"}
            response = self.client.post("/generateBuild")
            logger.info(f"Status: {response.status_code}")
            self.assertEqual(response.status_code, 404)

    def testGenerateBuildReturns200WithValidBuild(self):
        with patch("pcBuildListCompiler.app.PcBuildCompiler") as mockCompiler:
            mockBuild = {
                "gpu": MagicMock(data={"name": "RTX 4070", "price": 599.99}),
                "cpu": MagicMock(data={"name": "Ryzen 7", "price": 399.99}),
            }
            mockCompiler.return_value.findBestBuild.return_value = (mockBuild, 85, 1800)
            with self.client.session_transaction() as sess:
                sess["buildPreferences"] = {
                    "budget": 2000, "gpuPreference": "any",
                    "efficiency": 2, "futurePref": 4
                }
                sess["gameData"] = {"tier": "medium"}
            response = self.client.post("/generateBuild")
            logger.info(f"Status: {response.status_code}")
            self.assertEqual(response.status_code, 200)

    def testCheckMaintenanceReturns503WhenModeTrue(self):
        with patch("pcBuildListCompiler.app.maintenanceMode", True):
            response = self.client.get("/")
            logger.info(f"Status: {response.status_code}")
            self.assertEqual(response.status_code, 503)

    def testCheckMaintenanceAllowsThroughWhenModeFalse(self):
        with patch("pcBuildListCompiler.app.maintenanceMode", False):
            response = self.client.get("/")
            logger.info(f"Status: {response.status_code}")
            self.assertEqual(response.status_code, 302)

    def testSaveValuesStoresPreferencesCorrectly(self):
        response = self.client.post("/saveValues", json={
            "budget": 2000,
            "efficiency": 3,
            "futurePref": 4,
            "gpuPreference": "nvidia"
        })
        data = response.get_json()
        logger.info(f"Status: {response.status_code}, Preferences returned: {data}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["budget"], 2000)
        self.assertEqual(data["efficiency"], 3)
        self.assertEqual(data["gpuPreference"], "nvidia")

    def testSaveGameStoresGameDataCorrectly(self):
        with patch("pcBuildListCompiler.app.saveGamePreference") as mockSave:
            mockSave.return_value = {"tier": "high", "game": "Cyberpunk 2077"}
            response = self.client.post("/saveGame", json={
                "name": "Cyberpunk 2077"
            })
            data = response.get_json()
            logger.info(f"Status: {response.status_code}, Data: {data}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["tier"], "high")

    def testSaveGamePreferenceLowTierOldGame(self):
        with patch("pcBuildListCompiler.savedPreferences.requests.get") as mockGet:
            mockGet.return_value.status_code = 200
            mockGet.return_value.json.side_effect = [
                {"results": [{"slug": "old-game"}]},
                {
                    "released": "2010-01-01",
                    "platforms": [{"platform": {"name": "PlayStation 2"}}],
                    "genres": [{"name": "action"}],
                    "tags": []
                }
            ]
            from pcBuildListCompiler.savedPreferences import saveGamePreference
            result = saveGamePreference("Old Game")
            logger.info(f"Tier returned: {result['tier']}")
            self.assertEqual(result["tier"], "low")

    def testSaveGamePreferenceHighTierOpenWorld(self):
        with patch("pcBuildListCompiler.savedPreferences.requests.get") as mockGet:
            mockGet.return_value.status_code = 200
            mockGet.return_value.json.side_effect = [
                {"results": [{"slug": "open-world-game"}]},
                {
                    "released": "2020-01-01",
                    "platforms": [{"platform": {"name": "PC"}}],
                    "genres": [{"name": "open world"}],
                    "tags": []
                }
            ]
            from pcBuildListCompiler.savedPreferences import saveGamePreference
            result = saveGamePreference("Open World Game")
            logger.info(f"Tier returned: {result['tier']}")
            self.assertEqual(result["tier"], "high")

    def testSaveGamePreferenceMediumTierMidRangeGame(self):
        with patch("pcBuildListCompiler.savedPreferences.requests.get") as mockGet:
            mockGet.return_value.status_code = 200
            mockGet.return_value.json.side_effect = [
                {"results": [{"slug": "mid-game"}]},
                {
                    "released": "2016-01-01",
                    "platforms": [{"platform": {"name": "PC"}}],
                    "genres": [{"name": "action"}],
                    "tags": []
                }
            ]
            from pcBuildListCompiler.savedPreferences import saveGamePreference
            result = saveGamePreference("Mid Game")
            logger.info(f"Tier returned: {result['tier']}")
            self.assertEqual(result["tier"], "medium")

if __name__ == "__main__":
    unittest.main()