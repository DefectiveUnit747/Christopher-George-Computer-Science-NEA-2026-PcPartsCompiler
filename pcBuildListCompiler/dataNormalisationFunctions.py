import math

memory_type_score = {
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
        "coreCount": int(specs["coreCount"].split(" ")[0]),
        "coreClock": float(specs["coreClock"].split(" ")[0]),
        "boostClock": float(specs["coreClock"].split(" ")[0]),
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
        "memoryGb": memInGb,
        "coreClock": coreClock,
        "memoryType": specs["memoryType"],
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
        "wattage": int(specs["wattage"].split(" ")[0]),
        "efficiencyRating": efficiency,
        "formFactor": specs["formFactor"],
        "modular": modular
    }
    return assignPsuScore(normalisedSpecs)

def assignCpuScore(specs):
    score = specs["coreClock"] * specs["coreCount"]
    specs["score"] = score
    return specs

def assignRamScore(specs):
    score = specs["capacityGb"] * specs["speedMhz"]
    specs["score"] = score
    return specs

def assignGpuScore(specs):
    mem_score = memory_type_score.get(specs["memoryType"], 0)
    score = (
            specs["memoryGb"] * specs["coreClock"] +
            mem_score * 1000
    )
    specs["score"] = score
    return specs

def assignPsuScore(specs):
    efficiencyMap = {
        "na": 0,
        "bronze": 1,
        "silver": 2,
        "gold": 3,
        "platinum": 4,
        "titanium": 5
    }
    efficiency_score = efficiencyMap.get(specs["efficiencyRating"], 0)
    score = specs["wattage"] * efficiency_score
    specs["score"] = score
    return specs

def assignStorageScore(specs):
    capacity = specs["capacityGb"]
    read = specs["readSpeed"]
    write = specs["writeSpeed"]
    price = specs["price"]

    # Weighted scoring formula
    score = (
            capacity * 0.3 +
            (read + write) * 0.2 -
            price * 0.1
    )

    specs["score"] = round(score, 2)
    return specs

def assignCaseScore(specs):
    formFactorWeights = {
        "E-ATX": 3,
        "ATX": 2,
        "Micro ATX": 1.5,
        "Mini ITX": 1
    }
    formFactorScore = formFactorWeights.get(specs["formFactorSupport"], 1)
    gpuScore = specs["gpuMaxLength"] / 10  # scale down length to keep numbers reasonable
    pricePenalty = specs["price"] * 0.05   # higher price reduces score

    score = formFactorScore * 100 + gpuScore - pricePenalty
    specs["score"] = round(score, 2)
    return specs

def assignMotherBoardScore(specs):
    score = 0
    specs["score"] = score
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
