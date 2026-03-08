import unittest
from unittest.mock import patch, MagicMock, Mock
import time
import sys
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)

logger = logging.getLogger(__name__)

sys.modules['compatibilityFunctions'] = MagicMock(
    isCpuCompatibleWithMotherboard=Mock(return_value=True),
    isPsuCompatibleWithCpu=Mock(return_value=True),
    isGpuCompatibleWithCase=Mock(return_value=True),
    isPsuCompatibleWithGpu=Mock(return_value=True),
    isMotherboardCompatibleWithRam=Mock(return_value=True),
    isRamCapacityCompatibleWithMotherboard=Mock(return_value=True),
    isPsuCompatibleWithMotherboard=Mock(return_value=True),
    isMotherboardCompatibleWithCase=Mock(return_value=True)
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pcBuildListCompiler.createBuildList import (
    PcBuildCompiler, Component, CPU, GPU, Motherboard,
    RAM, PSU, Case, Storage, TIER_MAPPING, GPU_MAPPING
)


class TestLoadValidParts(unittest.TestCase):

    def setUp(self):
        logger.info("Initialising PcBuildCompiler")
        self.compiler = PcBuildCompiler(
            budget=1500,
            gpuPreference="None",
            aestheticsWeight=2,
            futureWeight=3,
            tier="medium"
        )

    @patch('pcBuildListCompiler.createBuildList.sqlite3.connect')
    def testFiltersByTierThreshold(self, mockConnect):
        logger.info("Running Test #1: Tier threshold filtering")
        mockConn = MagicMock()
        mockCursor = MagicMock()
        mockConnect.return_value = mockConn
        mockConn.cursor.return_value = mockCursor

        mockCursor.execute.return_value.fetchall.return_value = [{
            "partNumber": "CPU-HIGH", "name": "High CPU", "price": 300,
            "url": "url", "socketId": 1, "tdpWatts": 65, "imagePath": "path",
            "score": 60, "scoreEfficiency": 70, "scoreUpgradeability": 80
        }]

        self.compiler.loadValidParts()

        for call in mockCursor.execute.call_args_list:
            query = call[0][0]
            if "FROM cpu" in query:
                params = call[0][1]
                logger.info(f"CPU threshold param: {params[0]}")
                self.assertEqual(params[0], 30)
                return

    @patch('pcBuildListCompiler.createBuildList.sqlite3.connect')
    def testFiltersGpuByManufacturerPreference(self, mockConnect):
        logger.info("Running Test #2: GPU manufacturer filtering")

        compilerNvidia = PcBuildCompiler(
            budget=2000, gpuPreference="Nvidia",
            aestheticsWeight=2, futureWeight=3, tier="medium"
        )

        mockConn = MagicMock()
        mockCursor = MagicMock()
        mockConnect.return_value = mockConn
        mockConn.cursor.return_value = mockCursor
        mockCursor.execute.return_value.fetchall.return_value = []

        compilerNvidia.loadValidParts()

        for call in mockCursor.execute.call_args_list:
            query = call[0][0]
            if "FROM gpu" in query and "manufacturerId" in query:
                params = call[0][1]
                logger.info(f"GPU manufacturer param: {params[1]}")
                self.assertEqual(params[1], GPU_MAPPING["Nvidia"])
                return

        self.fail("GPU manufacturer filter not applied")


class TestScoreReformatting(unittest.TestCase):

    def testCalculatesWeightedFinalScore(self):
        logger.info("Running Test #3: Score reformatting")

        compiler = PcBuildCompiler(
            budget=1500, gpuPreference="None",
            aestheticsWeight=2, futureWeight=4, tier="medium"
        )

        inputDict = {
            "PART-001": {
                "name": "Test Part",
                "price": 100,
                "score": 50.0,
                "scoreEfficiency": 60.0,
                "scoreUpgradeability": 70.0
            }
        }

        result = compiler._reformatScores(inputDict)
        expected = 5 * 50.0 + 2 * 60.0 + 4 * 70.0

        logger.info(f"Expected finalScore: {expected}, Actual: {result['PART-001']['finalScore']}")
        self.assertEqual(result["PART-001"]["finalScore"], expected)


class TestMergeSortParts(unittest.TestCase):

    def testSortsByFinalScoreDescending(self):
        logger.info("Running Test #4: Merge sort")

        compiler = PcBuildCompiler(
            budget=1500, gpuPreference="None",
            aestheticsWeight=2, futureWeight=3, tier="medium"
        )

        parts = [
            ("PART-A", {"finalScore": 100}),
            ("PART-B", {"finalScore": 300}),
            ("PART-C", {"finalScore": 200}),
            ("PART-D", {"finalScore": 150})
        ]

        sortedParts = compiler._mergeSortParts(parts)
        logger.info(f"Sorted order: {[p[0] for p in sortedParts]}")
        self.assertEqual(sortedParts[0][0], "PART-B")


class TestParetoFilter(unittest.TestCase):

    def testRemovesDominatedParts(self):
        logger.info("Running Test #5: Pareto filtering")

        compiler = PcBuildCompiler(
            budget=1500, gpuPreference="None",
            aestheticsWeight=2, futureWeight=3, tier="medium"
        )

        parts = [
            ("PART-A", {"finalScore": 100, "price": 200}),
            ("PART-B", {"finalScore": 150, "price": 150}),
            ("PART-C", {"finalScore": 120, "price": 180}),
        ]

        filtered = compiler._paretoFilter(parts)
        logger.info(f"Remaining parts: {[p[0] for p in filtered]}")
        self.assertIn("PART-B", [p[0] for p in filtered])


class TestPruningHelpers(unittest.TestCase):

    def setUp(self):
        logger.info("Initialising pruning helper tests")
        self.compiler = PcBuildCompiler(
            budget=1500, gpuPreference="None",
            aestheticsWeight=2, futureWeight=3, tier="medium"
        )

        self.compiler.validParts = {
            "cpu": [
                ("CPU-1", CPU({"finalScore": 200, "price": 300})),
                ("CPU-2", CPU({"finalScore": 150, "price": 200}))
            ],
            "gpu": [
                ("GPU-1", GPU({"finalScore": 400, "price": 500})),
                ("GPU-2", GPU({"finalScore": 300, "price": 350}))
            ]
        }

    def testGetMaxScorePerComponent(self):
        logger.info("Running Test #7a: Max score")
        result = self.compiler._getMaxScorePerComponent(self.compiler.validParts["cpu"])
        logger.info(f"Max score: {result}")
        self.assertEqual(result, 200)

    def testGetMinPricePerComponent(self):
        logger.info("Running Test #7b: Min price")
        result = self.compiler._getMinPricePerComponent(self.compiler.validParts["gpu"])
        logger.info(f"Min price: {result}")
        self.assertEqual(result, 350)


class TestFullBuildGeneration(unittest.TestCase):

    @patch('pcBuildListCompiler.createBuildList.sqlite3.connect')
    def testFullBuildGeneration(self, mockConnect):
        logger.info("Running Test #8: Full build generation")

        compiler = PcBuildCompiler(
            budget=2000, gpuPreference="None",
            aestheticsWeight=2, futureWeight=3, tier="medium"
        )

        mockConn = MagicMock()
        mockCursor = MagicMock()
        mockConnect.return_value = mockConn
        mockConn.cursor.return_value = mockCursor

        def mockFetchall():
            return [{
                "partNumber": f"TEST-{i}", "name": f"Test Part {i}",
                "price": 100 + i, "url": "url", "imagePath": "path",
                "score": 50, "scoreEfficiency": 60, "scoreUpgradeability": 70,
                "socketId": 1, "tdpWatts": 50, "lengthMm": 250,
                "formFactor": "ATX", "memorySlots": 4, "memoryType": "DDR5",
                "maxMemory": 128, "ddrType": "DDR5", "numberOfModules": 2,
                "capacityGb": 16, "wattage": 650, "efficiencyRating": "Gold",
                "gpuMaxLength": 350, "formFactorSupport": "ATX"
            } for i in range(2)]

        mockCursor.execute.return_value.fetchall = mockFetchall

        bestBuild, bestScore, bestPrice = compiler.findBestBuild()
        logger.info(f"Best score: {bestScore}, Best price: {bestPrice}")

        self.assertIsNotNone(bestScore)
        self.assertIsNotNone(bestPrice)


class TestEdgeCases(unittest.TestCase):

    @patch('pcBuildListCompiler.createBuildList.sqlite3.connect')
    def testHandlesNoValidBuilds(self, mockConnect):
        logger.info("Running Test #10: No valid builds")

        compiler = PcBuildCompiler(
            budget=50, gpuPreference="None",
            aestheticsWeight=2, futureWeight=3, tier="high"
        )

        mockConn = MagicMock()
        mockCursor = MagicMock()
        mockConnect.return_value = mockConn
        mockConn.cursor.return_value = mockCursor

        def mockExpensiveParts():
            return [{
                "partNumber": "EXPENSIVE", "name": "Expensive", "price": 500,
                "url": "url", "imagePath": "path",
                "score": 80, "scoreEfficiency": 90, "scoreUpgradeability": 85,
                "socketId": 1, "tdpWatts": 100, "lengthMm": 300,
                "formFactor": "ATX", "memorySlots": 4, "memoryType": "DDR5",
                "maxMemory": 128, "ddrType": "DDR5", "numberOfModules": 2,
                "capacityGb": 32, "wattage": 850, "efficiencyRating": "Platinum",
                "gpuMaxLength": 400, "formFactorSupport": "ATX"
            }]

        mockCursor.execute.return_value.fetchall = mockExpensiveParts

        bestBuild, bestScore, bestPrice = compiler.findBestBuild()
        logger.info("No valid build found")

        self.assertIsNone(bestBuild)
        self.assertEqual(bestScore, 0)


class TestPerformance(unittest.TestCase):

    @patch('pcBuildListCompiler.createBuildList.sqlite3.connect')
    def testCompletesWithinReasonableTime(self, mockConnect):
        logger.info("Running Test #15: Performance test")

        compiler = PcBuildCompiler(
            budget=2000, gpuPreference="None",
            aestheticsWeight=2,
            futureWeight=3,
            tier="medium"
        )

        mockConn = MagicMock()
        mockCursor = MagicMock()
        mockConnect.return_value = mockConn
        mockConn.cursor.return_value = mockCursor

        def mockRealisticParts():
            return [{
                "partNumber": f"PART-{i}", "name": f"Part {i}",
                "price": 100 + i * 20, "url": "url", "imagePath": "path",
                "score": 50 + i * 5, "scoreEfficiency": 60, "scoreUpgradeability": 70,
                "socketId": 1, "tdpWatts": 50 + i * 5, "lengthMm": 250,
                "formFactor": "ATX", "memorySlots": 4, "memoryType": "DDR5",
                "maxMemory": 128, "ddrType": "DDR5", "numberOfModules": 2,
                "capacityGb": 16 + i * 8, "wattage": 650 + i * 50,
                "efficiencyRating": "Gold", "gpuMaxLength": 350,
                "formFactorSupport": "ATX"
            } for i in range(10)]

        mockCursor.execute.return_value.fetchall = mockRealisticParts

        start = time.time()
        compiler.findBestBuild()
        end = time.time()

        elapsed = end - start
        logger.info(f"Performance test completed in {elapsed:.2f}s")

        self.assertLess(elapsed, 10.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
