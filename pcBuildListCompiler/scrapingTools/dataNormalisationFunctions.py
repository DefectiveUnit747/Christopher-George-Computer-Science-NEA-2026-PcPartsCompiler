import math

gpuMemoryTypeScore = {
    "GDDR5": 1,
    "GDDR5X": 1.5,  # Standard ones
    "GDDR6": 2,
    "GDDR6X": 3,
    "GDDR7": 4,
    "HBM": 2.5,     # High Bandwidth Memory niche vega stuf typical AMD
    "HBM2": 3,
    "HBM2E": 3.5,
    "HBM3": 4
}
ddrScores = {"DDR3": 5, "DDR4": 15, "DDR5": 20}
efficiencyMap = {
    "na": {"performance": 0, "efficiency": 0},
    "bronze": {"performance": 15, "efficiency": 35},
    "silver": {"performance": 25, "efficiency": 50},
    "gold": {"performance": 30, "efficiency": 65},
    "platinum": {"performance": 35, "efficiency": 85},
    "titanium": {"performance": 40, "efficiency": 100}
} #The 80+ efficiency will have different weights when I calculate the score vs the efficiency score, so there is a dictionary for each efficiency tier

formFactorWeights = {
    "EATX": 4,
    "E-ATX": 4,
    "XL-ATX": 4,
    "ATX": 3,
    "mATX": 2,
    "Micro ATX": 2, #Got Worded versions asw in case of inconsistency across site
    "Micro-ATX": 2,
    "Mini ITX": 1,
    "Mini-ITX": 1,
}

def normaliseCpuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    print(specs)
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "scoreEfficiency": 0,
        "scoreUpgradeability": 0,
        "coreCount": int(specs["coreCount"].split(" ")[0]),
        "coreClock": float(specs["coreClock"].split(" ")[0]),
        "cache": float(specs["cache"].split(" ")[0]),
        "threads": int(specs["threads"]),
        "tdpWatts": int(specs["tdp"].split(" ")[0]) if isinstance(specs["tdp"], str) else int(specs["tdp"][0]),
        "socketId": specs["socket"]
    }
    return assignCpuScore(normalisedSpecs)

def normaliseMotherboardScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "scoreEfficiency": 0,
        "scoreUpgradeability": 0,
        "socketId": specs["socket"],
        "formFactor": specs["formFactor"],
        "tdpWatts": int(specs["tdp"].split(" ")[0]) if isinstance(specs["tdp"], str) else int(specs["tdp"][0]),
        "memorySlots": int(specs["memorySlots"].split(" ")[0]),
        "memoryType": (specs["memoryType"])[:4],
        "maxMemory": int(specs["maxMemory"].split(" ")[0])
    }
    return assignMotherBoardScore(normalisedSpecs)

def normaliseRamScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "scoreEfficiency": 0,
        "scoreUpgradeability": 0,
        "capacityGb": int(specs["capacityGb"].split(" ")[0]),
        "numberOfModules": int(specs["numberOfModules"]),
        "speedMhz": int(specs["speedMhz"]),
        "ddrType": specs["ddrType"]
    }
    return assignRamScore(normalisedSpecs)

def normaliseStorageScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    capacity = int(specs["capacityGb"].split(" ")[0])
    if capacity < 5:
        capacity = capacity * 1000
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "scoreEfficiency": 0,
        "scoreUpgradeability": 0,
        "capacityGb": capacity,
        "readSpeed": normaliseReadWriteOrRpm(specs["readSpeed"]),
        "writeSpeed": normaliseReadWriteOrRpm(specs["writeSpeed"]),
        "formFactor": specs["formFactor"] if specs["formFactor"] else "SSD"
    }
    return assignStorageScore(normalisedSpecs)

def normaliseGpuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score): #FIX THE CORECLOCK ONE
    print(specs)
    mem = int(specs["memoryGb"].split(" ")[0])
    memInGb = (math.floor(mem / 10 ** (math.floor(math.log10(mem)) - 1)) * 10 ** (math.floor(math.log10(mem)) - 1))//1000
    coreClockBeforeNormalisation = specs["coreClock"].split(" ")
    coreClock = None
    for word in coreClockBeforeNormalisation:
        if word.isdigit():
            coreClock = int(word)
            break
    tdp = (specs["tdpWatts"].split(" ")[0])
    tdpWatts = ""
    for i in tdp:
        if i.isdigit():
            tdpWatts += i
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "scoreEfficiency": 0,
        "scoreUpgradeability": 0,
        "memoryGb": memInGb,
        "coreClock": coreClock,
        "memoryType": (specs["memoryType"]).upper(),
        "tdpWatts": int(tdpWatts),
        "lengthMm": float(specs["length"].split(" ")[0])
    }
    return assignGpuScore(normalisedSpecs)

def normaliseCaseScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "scoreEfficiency": 0,
        "scoreUpgradeability": 0,
        "formFactorSupport": specs["formFactorSupport"],
        "gpuMaxLength": int(specs["gpuMaxLength"].split(" ")[0]),
    }
    return assignCaseScore(normalisedSpecs)

def normalisePsuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    efficiency = normaliseEfficiencyRating(specs["efficiencyRating"])
    modularity = specs["modularity"]
    modular = True if modularity == "Modular" else False
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "scoreEfficiency": 0,
        "scoreUpgradeability": 0,
        "wattage": int(specs["wattage"].split(" ")[0]),
        "efficiencyRating": efficiency,
        "formFactor": specs["formFactor"],
        "modular": modular
    }
    return assignPsuScore(normalisedSpecs)

#######################################################################################################################################

def assignCpuScore(specs):
    coreCount = specs["coreCount"]
    coreClock = specs["coreClock"]
    cache = specs["cache"]
    tdp = specs["tdpWatts"]
    threads = specs["threads"]

    rawPerformanceScore = coreCount * coreClock
    performance = featureScaling(rawPerformanceScore, 8, 150, 70)
    threadBonus = featureScaling(threads / max(coreCount, 1), 1.0, 2.0, 30)
    normalScore = max(0, min(100, round(performance + threadBonus)))

    perfPerWatt = rawPerformanceScore / max(tdp, 1)
    scaledEfficiency = featureScaling(perfPerWatt, 0.1, 1.5, 100)
    penaltyForTdp = exponentialDecay(tdp, 0.003)
    scoreEfficiency = round(max(0, min(100, scaledEfficiency * penaltyForTdp)))

    coreUpgrade = tanhSigmoidScaling(coreCount, midpoint=12, scaleFactor=6)
    cacheUpgrade = tanhSigmoidScaling(cache, midpoint=36, scaleFactor=18)
    scoreUpgradeability = max(0, min(100, round((coreUpgrade + cacheUpgrade) / 2)))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignRamScore(specs):
    capacity = specs["capacityGb"]
    ddrType = specs["ddrType"]
    numberOfModules = specs["numberOfModules"]
    speed = specs["speedMhz"]

    capacityScore = featureScaling(capacity, 4, 128, 50)
    speedScore = featureScaling(speed, 1600, 6400, 40)
    ddrScore = ddrScores.get(ddrType, 5)
    normalScore = max(0, min(100, round(capacityScore + speedScore + ddrScore)))

    scoreEfficiency = 0

    capacityUpgrade = tanhSigmoidScaling(capacity, midpoint=32, scaleFactor=16)
    moduleUpgrade = featureScaling(4 - numberOfModules, 0, 3, 100)
    scoreUpgradeability = max(0, min(100, round((capacityUpgrade + moduleUpgrade) / 2)))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignGpuScore(specs):
    memoryGb = specs["memoryGb"]
    coreClock = specs["coreClock"]
    memoryType = specs["memoryType"]
    tdp = specs["tdpWatts"]

    memoryTypeScore = gpuMemoryTypeScore.get(memoryType, 2)
    rawPerformanceScore = memoryGb * coreClock * memoryTypeScore
    normalScore = max(0, min(100, round(featureScaling(rawPerformanceScore, 1500, 160000, 100))))

    perfPerWatt = rawPerformanceScore / max(tdp, 1)
    scaledEfficiency = featureScaling(perfPerWatt, 15, 900, 100)
    tdpPenalty = exponentialDecay(tdp, 0.003)
    scoreEfficiency = max(0, min(100, round(scaledEfficiency * tdpPenalty)))

    memoryHeadroom = tanhSigmoidScaling(memoryGb, 10, 5)
    memoryTypeBonus = featureScaling(memoryTypeScore, 1, 4, 100)
    scoreUpgradeability = max(0, min(100, round((memoryHeadroom * 0.6) + (memoryTypeBonus * 0.4))))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignPsuScore(specs):
    wattage = specs["wattage"]
    efficiencyRating = specs["efficiencyRating"]
    modular = specs["modular"]

    wattageScore = featureScaling(wattage, 300, 1600, 60)
    effScore = efficiencyMap.get(str(efficiencyRating).lower(), 10)
    performanceEfficiencyScore = effScore["performance"]
    efficiencyEfficiencyScore = effScore["efficiency"]
    normalScore = max(0, min(100, round(wattageScore + performanceEfficiencyScore)))

    efficiencyNormalized = efficiencyEfficiencyScore

    tdpPenalty = exponentialDecay(wattage, 0.0015)
    scoreEfficiency = max(0, min(100, round(efficiencyNormalized * tdpPenalty)))

    wattageUpgrade = tanhSigmoidScaling(wattage, midpoint=850, scaleFactor=300)
    modularUpgrade = 100 if modular else 50
    scoreUpgradeability = max(0, min(100, round((wattageUpgrade * 0.6) + (modularUpgrade * 0.4))))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignStorageScore(specs):
    capacity = specs["capacityGb"]
    readSpeed = specs["readSpeed"]
    writeSpeed = specs["writeSpeed"]
    avgSpeed = (readSpeed + writeSpeed) // 2

    speedScore = featureScaling(avgSpeed, 100, 7000, 70)
    capacityScore = featureScaling(capacity, 256, 4000, 30)
    normalScore = max(0, min(100, round(speedScore + capacityScore)))

    scoreEfficiency = 0

    capacityUpgrade = tanhSigmoidScaling(capacity, midpoint=2000, scaleFactor=1000)
    speedUpgrade = tanhSigmoidScaling(avgSpeed, midpoint=3500, scaleFactor=1750)
    scoreUpgradeability = max(0, min(100, round((capacityUpgrade + speedUpgrade) / 2)))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignCaseScore(specs):
    formFactor = specs["formFactorSupport"]
    gpuMaxLength = specs["gpuMaxLength"]

    formFactorScore = formFactorWeights.get(formFactor, 2)
    gpuClearanceScore = tanhSigmoidScaling(gpuMaxLength, 350, 100)
    normalScore = max(0, min(100, round((formFactorScore / 4 * 40) + (gpuClearanceScore * 0.6))))

    scoreEfficiency = 0

    formFactorUpgrade = tanhSigmoidScaling(formFactorScore * 25, 75, 25)  # scaled to 0–100
    gpuUpgrade = gpuClearanceScore  # already scaled to 0–100
    scoreUpgradeability = max(0, min(100, round((formFactorUpgrade + gpuUpgrade) / 2)))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignMotherBoardScore(specs):
    ramSlots = specs["memorySlots"]
    maxMemory = specs["maxMemory"]

    ramScore = featureScaling(ramSlots, 2, 8, 40)
    memoryCapacityScore = featureScaling(maxMemory, 32, 192, 60)
    normalScore = max(0, min(100, round(ramScore + memoryCapacityScore)))

    scoreEfficiency = 0

    ramUpgrade = tanhSigmoidScaling(ramSlots, midpoint=4, scaleFactor=2)
    memoryUpgrade = tanhSigmoidScaling(maxMemory, midpoint=128, scaleFactor=64)
    scoreUpgradeability = max(0, min(100, round((ramUpgrade + memoryUpgrade) / 2)))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def normaliseEfficiencyRating(efficiencyString):
    if not efficiencyString or not isinstance(efficiencyString, str):
        return "na"

    rating = efficiencyString.lower().replace("+", "").replace("-", "").strip()

    # Handle 80 Plus ratings
    if "80 plus" in rating or "80plus" in rating:
        if "gold" in rating:
            return "gold"
        elif "silver" in rating:
            return "silver"
        elif "bronze" in rating:
            return "bronze"
        elif "platinum" in rating or "titanium" in rating:
            return "platinum"
        else:
            return "na"

    if "eta" in rating: #Apparently for New PSUs there's some cybenetics efficiency rating system also now
        if "gold" in rating:
            return "gold"
        elif "silver" in rating:
            return "silver"
        elif "bronze" in rating:
            return "bronze"
        elif "platinum" in rating or "titanium" in rating:
            return "platinum"
        else:
            return "na"

    # For the robustness innit
    return "na"

def normaliseReadWriteOrRpm(speed):
    value = speed.strip().lower()
    if "rpm" in value:
        readOrWrite = round(float("".join(n for n in value if n.isdigit())), 0)
        return readOrWrite * 0.025  # multiplication factor to approximate MB/s
    else:
        return int(''.join(n for n in value if n.isdigit()))

def tanhSigmoidScaling(attribute, midpoint, scaleFactor):
    score = (math.tanh((attribute - midpoint) / scaleFactor) + 1) / 2 *100 #add 1 divide by 2 adjusts the range of the tanh(x) graph from -1->1 to 0 --> 1
    return score #Midpoint is like the average value of that attribute. The scale factor is how steep the curve is, so if there is a steeper curve, greater increase in score for same increment

def exponentialDecay(value, decayRate):
    return math.exp(-decayRate * value)

def featureScaling(value, minValue, maxValue, maxScore): #MaxScore is like the proportion of the total that this specific thing will get, so if 50, accounts for 50% of the score's weighting
    if value <= minValue:
        return 0
    if value >= maxValue:
        return maxScore
    return ((value - minValue) / (maxValue - minValue)) * maxScore