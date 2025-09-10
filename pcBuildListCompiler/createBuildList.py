from tempPartsAndRequirementsDicts import partsDb, eldenRingMinimum
import pprint

partsCategories = list(partsDb.keys())

compatibilityCache = {} #for memoisation,
budget = 1200

def checkPartsCompatibility(part1, part2):
    key = (part1["id"], part2["id"])
    if key in compatibilityCache:
        return compatibilityCache[key]
    result = True

    if "socket" in part1 and "socket" in part2:
        result = part1["socket"] == part2["socket"]

    elif "ram_type" in part1 and "type" in part2:
        result = part1["ram_type"] == part2["type"]

    elif "form_factor_support" in part1 and "form_factor" in part2:
        result = part2["form_factor"] in part1["form_factor_support"]

    elif "gpu_max_length_mm" in part1 and "length_mm" in part2:
        result = part2["length_mm"] <= part1["gpu_max_length_mm"]

    compatibilityCache[key] = result
    return result

def filterMobos(cpu, partsDB):
    allCompatibleMobos = []
    for mobo in partsDB["Motherboard"]:
        if checkPartsCompatibility(cpu, mobo):
            allCompatibleMobos.append(mobo)
    return allCompatibleMobos

def filterRAM(motherboard, partsDB):
    allCompatibleRAM = []
    for ramKit in partsDB["RAM"]:
        if checkPartsCompatibility(motherboard, ramKit):
            allCompatibleRAM.append(ramKit)
    return allCompatibleRAM

def filterCase(mobo, gpu, partsDB):
    """Filter cases compatible with both motherboard and GPU"""
    allCompatibleCases = []
    for case in partsDB["Case"]:
        if (checkPartsCompatibility(mobo, case) and checkPartsCompatibility(gpu, case)):
            allCompatibleCases.append(case)
    return allCompatibleCases

def meetsRequirements(cpu, gpu, ram, storage):
    return (
        cpu["score"] >= eldenRingMinimum["CPU"]["score"] and
        gpu["score"] >= eldenRingMinimum["GPU"]["score"] and
        ram["capacity_gb"] >= eldenRingMinimum["RAM"]["required_gb"] and
        storage["capacity_gb"] >= eldenRingMinimum["Storage"]["required_gb"]
    )

def dfs(budget, partsDB):
    componentOrder = ["CPU", "Motherboard", "RAM", "GPU", "Storage", "PSU", "Case"]
    bestBuild = None
    bestScore = 0

    def getPrice(component):
        return component["price"]
    for componentType in partsDB:
        partsDB[componentType].sort(key=getPrice)

    def search(currentBuild, currentComponentType, budgetLeft):
        if currentComponentType >= len(componentOrder):
            cpu, gpu = currentBuild["CPU"], currentBuild["GPU"]
            ram, storage = currentBuild["RAM"], currentBuild["Storage"]

            if meetsRequirements(cpu, gpu, ram, storage):
                totalScore = cpu["score"] + gpu["score"]
                return currentBuild.copy(), totalScore
            return None, 0

        componentType = componentOrder[currentComponentType]
        candidates = findSuitableComponents(currentBuild, componentType)

        bestBuild = None
        bestScore = 0

        for component in candidates:
            if component["price"] > budgetLeft:
                break

            currentBuild[componentType] = component
            foundBuild, foundScore = search(currentBuild, currentComponentType + 1, budgetLeft - component["price"])

            if foundScore > bestScore:
                bestScore = foundScore
                bestBuild = foundBuild

            del currentBuild[componentType]

        return bestBuild, bestScore

    def findSuitableComponents(currentBuild, componentType):
        if componentType == "Motherboard" and "CPU" in currentBuild:
            return filterMobos(currentBuild["CPU"], partsDb)

        if componentType == "RAM" and "Motherboard" in currentBuild:
            return filterRAM(currentBuild["Motherboard"], partsDb)

        if componentType == "Case" and "Motherboard" in currentBuild and "GPU" in currentBuild:
            return filterCase(currentBuild["Motherboard"], currentBuild["GPU"], partsDb)

        return partsDb[componentType]

    bestBuild, bestScore = search({}, 0, budget)
    sum = 0
    for component in bestBuild.values():
        sum += (component["price"])

    return bestBuild, sum

bestBuild, price = dfs(1200, partsDb)
pprint.pprint(bestBuild)
print(f"This build costs £{price}")