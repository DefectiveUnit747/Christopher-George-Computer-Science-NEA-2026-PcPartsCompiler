import unittest
import logging
import time
from unittest.mock import patch
from pcBuildListCompiler.createBuildList import (
    PcBuildCompiler, CPU, GPU, Motherboard, RAM, PSU, Case, Storage
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


class TestBuildCompilationIntegration(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def tearDown(self):
        logger.info(f"Torn down {self._testMethodName}")

    def _makeValidParts(self):
        return {
            "gpu": [("GPU-001", GPU({
                "partNumber": "GPU-001", "name": "RTX 4070", "price": 399,
                "finalScore": 690, "tdpWatts": 200, "lengthMm": 300,
                "url": "", "imagePath": "", "manufacturerName": "Nvidia"
            }))],
            "cpu": [("CPU-001", CPU({
                "partNumber": "CPU-001", "name": "Ryzen 7", "price": 200,
                "finalScore": 625, "tdpWatts": 120, "socketId": "AM5",
                "url": "", "imagePath": ""
            }))],
            "motherboard": [("MB-001", Motherboard({
                "partNumber": "MB-001", "name": "ASUS X670", "price": 150,
                "finalScore": 615, "tdpWatts": 15, "socketId": "AM5",
                "formFactor": "ATX", "memorySlots": 4, "memoryType": "DDR5",
                "maxMemory": 128, "url": "", "imagePath": ""
            }))],
            "ram": [("RAM-001", RAM({
                "partNumber": "RAM-001", "name": "Corsair 32GB", "price": 89,
                "finalScore": 590, "ddrType": "DDR5", "numberOfModules": 2,
                "capacityGb": 32, "url": "", "imagePath": ""
            }))],
            "storage": [("SSD-001", Storage({
                "partNumber": "SSD-001", "name": "Samsung 980 Pro", "price": 79,
                "finalScore": 580, "capacityGb": 1000,
                "url": "", "imagePath": ""
            }))],
            "psu": [("PSU-001", PSU({
                "partNumber": "PSU-001", "name": "Corsair RM850x", "price": 89,
                "finalScore": 575, "wattage": 850,
                "url": "", "imagePath": ""
            }))],
            "case": [("CASE-001", Case({
                "partNumber": "CASE-001", "name": "NZXT H510", "price": 69,
                "finalScore": 515, "gpuMaxLength": 380, "formFactorSupport": "ATX",
                "url": "", "imagePath": ""
            }))]
        }

    def _loadValidParts(self, compiler, parts):
        compiler.validParts = parts

    def testFullBuildGenerationCompletesSuccessfully(self):
        compiler = PcBuildCompiler(budget=1400, gpuPreference="None",
                                   aestheticsWeight=2, futureWeight=4, tier="medium")
        parts = self._makeValidParts()

        def loadParts(dbPath=None):
            self._loadValidParts(compiler, parts)

        with patch.object(compiler, "loadValidParts", loadParts):
            bestBuild, bestScore, bestPrice = compiler.findBestBuild()
            logger.info(f"Build found: {bestBuild is not None}, score={bestScore}, price={bestPrice}")
            self.assertIsNotNone(bestBuild)
            self.assertGreater(bestScore, 0)
            self.assertLessEqual(bestPrice, 1400)

    def testNoBuildFoundWhenBudgetTooLow(self):
        compiler = PcBuildCompiler(budget=50, gpuPreference="None",
                                   aestheticsWeight=2, futureWeight=4, tier="medium")
        parts = self._makeValidParts()

        def loadParts(dbPath=None):
            self._loadValidParts(compiler, parts)

        with patch.object(compiler, "loadValidParts", loadParts):
            bestBuild, bestScore, bestPrice = compiler.findBestBuild()
            logger.info(f"bestBuild={bestBuild}, bestScore={bestScore}")
            self.assertIsNone(bestBuild)
            self.assertEqual(bestScore, 0)

    def testGpuBrandFilteringWorksCorrectly(self):
        parts = self._makeValidParts()
        parts["gpu"].append(("GPU-002", GPU({
            "partNumber": "GPU-002", "name": "RX 7900", "price": 549,
            "finalScore": 680, "tdpWatts": 250, "lengthMm": 320,
            "url": "", "imagePath": "", "manufacturerName": "AMD"
        })))

        def loadNvidiaOnly(dbPath=None):
            filteredParts = dict(parts)
            filteredParts["gpu"] = [(pn, part) for pn, part in parts["gpu"]
                                    if part.data.get("manufacturerName") == "Nvidia"]
            compiler.validParts = filteredParts

        compiler = PcBuildCompiler(budget=1400, gpuPreference="Nvidia",
                                   aestheticsWeight=2, futureWeight=4, tier="medium")
        with patch.object(compiler, "loadValidParts", loadNvidiaOnly):
            bestBuild, bestScore, bestPrice = compiler.findBestBuild()
            logger.info(f"GPU in build: {bestBuild['gpu'].data['manufacturerName'] if bestBuild else None}")
            self.assertIsNotNone(bestBuild)
            self.assertEqual(bestBuild["gpu"].data["manufacturerName"], "Nvidia")

    def testBuildCompletesWithinTimeLimit(self):
        parts = self._makeValidParts()
        for i in range(9):
            parts["gpu"].append((f"GPU-{i + 10}", GPU({
                "partNumber": f"GPU-{i + 10}", "name": f"GPU Extra {i}",
                "price": 500 + i * 10, "finalScore": 600 + i,
                "tdpWatts": 200, "lengthMm": 300,
                "url": "", "imagePath": "", "manufacturerName": "Nvidia"
            })))
            parts["cpu"].append((f"CPU-{i + 10}", CPU({
                "partNumber": f"CPU-{i + 10}", "name": f"CPU Extra {i}",
                "price": 200 + i * 10, "finalScore": 500 + i,
                "tdpWatts": 120, "socketId": "AM5",
                "url": "", "imagePath": ""
            })))
            parts["ram"].append((f"RAM-{i + 10}", RAM({
                "partNumber": f"RAM-{i + 10}", "name": f"RAM Extra {i}",
                "price": 50 + i * 5, "finalScore": 400 + i,
                "ddrType": "DDR5", "numberOfModules": 2,
                "capacityGb": 32, "url": "", "imagePath": ""
            })))
            parts["motherboard"].append((f"MB-{i + 10}", Motherboard({
                "partNumber": f"MB-{i + 10}", "name": f"MB Extra {i}",
                "price": 100 + i * 10, "finalScore": 450 + i,
                "tdpWatts": 15, "socketId": "AM5",
                "formFactor": "ATX", "memorySlots": 4, "memoryType": "DDR5",
                "maxMemory": 128, "url": "", "imagePath": ""
            })))
        compiler = PcBuildCompiler(budget=1400, gpuPreference="None",
                                   aestheticsWeight=2, futureWeight=4, tier="medium")

        def loadParts(dbPath=None):
            self._loadValidParts(compiler, parts)

        with patch.object(compiler, "loadValidParts", loadParts):
            start = time.time()
            bestBuild, bestScore, bestPrice = compiler.findBestBuild()
            elapsed = time.time() - start
            logger.info(f"Build completed in {elapsed:.10f}s")
            self.assertLess(elapsed, 10)

if __name__ == "__main__":
    unittest.main()