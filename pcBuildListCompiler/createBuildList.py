from tempPartsAndRequirementsDicts import partsDb, eldenRingMinimum
import pprint

partsCategories = list(partsDb.keys())

compatibilityCache = {} #for memoisation,
budget = 1200
"""
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
    #Filter cases compatible with both motherboard and GPU
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

def getPrice(component):
    return component["price"]

def getTotalBuildScore(build):
    pass

def dfs(budget, partsDB):
    componentOrder = ["GPU", "CPU", "Motherboard", "RAM", "Storage", "PSU"]
    stack = [({}, 0, budget)] #stack items represented as: dictionary of current chosen parts, component index in the list above, budget left

    def search(build, index, budgetLeft):
        if index >= len(componentOrder):
            if meetsRequirements(build["cpu"], build["gpu"], build["ram"], build["storage"]):
                return build, getTotalBuildScore(build)
bestBuild, price = dfs(1200, partsDb)
pprint.pprint(bestBuild)
print(f"This build costs £{price}")
"""

