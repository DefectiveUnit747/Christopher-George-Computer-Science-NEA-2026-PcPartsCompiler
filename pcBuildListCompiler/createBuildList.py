import sqlite3
import math
import logging

from pcBuildListCompiler.compatibilityFunctions import *

logger = logging.getLogger(__name__)

PART_MAPPING = {
    "cpu": {
        "table": "cpu",
        "columns": [
            "partNumber", "name", "price", "url",
            "socketId", "tdpWatts", "imagePath",
            "score", "scoreEfficiency", "scoreUpgradeability"
        ],
        "tierName": "cpu"
    },
    "gpu": {
        "table": "gpu",
        "columns": [
            "partNumber", "name", "price", "url",
            "tdpWatts", "lengthMm", "imagePath",
            "score", "scoreEfficiency", "scoreUpgradeability"
        ],
        "tierName": "gpu"
    },
    "motherboard": {
        "table": "motherboard",
        "columns": [
            "partNumber", "name", "price", "url",
            "socketId", "formFactor", "tdpWatts",
            "memorySlots", "memoryType", "maxMemory",
            "imagePath",
            "score", "scoreEfficiency", "scoreUpgradeability"
        ],
        "tierName": None
    },
    "ram": {
        "table": "ram",
        "columns": [
            "partNumber", "name", "price", "url",
            "ddrType", "numberOfModules", "capacityGb",
            "imagePath",
            "score", "scoreEfficiency", "scoreUpgradeability"
        ],
        "tierName": "ram"
    },
    "psu": {
        "table": "psu",
        "columns": [
            "partNumber", "name", "price", "url",
            "wattage", "efficiencyRating", "imagePath",
            "score", "scoreEfficiency", "scoreUpgradeability"
        ],
        "tierName": None
    },
    "case": {
        "table": "cases",
        "columns": [
            "partNumber", "name", "price", "url",
            "gpuMaxLength", "formFactorSupport",
            "imagePath",
            "score", "scoreEfficiency", "scoreUpgradeability"
        ],
        "tierName": None
    },
    "storage": {
        "table": "storage",
        "columns": [
            "partNumber", "name", "price", "url",
            "capacityGb", "imagePath",
            "score", "scoreEfficiency", "scoreUpgradeability"
        ],
        "tierName": None
    }
}

TIER_MAPPING = {
    "low":    {"cpu": 0,  "gpu": 20, "ram": 10},
    "medium": {"cpu": 30, "gpu": 50, "ram": 20},
    "high":   {"cpu": 50, "gpu": 75, "ram": 35},
}

GPU_MAPPING = {
    "AMD": 3,
    "Nvidia": 40,
    "Intel": 33
}

COMPONENT_ORDER = ["gpu", "cpu", "motherboard", "ram", "storage", "psu", "case"]


class Component:
    def __init__(self, data: dict):
        self.data = data

    @property
    def price(self):
        return self.data.get("price", 0)

    @property
    def finalScore(self):
        return self.data.get("finalScore", 0)

    def isCompatibleWith(self, build: dict) -> bool:
        return True

class CPU(Component):
    def isCompatibleWith(self, build: dict) -> bool:
        if "motherboard" in build:
            if not isCpuCompatibleWithMotherboard(self.data, build["motherboard"].data):
                return False
        if "psu" in build:
            if not isPsuCompatibleWithCpu(build["psu"].data, self.data):
                return False
        return True

class GPU(Component):
    def isCompatibleWith(self, build: dict) -> bool:
        if "case" in build:
            if not isGpuCompatibleWithCase(self.data, build["case"].data):
                return False
        if "psu" in build:
            if not isPsuCompatibleWithGpu(build["psu"].data, self.data):
                return False
        return True

class Motherboard(Component):
    def isCompatibleWith(self, build: dict) -> bool:
        if "cpu" in build:
            if not isCpuCompatibleWithMotherboard(build["cpu"].data, self.data):
                return False
        if "ram" in build:
            if not isMotherboardCompatibleWithRam(self.data, build["ram"].data):
                return False
            if not isRamCapacityCompatibleWithMotherboard(build["ram"].data, self.data):
                return False
        if "psu" in build:
            if not isPsuCompatibleWithMotherboard(build["psu"].data, self.data):
                return False
        return True

class RAM(Component):
    def isCompatibleWith(self, build: dict) -> bool:
        if "motherboard" in build:
            if not isMotherboardCompatibleWithRam(build["motherboard"].data, self.data):
                return False
            if not isRamCapacityCompatibleWithMotherboard(self.data, build["motherboard"].data):
                return False
        return True

class PSU(Component):
    def isCompatibleWith(self, build: dict) -> bool:
        totalTdp = sum(part.data.get("tdpWatts", 0) for part in build.values())
        return self.data.get("wattage", 0) >= totalTdp

class Case(Component):
    def isCompatibleWith(self, build: dict) -> bool:
        if "gpu" in build:
            if not isGpuCompatibleWithCase(build["gpu"].data, self.data):
                return False
        if "motherboard" in build:
            if not isMotherboardCompatibleWithCase(build["motherboard"].data, self.data):
                return False
        return True

class Storage(Component):
    pass


COMPONENT_CLASSES = {
    "cpu": CPU,
    "gpu": GPU,
    "motherboard": Motherboard,
    "ram": RAM,
    "psu": PSU,
    "case": Case,
    "storage": Storage
}


