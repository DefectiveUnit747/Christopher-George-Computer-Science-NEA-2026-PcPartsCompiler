import unittest
import logging
from pcBuildListCompiler.scrapingTools.dataNormalisationFunctions import (
    normaliseCpuScrapedValues, normaliseGpuScrapedValues,
    normaliseMotherboardScrapedValues, normaliseRamScrapedValues,
    normaliseStorageScrapedValues, normalisePsuScrapedValues,
    normaliseCaseScrapedValues, normaliseEfficiencyRating,
    normaliseReadWriteOrRpm
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


class TestNormalisation(unittest.TestCase):

    def testNormaliseCpu(self):
        logger.info("Running testNormaliseCpu")
        specs = {
            "coreCount": "8 cores",
            "coreClock": "4.5 GHz",
            "cache": "32 MB",
            "threads": "16",
            "tdp": "105 W",
            "socket": "AM5"
        }
        r = normaliseCpuScrapedValues(specs, "Ryzen 7", 3, "CPU1", 300, "url", 50)
        logger.info(f"CPU normalised: {r}")
        self.assertEqual(r["coreCount"], 8)
        self.assertEqual(r["coreClock"], 4.5)
        self.assertEqual(r["cache"], 32)
        self.assertEqual(r["threads"], 16)
        self.assertEqual(r["tdpWatts"], 105)

    def testNormaliseGpu(self):
        logger.info("Running testNormaliseGpu")
        specs = {
            "memoryGb": "16 GB",
            "coreClock": "Base 1500 MHz",
            "memoryType": "GDDR6X",
            "tdpWatts": "320 W",
            "length": "300 mm"
        }
        r = normaliseGpuScrapedValues(specs, "RTX 4080", 40, "GPU1", 1200, "url", 80)
        logger.info(f"GPU normalised: {r}")
        self.assertEqual(r["memoryGb"], 16)
        self.assertEqual(r["coreClock"], 1500)
        self.assertEqual(r["memoryType"], "GDDR6X")
        self.assertEqual(r["tdpWatts"], 320)
        self.assertEqual(r["lengthMm"], 300.0)

    def testNormaliseMotherboard(self):
        logger.info("Running testNormaliseMotherboard")
        specs = {
            "socket": "AM5",
            "formFactor": "ATX",
            "tdp": "15 W",
            "memorySlots": "4 slots",
            "memoryType": "DDR5",
            "maxMemory": "128 GB"
        }
        r = normaliseMotherboardScrapedValues(specs, "ASUS X670", 6, "MB1", 250, "url", 60)
        logger.info(f"Motherboard normalised: {r}")
        self.assertEqual(r["socketId"], "AM5")
        self.assertEqual(r["formFactor"], "ATX")
        self.assertEqual(r["memorySlots"], 4)
        self.assertEqual(r["memoryType"], "DDR5")
        self.assertEqual(r["maxMemory"], 128)

    def testNormaliseRam(self):
        logger.info("Running testNormaliseRam")
        specs = {
            "capacityGb": "32 GB",
            "numberOfModules": "2",
            "speedMhz": "6000",
            "ddrType": "DDR5"
        }
        r = normaliseRamScrapedValues(specs, "Corsair 32GB", 24, "RAM1", 120, "url", 40)
        logger.info(f"RAM normalised: {r}")
        self.assertEqual(r["capacityGb"], 32)
        self.assertEqual(r["numberOfModules"], 2)
        self.assertEqual(r["speedMhz"], 6000)

    def testNormaliseStorage(self):
        logger.info("Running testNormaliseStorage")
        specs = {
            "capacityGb": "1 TB",
            "readSpeed": "7000 MB/s",
            "writeSpeed": "5000 MB/s",
            "formFactor": "M.2"
        }
        r = normaliseStorageScrapedValues(specs, "Samsung 980 Pro", 45, "ST1", 150, "url", 70)
        logger.info(f"Storage normalised: {r}")
        self.assertEqual(r["capacityGb"], 1000)
        self.assertEqual(r["readSpeed"], 7000)
        self.assertEqual(r["writeSpeed"], 5000)

    def testNormaliseStorageRpm(self):
        logger.info("Running testNormaliseStorageRpm")
        r = normaliseReadWriteOrRpm("7200 RPM")
        logger.info(f"RPM normalised: {r}")
        self.assertAlmostEqual(r, 7200 * 0.025)

    def testNormalisePsu(self):
        logger.info("Running testNormalisePsu")
        specs = {
            "wattage": "850 W",
            "efficiencyRating": "80 Plus Gold",
            "formFactor": "ATX",
            "modularity": "Modular"
        }
        r = normalisePsuScrapedValues(specs, "RM850x", 24, "PSU1", 140, "url", 55)
        logger.info(f"PSU normalised: {r}")
        self.assertEqual(r["wattage"], 850)
        self.assertEqual(r["efficiencyRating"], "gold")
        self.assertTrue(r["modular"])

    def testNormalisePsuNonModular(self):
        logger.info("Running testNormalisePsuNonModular")
        specs = {
            "wattage": "650 W",
            "efficiencyRating": "80 Plus Bronze",
            "formFactor": "ATX",
            "modularity": "Non-Modular"
        }
        r = normalisePsuScrapedValues(specs, "EVGA 650", 18, "PSU2", 80, "url", 30)
        logger.info(f"PSU normalised: {r}")
        self.assertFalse(r["modular"])

    def testNormaliseCase(self):
        logger.info("Running testNormaliseCase")
        specs = {
            "formFactorSupport": "ATX",
            "gpuMaxLength": "350 mm"
        }
        r = normaliseCaseScrapedValues(specs, "H510", 37, "CASE1", 90, "url", 20)
        logger.info(f"Case normalised: {r}")
        self.assertEqual(r["formFactorSupport"], "ATX")
        self.assertEqual(r["gpuMaxLength"], 350)

    def testEfficiencyGold(self):
        logger.info("Running testEfficiencyGold")
        self.assertEqual(normaliseEfficiencyRating("80 Plus Gold"), "gold")

    def testEfficiencyEta(self):
        logger.info("Running testEfficiencyEta")
        self.assertEqual(normaliseEfficiencyRating("ETA Silver"), "silver")

    def testEfficiencyInvalid(self):
        logger.info("Running testEfficiencyInvalid")
        self.assertEqual(normaliseEfficiencyRating("???"), "na")

    def testReadWriteMb(self):
        logger.info("Running testReadWriteMb")
        self.assertEqual(normaliseReadWriteOrRpm("3500 MB/s"), 3500)

    def testReadWriteRpm(self):
        logger.info("Running testReadWriteRpm")
        self.assertAlmostEqual(normaliseReadWriteOrRpm("5400rpm"), 5400 * 0.025)

if __name__ == "__main__":
    unittest.main()
