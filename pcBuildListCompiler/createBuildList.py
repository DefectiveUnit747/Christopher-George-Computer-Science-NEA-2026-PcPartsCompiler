from compatibilityFunctions import *
import sqlite3
import math

# Constants
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
    "low": {"cpu": 0, "gpu": 20, "ram": 10},
    "medium": {"cpu": 30, "gpu": 50, "ram": 20},
    "high": {"cpu": 50, "gpu": 75, "ram": 35},
}
GPU_MAPPING = {
    "AMD": 3,
    "Nvidia": 40,
    "Intel": 33
}
COMPONENT_ORDER = ["gpu", "cpu", "motherboard", "ram", "storage", "psu", "case"]

# Global variables (set by Flask before running algorithm)
budget = 1400
gpuPreference = "None"
aestheticsWeightage = 2
futureProofingWeightage = 4
tier = "medium"
validPartsDict = {}
bestBuild = None
bestScore = 0
bestPrice = 0
compatibilityCache = {}

def paretoFilter(partsList):
    #Remove dominated parts that r definitely worse in both score AND price
    if len(partsList) == 0:
        return partsList

    filtered = []

    for i in range(len(partsList)):
        partNumber1, partData1 = partsList[i]
        isDominated = False

        for j in range(len(partsList)):
            if i == j:
                continue

            partNumber2, partData2 = partsList[j]

            # Part 1 is dominated ONLY if Part 2 is STRICTLY better in BOTH dimensions
            if (partData2["finalScore"] > partData1["finalScore"] and
                    partData2["price"] < partData1["price"]):
                isDominated = True
                break

        if not isDominated:
            filtered.append((partNumber1, partData1))

    return filtered

