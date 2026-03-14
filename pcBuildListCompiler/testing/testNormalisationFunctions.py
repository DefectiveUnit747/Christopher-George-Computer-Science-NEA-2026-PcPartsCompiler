import unittest
import logging
from pcBuildListCompiler.scrapingTools.dataNormalisationFunctions import (
    featureScaling, tanhSigmoidScaling, exponentialDecay,
    assignCpuScore, assignGpuScore, assignRamScore,
    normaliseCpuScrapedValues, normaliseGpuScrapedValues,
    normaliseMotherboardScrapedValues, normaliseRamScrapedValues,
    normaliseStorageScrapedValues, normalisePsuScrapedValues,
    normaliseCaseScrapedValues, normaliseEfficiencyRating,
    normaliseReadWriteOrRpm
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


class TestFeatureScaling(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testValueBelowMinReturnsZero(self):
        result = featureScaling(5, 8, 150, 70)
        logger.info(f"Result: {result}")
        self.assertEqual(result, 0)

    def testValueAboveMaxReturnsMaxScore(self):
        result = featureScaling(200, 8, 150, 70)
        logger.info(f"Result: {result}")
        self.assertEqual(result, 70)

    def testMidrangeValueReturnsCorrectProportion(self):
        result = featureScaling(79, 8, 150, 70)
        logger.info(f"Result: {result}")
        self.assertAlmostEqual(result, 35.0, places=0)

    def testValueAtMinReturnsZero(self):
        result = featureScaling(8, 8, 150, 70)
        logger.info(f"Result: {result}")
        self.assertEqual(result, 0)

    def testValueAtMaxReturnsMaxScore(self):
        result = featureScaling(150, 8, 150, 70)
        logger.info(f"Result: {result}")
        self.assertEqual(result, 70)


class TestTanhSigmoidScaling(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testMidpointReturnsApproximatelyFifty(self):
        result = tanhSigmoidScaling(12, 12, 6)
        logger.info(f"Result: {result}")
        self.assertAlmostEqual(result, 50.0, places=1)

    def testExtremeHighApproaches100(self):
        result = tanhSigmoidScaling(100, 12, 6)
        logger.info(f"Result: {result}")
        self.assertGreater(result, 95)

    def testExtremeLowApproachesZero(self):
        result = tanhSigmoidScaling(-100, 12, 6)
        logger.info(f"Result: {result}")
        self.assertLess(result, 5)


class TestExponentialDecay(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testZeroInputReturnsOne(self):
        result = exponentialDecay(0, 0.003)
        logger.info(f"Result: {result}")
        self.assertAlmostEqual(result, 1.0, places=5)

    def testHigherInputReturnsLowerOutput(self):
        result1 = exponentialDecay(100, 0.003)
        result2 = exponentialDecay(200, 0.003)
        logger.info(f"decay(100)={result1}, decay(200)={result2}")
        self.assertGreater(result1, result2)

    def testOutputAlwaysBetweenZeroAndOne(self):
        result = exponentialDecay(10000, 0.003)
        logger.info(f"Result: {result}")
        self.assertGreater(result, 0)
        self.assertLessEqual(result, 1)


class TestAssignCpuScore(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "coreCount": 8, "coreClock": 4.2,
            "cache": 32, "tdpWatts": 105, "threads": 16
        }

    def testAllThreeScoresPresent(self):
        result = assignCpuScore(self.specs.copy())
        logger.info(f"Result: {result}")
        self.assertIn("score", result)
        self.assertIn("scoreEfficiency", result)
        self.assertIn("scoreUpgradeability", result)

    def testAllScoresInValidRange(self):
        result = assignCpuScore(self.specs.copy())
        logger.info(f"Scores: score={result['score']}, efficiency={result['scoreEfficiency']}, upgradeability={result['scoreUpgradeability']}")
        for key in ["score", "scoreEfficiency", "scoreUpgradeability"]:
            self.assertGreaterEqual(result[key], 0)
            self.assertLessEqual(result[key], 100)


class TestAssignGpuScore(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "memoryGb": 12, "coreClock": 2500,
            "memoryType": "GDDR6X", "tdpWatts": 200
        }

    def testAllThreeScoresPresent(self):
        result = assignGpuScore(self.specs.copy())
        logger.info(f"Result: {result}")
        self.assertIn("score", result)
        self.assertIn("scoreEfficiency", result)
        self.assertIn("scoreUpgradeability", result)

    def testAllScoresInValidRange(self):
        result = assignGpuScore(self.specs.copy())
        logger.info(f"Scores: score={result['score']}, efficiency={result['scoreEfficiency']}, upgradeability={result['scoreUpgradeability']}")
        for key in ["score", "scoreEfficiency", "scoreUpgradeability"]:
            self.assertGreaterEqual(result[key], 0)
            self.assertLessEqual(result[key], 100)


class TestAssignRamScore(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "capacityGb": 32, "speedMhz": 3200,
            "ddrType": "DDR4", "numberOfModules": 2
        }

    def testAllThreeScoresPresent(self):
        result = assignRamScore(self.specs.copy())
        logger.info(f"Result: {result}")
        self.assertIn("score", result)
        self.assertIn("scoreEfficiency", result)
        self.assertIn("scoreUpgradeability", result)

    def testAllScoresInValidRange(self):
        result = assignRamScore(self.specs.copy())
        logger.info(f"Scores: score={result['score']}, efficiency={result['scoreEfficiency']}, upgradeability={result['scoreUpgradeability']}")
        for key in ["score", "scoreEfficiency", "scoreUpgradeability"]:
            self.assertGreaterEqual(result[key], 0)
            self.assertLessEqual(result[key], 100)

class TestOutputClamping(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testScoreNotBelowZero(self):
        specs = {
            "coreCount": 0, "coreClock": 0.0,
            "cache": 0, "tdpWatts": 1, "threads": 0
        }
        result = assignCpuScore(specs.copy())
        logger.info(f"Score with minimal specs: {result['score']}")
        self.assertGreaterEqual(result["score"], 0)

    def testScoreNotAbove100(self):
        specs = {
            "coreCount": 9999, "coreClock": 9999.0,
            "cache": 9999, "tdpWatts": 1, "threads": 9999
        }
        result = assignCpuScore(specs.copy())
        logger.info(f"Score with extreme specs: {result['score']}")
        self.assertLessEqual(result["score"], 100)

class TestNormaliseCpuScrapedValues(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "coreCount": "8 Cores", "coreClock": "4.2 GHz",
            "cache": "32 MB", "threads": "16",
            "tdp": "105 W", "socket": "AM5"
        }

    def testCorrectValuesAndTypes(self):
        result = normaliseCpuScrapedValues(
            self.specs, "Test CPU", 1, "AMD-001", 299.99, "http://test.com", 0
        )
        logger.info(f"Result: coreCount={result['coreCount']}, coreClock={result['coreClock']}, socketId={result['socketId']}")
        self.assertEqual(result["coreCount"], 8)
        self.assertIsInstance(result["coreCount"], int)
        self.assertEqual(result["coreClock"], 4.2)
        self.assertIsInstance(result["coreClock"], float)
        self.assertEqual(result["tdpWatts"], 105)
        self.assertEqual(result["socketId"], "AM5")

    def testSingleCoreCpu(self):
        specs = {**self.specs, "coreCount": "1 Cores", "threads": "1"}
        result = normaliseCpuScrapedValues(
            specs, "Test CPU", 1, "AMD-001", 299.99, "http://test.com", 0
        )
        logger.info(f"Result: coreCount={result['coreCount']}, threads={result['threads']}")
        self.assertEqual(result["coreCount"], 1)
        self.assertEqual(result["threads"], 1)

    def testTdpAsList(self):
        specs = {**self.specs, "tdp": ["105 W", "extra"]}
        result = normaliseCpuScrapedValues(
            specs, "Test CPU", 1, "AMD-001", 299.99, "http://test.com", 0
        )
        logger.info(f"Result: tdpWatts={result['tdpWatts']}")
        self.assertEqual(result["tdpWatts"], 105)


class TestNormaliseGpuScrapedValues(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "memoryGb": "12 GB", "coreClock": "Base 2500 MHz",
            "memoryType": "GDDR6X", "tdpWatts": "200 W", "length": "336 mm"
        }

    def testCorrectValuesAndTypes(self):
        result = normaliseGpuScrapedValues(
            self.specs, "Test GPU", 1, "NV-001", 599.99, "http://test.com", 0
        )
        logger.info(f"Result: memoryGb={result['memoryGb']}, lengthMm={result['lengthMm']}, tdpWatts={result['tdpWatts']}")
        self.assertEqual(result["memoryGb"], 12)
        self.assertIsInstance(result["memoryGb"], float)
        self.assertEqual(result["lengthMm"], 336)
        self.assertEqual(result["tdpWatts"], 200)

    def testMinimumMemoryGpu(self):
        specs = {**self.specs, "memoryGb": "1 GB"}
        result = normaliseGpuScrapedValues(
            specs, "Test GPU", 1, "NV-001", 599.99, "http://test.com", 0
        )
        logger.info(f"Result: memoryGb={result['memoryGb']}")
        self.assertEqual(result["memoryGb"], 1)


class TestNormaliseMotherboardScrapedValues(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "socket": "AM5", "formFactor": "ATX",
            "memorySlots": "4 slots", "memoryType": "DDR5",
            "maxMemory": "128 GB", "tdp": "15 W"
        }

    def testCorrectTypes(self):
        result = normaliseMotherboardScrapedValues(
            self.specs, "Test MB", 1, "MB-001", 199.99, "http://test.com", 0
        )
        logger.info(f"Result: socketId={result['socketId']}, memorySlots={result['memorySlots']}, maxMemory={result['maxMemory']}")
        self.assertIsInstance(result["memorySlots"], int)
        self.assertIsInstance(result["maxMemory"], int)
        self.assertIsInstance(result["tdpWatts"], int)
        self.assertEqual(result["socketId"], "AM5")
        self.assertEqual(result["memorySlots"], 4)
        self.assertEqual(result["maxMemory"], 128)


class TestNormaliseRamScrapedValues(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "capacityGb": "32 GB", "speedMhz": "3200",
            "ddrType": "DDR4", "numberOfModules": "2"
        }

    def testCorrectValuesAndTypes(self):
        result = normaliseRamScrapedValues(
            self.specs, "Test RAM", 1, "RAM-001", 89.99, "http://test.com", 0
        )
        logger.info(f"Result: capacityGb={result['capacityGb']}, speedMhz={result['speedMhz']}, numberOfModules={result['numberOfModules']}")
        self.assertEqual(result["capacityGb"], 32)
        self.assertEqual(result["speedMhz"], 3200)
        self.assertEqual(result["numberOfModules"], 2)
        self.assertIsInstance(result["capacityGb"], int)

    def testSingleModuleRam(self):
        specs = {**self.specs, "numberOfModules": "1"}
        result = normaliseRamScrapedValues(
            specs, "Test RAM", 1, "RAM-001", 89.99, "http://test.com", 0
        )
        logger.info(f"Result: numberOfModules={result['numberOfModules']}")
        self.assertEqual(result["numberOfModules"], 1)


class TestNormaliseStorageScrapedValues(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "capacityGb": "1 TB",
            "readSpeed": "7000 MB/s",
            "writeSpeed": "6500 MB/s",
            "formFactor": "M.2"
        }

    def testTbConvertedToGb(self):
        result = normaliseStorageScrapedValues(
            self.specs, "Test SSD", 1, "SSD-001", 99.99, "http://test.com", 0
        )
        logger.info(f"Result: capacityGb={result['capacityGb']}")
        self.assertEqual(result["capacityGb"], 1000)

    def testGbStaysAsGb(self):
        specs = {**self.specs, "capacityGb": "500 GB"}
        result = normaliseStorageScrapedValues(
            specs, "Test SSD", 1, "SSD-001", 99.99, "http://test.com", 0
        )
        logger.info(f"Result: capacityGb={result['capacityGb']}")
        self.assertEqual(result["capacityGb"], 500)

    def testRpmHandled(self):
        specs = {
            "capacityGb": "2 TB",
            "readSpeed": "7200 RPM",
            "writeSpeed": "7200 RPM",
            "formFactor": "HDD"
        }
        result = normaliseStorageScrapedValues(
            specs, "Test HDD", 1, "HDD-001", 49.99, "http://test.com", 0
        )
        logger.info(f"Result: capacityGb={result['capacityGb']}, readSpeed={result['readSpeed']}")
        self.assertEqual(result["capacityGb"], 2000)
        self.assertIsInstance(result["readSpeed"], float)


class TestNormalisePsuScrapedValues(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "wattage": "850 W",
            "efficiencyRating": "80 Plus Gold",
            "formFactor": "ATX",
            "modularity": "Modular"
        }

    def testCorrectValuesAndTypes(self):
        result = normalisePsuScrapedValues(
            self.specs, "Test PSU", 1, "PSU-001", 109.99, "http://test.com", 0
        )
        logger.info(f"Result: wattage={result['wattage']}, efficiencyRating={result['efficiencyRating']}, modular={result['modular']}")
        self.assertEqual(result["wattage"], 850)
        self.assertEqual(result["efficiencyRating"], "gold")
        self.assertTrue(result["modular"])

    def testNonModular(self):
        specs = {**self.specs, "modularity": "Non-Modular"}
        result = normalisePsuScrapedValues(
            specs, "Test PSU", 1, "PSU-001", 109.99, "http://test.com", 0
        )
        logger.info(f"Result: modular={result['modular']}")
        self.assertFalse(result["modular"])

    def testMinimumWattage(self):
        specs = {**self.specs, "wattage": "1 W"}
        result = normalisePsuScrapedValues(
            specs, "Test PSU", 1, "PSU-001", 109.99, "http://test.com", 0
        )
        logger.info(f"Result: wattage={result['wattage']}")
        self.assertEqual(result["wattage"], 1)


class TestNormaliseCaseScrapedValues(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.specs = {
            "formFactorSupport": "ATX",
            "gpuMaxLength": "380 mm"
        }

    def testCorrectValuesAndTypes(self):
        result = normaliseCaseScrapedValues(
            self.specs, "Test Case", 1, "CASE-001", 79.99, "http://test.com", 0
        )
        logger.info(f"Result: formFactorSupport={result['formFactorSupport']}, gpuMaxLength={result['gpuMaxLength']}")
        self.assertEqual(result["formFactorSupport"], "ATX")
        self.assertEqual(result["gpuMaxLength"], 380)
        self.assertIsInstance(result["gpuMaxLength"], int)

    def testMinimumGpuLength(self):
        specs = {**self.specs, "gpuMaxLength": "1 mm"}
        result = normaliseCaseScrapedValues(
            specs, "Test Case", 1, "CASE-001", 79.99, "http://test.com", 0
        )
        logger.info(f"Result: gpuMaxLength={result['gpuMaxLength']}")
        self.assertEqual(result["gpuMaxLength"], 1)


class TestNormaliseEfficiencyRating(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def test80PlusGold(self):
        result = normaliseEfficiencyRating("80 Plus Gold")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "gold")

    def test80PlusPlatinum(self):
        result = normaliseEfficiencyRating("80 Plus Platinum")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "platinum")

    def test80PlusBronze(self):
        result = normaliseEfficiencyRating("80 Plus Bronze")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "bronze")

    def test80PlusSilver(self):
        result = normaliseEfficiencyRating("80 Plus Silver")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "silver")

    def testPlain80PlusReturnsNa(self):
        result = normaliseEfficiencyRating("80 Plus")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "na")

    def testEtaGold(self):
        result = normaliseEfficiencyRating("ETA Gold")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "gold")

    def testNoneReturnsNa(self):
        result = normaliseEfficiencyRating(None)
        logger.info(f"Result: {result}")
        self.assertEqual(result, "na")

    def testEmptyStringReturnsNa(self):
        result = normaliseEfficiencyRating("")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "na")

    def testUnknownReturnsNa(self):
        result = normaliseEfficiencyRating("unknown")
        logger.info(f"Result: {result}")
        self.assertEqual(result, "na")


class TestNormaliseReadWriteOrRpm(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testExtractsMbsValue(self):
        result = normaliseReadWriteOrRpm("7000 MB/s")
        logger.info(f"Result: {result}")
        self.assertEqual(result, 7000)

    def testZeroMbs(self):
        result = normaliseReadWriteOrRpm("0 MB/s")
        logger.info(f"Result: {result}")
        self.assertEqual(result, 0)

    def testRpmReturnsFloat(self):
        result = normaliseReadWriteOrRpm("7200 RPM")
        logger.info(f"Result: {result}")
        self.assertIsInstance(result, float)
        self.assertAlmostEqual(result, 180.0, places=1)

if __name__ == "__main__":
    unittest.main()