import unittest
import logging
import time
from unittest.mock import patch
from pcBuildListCompiler.compatibilityFunctions import (
    isCpuCompatibleWithMotherboard,
    isMotherboardCompatibleWithRam,
    isRamCapacityCompatibleWithMotherboard,
    isGpuCompatibleWithCase,
    isMotherboardCompatibleWithCase,
    isPsuCompatibleWithMotherboard,
    isPsuCompatibleWithCpu,
    isPsuCompatibleWithGpu
)
from pcBuildListCompiler.createBuildList import (
    PcBuildCompiler, CPU, GPU, Motherboard, RAM, PSU, Case, Storage
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

class TestIsCpuCompatibleWithMotherboard(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testMatchingSocketsReturnsTrue(self):
        cpu = {"socketId": "AM5"}
        motherboard = {"socketId": "AM5"}
        result = isCpuCompatibleWithMotherboard(cpu, motherboard)
        logger.info(f"cpu={cpu}, motherboard={motherboard}, result={result}")
        self.assertTrue(result)

    def testMismatchedSocketsReturnsFalse(self):
        cpu = {"socketId": "AM5"}
        motherboard = {"socketId": "LGA1700"}
        result = isCpuCompatibleWithMotherboard(cpu, motherboard)
        logger.info(f"cpu={cpu}, motherboard={motherboard}, result={result}")
        self.assertFalse(result)

    def testNoneSocketIdReturnsFalse(self):
        cpu = {"socketId": None}
        motherboard = {"socketId": "AM5"}
        result = isCpuCompatibleWithMotherboard(cpu, motherboard)
        logger.info(f"cpu socketId=None, motherboard={motherboard}, result={result}")
        self.assertFalse(result)


class TestIsMotherboardCompatibleWithRam(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testMatchingDdrTypeReturnsTrue(self):
        motherboard = {"memoryType": "DDR5"}
        ram = {"ddrType": "DDR5"}
        result = isMotherboardCompatibleWithRam(motherboard, ram)
        logger.info(f"motherboard={motherboard}, ram={ram}, result={result}")
        self.assertTrue(result)

    def testMismatchedDdrTypeReturnsFalse(self):
        motherboard = {"memoryType": "DDR4"}
        ram = {"ddrType": "DDR5"}
        result = isMotherboardCompatibleWithRam(motherboard, ram)
        logger.info(f"motherboard={motherboard}, ram={ram}, result={result}")
        self.assertFalse(result)


class TestIsRamCapacityCompatibleWithMotherboard(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testModulesFitReturnsTrue(self):
        ram = {"numberOfModules": 2}
        motherboard = {"memorySlots": 4}
        result = isRamCapacityCompatibleWithMotherboard(ram, motherboard)
        logger.info(f"ram={ram}, motherboard={motherboard}, result={result}")
        self.assertTrue(result)

    def testModulesExceedSlotsReturnsFalse(self):
        ram = {"numberOfModules": 4}
        motherboard = {"memorySlots": 2}
        result = isRamCapacityCompatibleWithMotherboard(ram, motherboard)
        logger.info(f"ram={ram}, motherboard={motherboard}, result={result}")
        self.assertFalse(result)


class TestIsGpuCompatibleWithCase(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testGpuFitsReturnsTrue(self):
        gpu = {"lengthMm": 300}
        case = {"gpuMaxLength": 380}
        result = isGpuCompatibleWithCase(gpu, case)
        logger.info(f"gpu={gpu}, case={case}, result={result}")
        self.assertTrue(result)

    def testGpuTooLongReturnsFalse(self):
        gpu = {"lengthMm": 400}
        case = {"gpuMaxLength": 380}
        result = isGpuCompatibleWithCase(gpu, case)
        logger.info(f"gpu={gpu}, case={case}, result={result}")
        self.assertFalse(result)

    def testGpuExactlyAtMaxLengthReturnsTrue(self):
        gpu = {"lengthMm": 380}
        case = {"gpuMaxLength": 380}
        result = isGpuCompatibleWithCase(gpu, case)
        logger.info(f"gpu lengthMm=380, case gpuMaxLength=380, result={result}")
        self.assertTrue(result)


class TestIsMotherboardCompatibleWithCase(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testSupportedFormFactorReturnsTrue(self):
        motherboard = {"formFactor": "ATX"}
        case = {"formFactorSupport": "ATX"}
        result = isMotherboardCompatibleWithCase(motherboard, case)
        logger.info(f"motherboard={motherboard}, case={case}, result={result}")
        self.assertTrue(result)

    def testUnsupportedFormFactorReturnsFalse(self):
        motherboard = {"formFactor": "ATX"}
        case = {"formFactorSupport": "ITX"}
        result = isMotherboardCompatibleWithCase(motherboard, case)
        logger.info(f"motherboard={motherboard}, case={case}, result={result}")
        self.assertFalse(result)


class TestIsPsuCompatibleWithGpu(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testSufficientWattageReturnsTrue(self):
        psu = {"wattage": 850}
        gpu = {"tdpWatts": 200}
        result = isPsuCompatibleWithGpu(psu, gpu)
        logger.info(f"psu wattage=850, gpu tdp=200, result={result}")
        self.assertTrue(result)

    def testInsufficientWattageReturnsFalse(self):
        psu = {"wattage": 300}
        gpu = {"tdpWatts": 400}
        result = isPsuCompatibleWithGpu(psu, gpu)
        logger.info(f"psu wattage=300, gpu tdp=400, result={result}")
        self.assertFalse(result)


class TestIsPsuCompatibleWithCpu(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testSufficientWattageReturnsTrue(self):
        psu = {"wattage": 850}
        cpu = {"tdpWatts": 105}
        result = isPsuCompatibleWithCpu(psu, cpu)
        logger.info(f"psu wattage=850, cpu tdp=105, result={result}")
        self.assertTrue(result)

    def testInsufficientWattageReturnsFalse(self):
        psu = {"wattage": 50}
        cpu = {"tdpWatts": 105}
        result = isPsuCompatibleWithCpu(psu, cpu)
        logger.info(f"psu wattage=50, cpu tdp=105, result={result}")
        self.assertFalse(result)


class TestIsPsuCompatibleWithMotherboard(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")

    def testSufficientWattageReturnsTrue(self):
        psu = {"wattage": 850}
        motherboard = {"tdpWatts": 15}
        result = isPsuCompatibleWithMotherboard(psu, motherboard)
        logger.info(f"psu wattage=850, motherboard tdp=15, result={result}")
        self.assertTrue(result)

    def testInsufficientWattageReturnsFalse(self):
        psu = {"wattage": 10}
        motherboard = {"tdpWatts": 15}
        result = isPsuCompatibleWithMotherboard(psu, motherboard)
        logger.info(f"psu wattage=10, motherboard tdp=15, result={result}")
        self.assertFalse(result)


class TestMergeSortParts(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.compiler = PcBuildCompiler.__new__(PcBuildCompiler)

    def testSortsByFinalScoreDescending(self):
        parts = [
            ("P1", {"finalScore": 300, "price": 100}),
            ("P2", {"finalScore": 100, "price": 200}),
            ("P3", {"finalScore": 200, "price": 150}),
            ("P4", {"finalScore": 150, "price": 180})
        ]
        result = self.compiler._mergeSortParts(parts)
        scores = [d["finalScore"] for _, d in result]
        logger.info(f"Sorted scores: {scores}")
        self.assertEqual(scores, [300, 200, 150, 100])


class TestParetoFilter(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.compiler = PcBuildCompiler.__new__(PcBuildCompiler)

    def testRemovesDominatedParts(self):
        parts = [
            ("P1", {"finalScore": 100, "price": 200}),
            ("P2", {"finalScore": 150, "price": 150}),
            ("P3", {"finalScore": 120, "price": 180})
        ]
        result = self.compiler._paretoFilter(parts)
        scores = [d["finalScore"] for _, d in result]
        logger.info(f"Pareto result count: {len(result)}, scores: {scores}")
        self.assertEqual(len(result), 1)
        self.assertEqual(scores[0], 150)


class TestLowerBoundPruning(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.compiler = PcBuildCompiler.__new__(PcBuildCompiler)

    def testCalculatesMinimumRemainingCostCorrectly(self):
        self.compiler.validParts = {
            "cpu": [("CPU-001", CPU({"price": 300, "finalScore": 80})),
                    ("CPU-002", CPU({"price": 200, "finalScore": 70}))],
            "gpu": [("GPU-001", GPU({"price": 500, "finalScore": 90})),
                    ("GPU-002", GPU({"price": 350, "finalScore": 85}))]
        }
        result = self.compiler._lowerBoundPruning(["cpu", "gpu"])
        logger.info(f"Lower bound result: {result}, expected: 550")
        self.assertEqual(result, 550)


class TestBranchAndBoundUpper(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.compiler = PcBuildCompiler.__new__(PcBuildCompiler)

    def testReturnsSumOfMaxScores(self):
        self.compiler.validParts = {
            "cpu": [("CPU-001", CPU({"price": 300, "finalScore": 100})),
                    ("CPU-002", CPU({"price": 200, "finalScore": 80}))],
            "gpu": [("GPU-001", GPU({"price": 500, "finalScore": 100})),
                    ("GPU-002", GPU({"price": 350, "finalScore": 90}))]
        }
        result = self.compiler._branchAndBoundUpper(["cpu", "gpu"])
        logger.info(f"Upper bound result: {result}, expected: 200")
        self.assertEqual(result, 200)

if __name__ == "__main__":
    unittest.main()