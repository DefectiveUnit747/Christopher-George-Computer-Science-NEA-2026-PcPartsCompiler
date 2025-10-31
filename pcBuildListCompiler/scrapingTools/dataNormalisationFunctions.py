import math

memory_type_score = {
    "GDDR5": 1,
    "GDDR6": 2,
    "GDDR6X": 3,
    "GDDR7": 4
}

def normaliseCpuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "coreCount": int(specs["coreCount"].split(" ")[0]),
        "coreClock": int(specs["coreClock"].split(" ")[0]),
        "tdp": int(specs["tdp"][0]),
        "socket": specs["socket"]}

    return assignCpuScore(normalisedSpecs)

def normaliseMotherboardScrapedValues(specs, name, manufacturerId, partNumber, price, url):
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "socket": specs["socket"],
        "formFactor": specs["formFactor"],
        "tdp": int(specs["tdp"][0]),
        "memorySlots": int(specs["memorySlots"].split(" ")[0]),
        "memoryType": specs["memoryType"]}
    return normalisedSpecs

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
        "speedMHz": int(specs["speedMHz"]),
        "ddrType": specs["ddrType"]}
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
        "readSpeed": float(specs["readSpeed"].replace("Up to ", "").replace(",", "").split()[0]),
        "writeSpeed": float(specs["writeSpeed"].replace("Up to ", "").replace(",", "").split()[0])}
    return assignStorageScore(normalisedSpecs)

def normaliseGpuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    mem = int(specs["memoryGb"].split(" ")[0])
    memInGb = math.floor(mem / 10**(math.floor(math.log10(mem)) - 1)) * 10**(math.floor(math.log10(mem)) - 1)
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "memoryGb": memInGb,
        "coreClock": int(specs["coreClock"].split(" ")[0]),
        "memoryType": specs["memoryType"],
        "tdp": int(specs["tdp"].split(" ")[0]),
        "length": int(specs["length"].split(" ")[0])}
    return assignGpuScore(normalisedSpecs)

def normaliseCaseScrapedValues(specs, name, manufacturerId, partNumber, url, price):
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "formFactorSupport": specs["formFactorSupport"],
        "gpuMaxLength": int(specs["gpuMaxLength"].split(" ")[0])}
    return normalisedSpecs

def normalisePsuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score):
    normalisedSpecs = {
        "partNumber": partNumber,
        "name": name,
        "price": price,
        "manufacturerId": manufacturerId,
        "url": url,
        "score": score,
        "wattage": int(specs["wattage"].split(" ")[0]),
        "efficiencyRating": specs["efficiencyRating"][2],
        "formFactor": specs["formFactor"]}
    return assignPsuScore(normalisedSpecs)

def assignCpuScore(specs):
    score = specs["coreClock"] * specs["coreCount"]
    specs["score"] = score
    return specs

def assignRamScore(specs):
    score = specs["capacityGb"] * specs["speedMHz"]
    specs["score"] = score
    return specs

def assignGpuScore(specs):
    mem_score = memory_type_score.get(specs["memoryType"], 0)
    score = (
        specs["memoryGb"] * specs["coreClock"] +
        mem_score * 1000  # bonus for newer memory tech
    )
    specs["score"] = score
    return specs

def assignPsuScore(specs):
    efficiencyMap = {
        "Bronze": 1,
        "Silver": 2,
        "Gold": 3,
        "Platinum": 4,
        "Titanium": 5
    }
    efficiency_score = efficiencyMap.get(specs["efficiencyRating"], 0)
    score = specs["wattage"] * efficiency_score
    specs["score"] = score
    return specs

def assignStorageScore(specs):
    capacity = specs["capacityGb"]
    read_speed = specs["readSpeed"]
    write_speed = specs["writeSpeed"]
    price = specs["price"]

    # Weighted scoring formula
    score = (
        capacity * 0.3 +               # Capacity matters for storage
        (read_speed + write_speed) * 0.2 -  # Speed matters for performance
        price * 0.1                    # Penalize higher price
    )

    specs["score"] = round(score, 2)
    return specs