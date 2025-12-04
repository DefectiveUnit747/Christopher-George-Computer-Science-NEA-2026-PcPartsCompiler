import math

gpuMemoryTypeScore = {
    "GDDR5": 1,
    "GDDR6": 2,
    "GDDR6X": 3,
    "GDDR7": 4
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
        "memoryType": specs["memoryType"]
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
        "readSpeed": normaliseReadWriteOrRpm(specs["readSpeed"]),
        "writeSpeed": normaliseReadWriteOrRpm(specs["writeSpeed"])
    }
    return assignStorageScore(normalisedSpecs)

def normaliseGpuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score): #FIX THE CORECLOCK ONE
    print(specs)
    mem = int(specs["memoryGb"].split(" ")[0])
    memInGb = (math.floor(mem / 10 ** (math.floor(math.log10(mem)) - 1)) * 10 ** (math.floor(math.log10(mem)) - 1))//1000
    coreClockBeforeNormalisation = specs["coreClock"].split(" ")
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

def assignCpuScore(specs, maximum = 50):
    normalScore = round(((math.log1p(specs["coreCount"]**0.8 + specs["coreClock"]**1.2)) / math.log1p(maximum)) * 100)
    scoreEfficiency = normalScore / specs["tdpWatts"]
    scoreEfficiency = round(scoreEfficiency * math.e**(-0.002 * specs["tdpWatts"]) / math.log1p(maximum) * 100)
    sigmoidCoreCount = tanhSigmoidScaling(specs["coreCount"], 8, 4)
    sigmoidCache = tanhSigmoidScaling(specs["cache"], 16, 8)
    scoreUpgradeability = round(harmonicMean([sigmoidCoreCount, sigmoidCache]))
    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignRamScore(specs, maximum = 5000000):
    normalScore = round((math.log1p(specs["capacityGb"] * specs["speedMhz"]) / math.log1p(maximum)) * 100)
    scoreEfficiency = 0
    moduleScore = 100 - (specs["numberOfModules"] * 25)
    capacityScore = tanhSigmoidScaling(specs["capacityGb"], 32, 16)
    scoreUpgradeability = round(harmonicMean([max(moduleScore, 10), capacityScore]))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignGpuScore(specs, maximum = 1000000):
    memScore = gpuMemoryTypeScore.get(specs["memoryType"], 0)
    rawScore = specs["memoryGb"] * specs["coreClock"] + memScore * 1000
    normalScore = round((math.log1p(rawScore) / math.log1p(maximum)) * 100)
    perfPerWatt = rawScore / specs["tdpWatts"]
    scoreEfficiency = round(min((perfPerWatt) * math.exp(-0.005 * specs["tdpWatts"]), 100))
    memoryScore = tanhSigmoidScaling(specs["memoryGb"], 12, 6)
    memTypeScore = memScore * 20
    scoreUpgradeability = round(harmonicMean([memoryScore, memTypeScore]))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignPsuScore(specs, maximum = 20000):
    efficiencyMap = {
        "na": 1,
        "Bronze": 2,
        "Silver": 3,
        "Gold": 4,
        "Platinum": 5,
        "Titanium": 6
    }
    efficiencyRating = efficiencyMap.get(specs["efficiencyRating"].lower(), 1)
    normalScore = round((math.log1p(specs["wattage"]) / math.log1p(maximum)) * 100)
    scoreEfficiency = round(efficiencyRating * 16.67)

    wattageScore = tanhSigmoidScaling(specs["wattage"], 750, 200)
    modularScore = 100 if specs["modular"] else 50  # modular = easier cable management
    scoreUpgradeability = round(harmonicMean([wattageScore, modularScore]))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignStorageScore(specs, maximum = 1000000):
    capacity = specs["capacityGb"]
    read_speed = specs["readSpeed"]
    write_speed = specs["writeSpeed"]

    rawScore = capacity * 0.5 + (read_speed + write_speed) * 0.25
    normalScore = round((math.log1p(rawScore) / math.log1p(maximum)) * 100)
    scoreEfficiency = 0

    capacityScore = tanhSigmoidScaling(capacity, 2000, 1000)
    speedScore = tanhSigmoidScaling((read_speed + write_speed) / 2, 3000, 1500)
    scoreUpgradeability = round(harmonicMean([capacityScore, speedScore]))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignCaseScore(specs):
    formFactorWeights = {
        "E-ATX": 4,
        "ATX": 3,
        "Micro ATX": 2,
        "Mini ITX": 1
    }
    formFactorScore = formFactorWeights.get(specs["formFactorSupport"], 2)

    normalScore = round(formFactorScore * 20 + specs["gpuMaxLength"] * 0.15)

    scoreEfficiency = 0

    formFactorUpgrade = formFactorScore * 25
    gpuClearanceScore = tanhSigmoidScaling(specs["gpuMaxLength"], 350, 100)
    scoreUpgradeability = round(harmonicMean([formFactorUpgrade, gpuClearanceScore]))

    specs["score"] = normalScore
    specs["scoreEfficiency"] = scoreEfficiency
    specs["scoreUpgradeability"] = scoreUpgradeability
    return specs

def assignMotherBoardScore(specs, maximum=100):
    memoryScore = specs["memorySlots"] * 10
    connectivityScore = (specs.get("pcieSlots", 0) * 5 +
                         specs.get("m2Slots", 0) * 10 +
                         specs.get("sataPorts", 0) * 2)
    normalScore = round(min(memoryScore + connectivityScore, 100))

    scoreEfficiency = 0

    ramSlotScore = tanhSigmoidScaling(specs["memorySlots"], 4, 2)
    expansionScore = tanhSigmoidScaling(specs.get("m2Slots", 0), 3, 1.5)
    scoreUpgradeability = round(harmonicMean([ramSlotScore, expansionScore]))

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
    score = (math.tanh((attribute - midpoint) / scaleFactor)+1)/2 *100 #add 1 divide by 2 adjusts the range of the tanh(x) graph from -1->1 to 0 --> 1
    return score #Midpoint is like the average value of that attribute. The scale factor is how steep the curve is, so if there is a steeper curve, greater increase in score for same increment

def harmonicMean(attributes):
    return len(attributes) / sum(1.0/x for x in attributes)