def getValidPartsFromDb(gpuPreference, tier, aestheticsWeightage, futureProofingWeightage):
    validPartsDicts = {}
    conn = sqlite3.connect("computerParts.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    for key, value in PART_MAPPING.items():
        minScore = TIER_MAPPING[tier][key] if value["tierName"] else 0
        columns = ", ".join(value["columns"])
        table = value["table"]

        if key == "gpu" and gpuPreference != "None":
            manufacturerId = GPU_MAPPING[gpuPreference]
            query = f"SELECT {columns} FROM {table} WHERE score >= ? AND manufacturerId = ?"
            values = c.execute(query, (minScore, manufacturerId)).fetchall()
        else:
            query = f"SELECT {columns} FROM {table} WHERE score >= ?"
            values = c.execute(query, (minScore,)).fetchall()

        validDict = {part["partNumber"]: dict(part) for part in values}
        formattedDict = reformatDictionariesWithNewScores(validDict, aestheticsWeightage, futureProofingWeightage)

        # Sort parts by finalScore (highest first) using merge sort
        sortedParts = mergeSortParts(list(formattedDict.items()))

        # Apply Pareto filtering
        filteredParts = paretoFilter(sortedParts)

        validPartsDicts[key] = filteredParts

    conn.close()
    return validPartsDicts

def reformatDictionariesWithNewScores(validDict, aestheticsWeightage, futureProofingWeightage):
    for key, value in validDict.items():
        score = float(value.get("score", 0))
        efficiencyScore = float(value.get("scoreEfficiency", 0))
        futureScore = float(value.get("scoreUpgradeability", 0))
        performanceWeight = 5

        weightedScore = (performanceWeight * score) + (aestheticsWeightage * efficiencyScore) + (
                futureProofingWeightage * futureScore)
        value.pop("score")
        value.pop("scoreEfficiency")
        value.pop("scoreUpgradeability")
        value["finalScore"] = weightedScore
    return validDict

def mergeSortParts(parts):
    if len(parts) <= 1:
        return parts

    mid = len(parts) // 2
    left = mergeSortParts(parts[:mid])
    right = mergeSortParts(parts[mid:])

    return mergeParts(left, right)

def mergeParts(left, right):
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        left_score = left[i][1]["finalScore"]
        right_score = right[j][1]["finalScore"]

        if left_score >= right_score:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

def getMaxScorePerComponent(componentType, partsList):
    # Return highest score (first in pre-sorted list)
    return partsList[0][1]['finalScore'] if partsList else 0

def getMinPricePerComponent(partsList):
    # Now partsList is a list of tuples, not a dict
    return min(partData["price"] for _, partData in partsList) if partsList else math.inf

def lowerBoundPruning(remaining, validPartsDict):
    return sum(getMinPricePerComponent(validPartsDict[i]) for i in remaining)

def branchAndBound(build, remaining, validPartsDict):
    return sum(getMaxScorePerComponent(i, validPartsDict[i]) for i in remaining)

def isCompatibleWithCurrentBuild(componentType, newPart, currentBuild):
    if componentType == "cpu":
        if "motherboard" in currentBuild and not isCpuCompatibleWithMotherboard(newPart, currentBuild["motherboard"]):
            return False
        if "psu" in currentBuild and not isPsuCompatibleWithCpu(currentBuild["psu"], newPart):
            return False
        return True

    elif componentType == "motherboard":
        if "cpu" in currentBuild and not isCpuCompatibleWithMotherboard(currentBuild["cpu"], newPart):
            return False
        if "ram" in currentBuild:
            if not isMotherboardCompatibleWithRam(newPart, currentBuild["ram"]):
                return False
            if not isRamCapacityCompatibleWithMotherboard(currentBuild["ram"], newPart):
                return False
        if "psu" in currentBuild and not isPsuCompatibleWithMotherboard(currentBuild["psu"], newPart):
            return False
        return True

    elif componentType == "ram":
        if "motherboard" in currentBuild:
            if not isMotherboardCompatibleWithRam(currentBuild["motherboard"], newPart):
                return False
            if not isRamCapacityCompatibleWithMotherboard(newPart, currentBuild["motherboard"]):
                return False
        return True

    elif componentType == "gpu":
        if "case" in currentBuild and not isGpuCompatibleWithCase(newPart, currentBuild["case"]):
            return False
        if "psu" in currentBuild and not isPsuCompatibleWithGpu(currentBuild["psu"], newPart):
            return False
        return True

    elif componentType == "psu":
        return newPart["wattage"] >= calculateTotalWattage(currentBuild)

    elif componentType == "case":
        if "gpu" in currentBuild and not isGpuCompatibleWithCase(currentBuild["gpu"], newPart):
            return False
        if "motherboard" in currentBuild and not isMotherboardCompatibleWithCase(currentBuild["motherboard"], newPart):
            return False
        return True

    return True

def calculateTotalWattage(build):
    return sum(partData.get("tdpWatts", 0) for partData in build.values())

def depthFirstSearch(level, currentBuild, currentPrice, currentScore, budget, validPartsDict):
    global bestBuild, bestScore, bestPrice

    if level == 7:
        if currentScore > bestScore:
            bestScore = currentScore
            bestBuild = currentBuild.copy()
            bestPrice = currentPrice
            print(f"New Best Score: {currentScore}, Price: £{currentPrice:.2f}")
        return

    currentComponentType = COMPONENT_ORDER[level]
    remaining = COMPONENT_ORDER[level + 1:]
    maxScore = 0.95 * branchAndBound(currentBuild, remaining, validPartsDict)
    minBudgetOnBranch = lowerBoundPruning(remaining, validPartsDict)


    for partNumber, partData in validPartsDict[currentComponentType]:
        if currentComponentType == "gpu":
            newPrice = currentPrice + (1.2 * partData["price"])
        else:
            newPrice = currentPrice + partData["price"]

        # Pruning checks
        if newPrice > budget:
            continue
        if (budget - newPrice) < minBudgetOnBranch:
            continue
        if not isCompatibleWithCurrentBuild(currentComponentType, partData, currentBuild):
            continue
        if bestBuild and (currentScore + maxScore) <= bestScore:
            continue

        newBuild = currentBuild.copy()
        newBuild[currentComponentType] = partData
        newScore = currentScore + partData["finalScore"]
        depthFirstSearch(level + 1, newBuild, newPrice, newScore, budget, validPartsDict)