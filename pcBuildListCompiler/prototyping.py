# Small test dataset for algorithm testing
validPartsDict = {
    "gpu": [
        ("RTX-4060", {
            "partNumber": "RTX-4060",
            "name": "NVIDIA GeForce RTX 4060 8GB",
            "price": 299.99,
            "manufacturerId": 40,
            "url": "https://www.cclonline.com/product/rtx-4060",
            "tdpWatts": 115,
            "lengthMm": 244.0,
            "imagePath": "productImages/gpuImages/RTX-4060.jpg",
            "finalScore": 650.5,
            "memoryGb": 8,
            "coreClock": 2460,
            "memoryType": "GDDR6"
        }),
        ("RX-7600", {
            "partNumber": "RX-7600",
            "name": "AMD Radeon RX 7600 8GB",
            "price": 269.99,
            "manufacturerId": 3,
            "url": "https://www.cclonline.com/product/rx-7600",
            "tdpWatts": 165,
            "lengthMm": 240.0,
            "imagePath": "productImages/gpuImages/RX-7600.jpg",
            "finalScore": 620.3,
            "memoryGb": 8,
            "coreClock": 2250,
            "memoryType": "GDDR6"
        }),
        ("RTX-3060", {
            "partNumber": "RTX-3060",
            "name": "NVIDIA GeForce RTX 3060 12GB",
            "price": 289.99,
            "manufacturerId": 40,
            "url": "https://www.cclonline.com/product/rtx-3060",
            "tdpWatts": 170,
            "lengthMm": 242.0,
            "imagePath": "productImages/gpuImages/RTX-3060.jpg",
            "finalScore": 580.2,
            "memoryGb": 12,
            "coreClock": 1777,
            "memoryType": "GDDR6"
        })
    ],
    "cpu": [
        ("R5-7600", {
            "partNumber": "R5-7600",
            "name": "AMD Ryzen 5 7600 6-Core",
            "price": 199.99,
            "manufacturerId": 2,
            "url": "https://www.cclonline.com/product/r5-7600",
            "socketId": "AM5",
            "tdpWatts": 65,
            "imagePath": "productImages/cpuImages/R5-7600.jpg",
            "finalScore": 545.8,
            "coreCount": 6,
            "coreClock": 3.8,
            "cache": 32,
            "threads": 12
        }),
        ("I5-12400F", {
            "partNumber": "I5-12400F",
            "name": "Intel Core i5-12400F 6-Core",
            "price": 149.99,
            "manufacturerId": 29,
            "url": "https://www.cclonline.com/product/i5-12400f",
            "socketId": "LGA1700",
            "tdpWatts": 117,
            "imagePath": "productImages/cpuImages/I5-12400F.jpg",
            "finalScore": 510.5,
            "coreCount": 6,
            "coreClock": 2.5,
            "cache": 18,
            "threads": 12
        }),
        ("R5-5600", {
            "partNumber": "R5-5600",
            "name": "AMD Ryzen 5 5600 6-Core",
            "price": 129.99,
            "manufacturerId": 2,
            "url": "https://www.cclonline.com/product/r5-5600",
            "socketId": "AM4",
            "tdpWatts": 65,
            "imagePath": "productImages/cpuImages/R5-5600.jpg",
            "finalScore": 485.0,
            "coreCount": 6,
            "coreClock": 3.5,
            "cache": 32,
            "threads": 12
        })
    ],
    "motherboard": [
        ("B650-PRO", {
            "partNumber": "B650-PRO",
            "name": "Gigabyte B650 Gaming X",
            "price": 179.99,
            "manufacturerId": 23,
            "url": "https://www.cclonline.com/product/b650-pro",
            "socketId": "AM5",
            "formFactor": "ATX",
            "tdpWatts": 25,
            "memorySlots": 4,
            "memoryType": "DDR5",
            "maxMemory": 128,
            "imagePath": "productImages/motherboardImages/B650-PRO.jpg",
            "finalScore": 445.3
        }),
        ("B660M-GAMING", {
            "partNumber": "B660M-GAMING",
            "name": "MSI B660M Gaming WiFi",
            "price": 139.99,
            "manufacturerId": 33,
            "url": "https://www.cclonline.com/product/b660m-gaming",
            "socketId": "LGA1700",
            "formFactor": "Micro ATX",
            "tdpWatts": 25,
            "memorySlots": 4,
            "memoryType": "DDR4",
            "maxMemory": 128,
            "imagePath": "productImages/motherboardImages/B660M-GAMING.jpg",
            "finalScore": 410.7
        }),
        ("B550M-PLUS", {
            "partNumber": "B550M-PLUS",
            "name": "ASUS TUF B550M-PLUS",
            "price": 119.99,
            "manufacturerId": 4,
            "url": "https://www.cclonline.com/product/b550m-plus",
            "socketId": "AM4",
            "formFactor": "Micro ATX",
            "tdpWatts": 20,
            "memorySlots": 4,
            "memoryType": "DDR4",
            "maxMemory": 128,
            "imagePath": "productImages/motherboardImages/B550M-PLUS.jpg",
            "finalScore": 385.2
        })
    ]
}

componentOrder = ["cpu", "gpu", "motherboard"]  # removed "ram" for now
budget = 1000

def calculateTotalScore(build):
    total = 0
    for key, value in build.items():
        if value:
            total += value["finalScore"]
    return total

def calculateTotalPrice(build):
    total = 0
    for key, value in build.items():
        if value:
            total += value["price"]

    return total

def isCpuCompatibleWithMotherboard(cpu, motherboard):
    return cpu["socketId"] == motherboard["socketId"]

def depthFirstSearch(level, currentBuild, currentPrice, bestBuild):
    if level == len(componentOrder):
        # evaluate final score
        score = calculateTotalScore(currentBuild)
        if score > bestBuild["score"]:
            bestBuild["score"] = score
            bestBuild["build"] = currentBuild.copy()
        return

    currentType = componentOrder[level]

    for partNumber, part in validPartsDict[currentType]:
        price = part["price"]

        # budget check
        if currentPrice + price > budget:
            continue
        if currentType == "motherboard":
            if not isCpuCompatibleWithMotherboard(currentBuild["cpu"], part):
                continue

        # create a new build state
        newBuild = currentBuild.copy()
        newBuild[currentType] = part

        depthFirstSearch(
            level + 1,
            newBuild,
            currentPrice + price,
            bestBuild
        )

# run it
bestBuild = {"score": 0, "build": {}}
depthFirstSearch(0, {"cpu": None, "gpu": None, "motherboard": None}, 0, bestBuild)

print("Best score:", bestBuild["score"])
print("Best build:", bestBuild["build"])
print(f"Price: {calculateTotalPrice(bestBuild["build"])}")