class PcBuildCompiler:
    def __init__(self, budget, gpuPreference, aestheticsWeight, futureWeight, tier):
        self.budget = budget
        self.gpuPreference = gpuPreference
        self.aestheticsWeight = aestheticsWeight
        self.futureWeight = futureWeight
        self.tier = tier

        self.validParts = {}
        self.bestBuild = None
        self.bestScore = 0.0
        self.bestPrice = 0.0

    def _paretoFilter(self, partsList):
        if not partsList:
            return partsList

        filtered = []
        for i in range(len(partsList)):
            pn1, d1 = partsList[i]
            dominated = False

            for j in range(len(partsList)):
                if i == j:
                    continue

                pn2, d2 = partsList[j]

                if d2["finalScore"] > d1["finalScore"] and d2["price"] < d1["price"]:
                    dominated = True
                    break

            if not dominated:
                filtered.append((pn1, d1))

        return filtered

    def _reformatScores(self, validDict):
        for key, value in validDict.items():
            score = float(value.get("score", 0))
            eff = float(value.get("scoreEfficiency", 0))
            upg = float(value.get("scoreUpgradeability", 0))
            weighted = 5 * score + self.aestheticsWeight * eff + self.futureWeight * upg
            value.pop("score", None)
            value.pop("scoreEfficiency", None)
            value.pop("scoreUpgradeability", None)
            value["finalScore"] = weighted
        return validDict

    def _mergeSortParts(self, parts):
        if len(parts) <= 1:
            return parts
        mid = len(parts) // 2
        left = self._mergeSortParts(parts[:mid])
        right = self._mergeSortParts(parts[mid:])
        return self._mergeParts(left, right)

    def _mergeParts(self, left, right):
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i][1]["finalScore"] >= right[j][1]["finalScore"]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    def loadValidParts(self, dbPath="computerParts.db"):
        logger.info("Loading valid parts")

        conn = sqlite3.connect(dbPath)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        validPartsDicts = {}

        for key, value in PART_MAPPING.items():
            minScore = TIER_MAPPING[self.tier][key] if value["tierName"] else 0
            columns = ", ".join(value["columns"])
            table = value["table"]

            if key == "gpu" and self.gpuPreference != "None":
                manufacturerId = GPU_MAPPING[self.gpuPreference]
                query = f"SELECT {columns} FROM {table} WHERE score >= ? AND manufacturerId = ?"
                values = c.execute(query, (minScore, manufacturerId)).fetchall()
                logger.info("Applied GPU preference: %s", self.gpuPreference)
            else:
                query = f"SELECT {columns} FROM {table} WHERE score >= ?"
                values = c.execute(query, (minScore,)).fetchall()

            logger.info("Loaded %d %s parts", len(values), key)

            validDict = {part["partNumber"]: dict(part) for part in values}
            formattedDict = self._reformatScores(validDict)
            sortedParts = self._mergeSortParts(list(formattedDict.items()))
            filteredParts = self._paretoFilter(sortedParts)

            validPartsDicts[key] = filteredParts

        conn.close()

        wrapped = {}
        for compType, partsList in validPartsDicts.items():
            cls = COMPONENT_CLASSES[compType]
            wrapped[compType] = [(pn, cls(data)) for pn, data in partsList]

        self.validParts = wrapped

    def _getMaxScorePerComponent(self, partsList):
        return partsList[0][1].finalScore if partsList else 0

    def _getMinPricePerComponent(self, partsList):
        return min(part.price for _, part in partsList) if partsList else math.inf

    def _lowerBoundPruning(self, remaining):
        return sum(self._getMinPricePerComponent(self.validParts[comp]) for comp in remaining)

    def _branchAndBoundUpper(self, remaining):
        return sum(self._getMaxScorePerComponent(self.validParts[comp]) for comp in remaining)

    def _dfs(self, level, currentBuild, currentPrice, currentScore):
        if level == len(COMPONENT_ORDER):
            if currentScore > self.bestScore:
                self.bestScore = currentScore
                self.bestBuild = currentBuild.copy()
                self.bestPrice = currentPrice
                logger.info("New best build: score=%.2f price=%.2f", currentScore, currentPrice)
            return

        currentType = COMPONENT_ORDER[level]
        remaining = COMPONENT_ORDER[level + 1:]

        maxScoreFuture = 0.95 * self._branchAndBoundUpper(remaining)
        minBudgetFuture = self._lowerBoundPruning(remaining)

        for partNumber, part in self.validParts.get(currentType, []):
            newPrice = currentPrice + (1.2 * part.price if currentType == "gpu" else part.price)

            if newPrice > self.budget:
                continue
            if (self.budget - newPrice) < minBudgetFuture:
                continue
            if not part.isCompatibleWith(currentBuild):
                continue
            if self.bestBuild and (currentScore + maxScoreFuture) <= self.bestScore:
                continue

            newBuild = currentBuild.copy()
            newBuild[currentType] = part
            newScore = currentScore + part.finalScore

            self._dfs(level + 1, newBuild, newPrice, newScore)

    def findBestBuild(self, dbPath="computerParts.db"):
        logger.info("Starting build search")
        self.loadValidParts(dbPath)
        self.bestBuild = None
        self.bestScore = 0
        self.bestPrice = 0

        self._dfs(0, {}, 0.0, 0.0)

        logger.info("Build search complete: bestScore=%.2f bestPrice=%.2f",
                    self.bestScore, self.bestPrice)

        return self.bestBuild, self.bestScore, self.bestPrice




