from createDatabase import *
from scraper import Scraper
from bs4 import BeautifulSoup
import time
import random
from dataNormalisationFunctions import *
#ADD IN LOGGING

manufacturers = [
    "ADATA", "Aerocool", "AMD", "Antec", "ASRock", "ASUS", "be quiet!", "Biostar",
    "CaseLabs", "Colorful", "Cooler Master", "Corsair", "Cougar", "Crucial",
    "Deepcool", "ECS", "Enermax", "EVGA", "Foxconn", "Fractal Design", "Gainward",
    "GALAX", "Gigabyte", "G.Skill", "HIS", "Hitachi", "In Win", "Inno3D", "Intel",
    "Kingston", "Lian Li", "Matrox", "MSI", "Mushkin", "NVIDIA", "NZXT", "Palit",
    "Patriot", "Phanteks", "Plextor", "PNY", "PowerColor", "Rosewill", "Sapphire",
    "Samsung", "SanDisk", "Seagate", "Seasonic", "SilverStone", "SK Hynix",
    "Super Flower", "Supermicro", "TeamGroup", "Thermaltake", "Toshiba", "VisionTek",
    "Western Digital", "XFX", "Zotac", "Micron", "GameMax"
]
fieldMapping = {
            "cpu": {
                "CPU Base Speed": "coreClock",
                "CPU Manufacturer": "manufacturer",
                "CPU Base TDP": "tdp",
                "Cache": "cache",
                "Socket": "socket",
                "CPU Socket": "socket",
                "Number of Cores": "coreCount",
                "CPU Threads": "threads"
            },

            "motherboard": {
                "Manufacturer": "manufacturer",
                "Power Requirement (auto)": "tdp",
                "Socket": "socket",
                "Motherboard Form Factor": "formFactor",
                "Memory Slot": "memorySlots",
                "Memory Type": "memoryType",
                "Maximum RAM": "maxMemory"
            },

            "gpu": { #Finished
                "Chipset Manufacturer": "manufacturer",
                "Memory Size": "memoryGb",
                "Memory Type": "memoryType",
                "Depth": "length",
                "Number of Cores": "coreCount",
                "Power Consumption": "tdpWatts",
                "12V-2x6 Rating": "tdpWatts",
                "Base Chip Clock": "coreClock",
                "Boost Chip Clock": "coreClock",
                "GPU Length": "length"
            },

            "psu": {
                "Manufacturer": "manufacturer",
                "Power": "wattage",
                "80Plus Rated": "efficiencyRating",
                "PSU Form Factor": "formFactor",
                "Modular Cables": "modularity"
            },

            "cases": {
                "Manufacturer": "manufacturer",
                "Maximum Motherboard Size Supported": "formFactorSupport",
                "GPU Length": "gpuMaxLength",
                "PSU Form Factor": "psuFormFactorSupport"
            },

            "storage": {
                "Manufacturer": "manufacturer",
                "Drive Capacity": "capacityGb",
                "Disk Capacity": "capacityGb",
                "Read Speed": "readSpeed",
                "Write Speed": "writeSpeed",
                "Disk Speed": ["readSpeed", "writeSpeed"],
                "In The Box": "formFactor"
            },

            "ram": {
                "Manufacturer": "manufacturer",
                "Memory Size": "capacityGb",
                "Memory DIMM Count": "numberOfModules",
                "Memory Speed": "speedMhz",
                "Memory Type": "ddrType",
            }
        }
componentImageFolders = {
    "cpu": "cpuImages",
    "gpu": "gpuImages",
    "ram": "ramImages",
    "motherboard": "motherboardImages",
    "psu": "psuImages",
    "storage": "storageImages",
    "cases": "caseImages"
}
finalFullComponentMap = {
    "cpu": {
        "normaliser": normaliseCpuScrapedValues,
        "table": "cpu",
        "categoryUrl": "/pc-components/cpu-processors"
    },
    "gpu": {
        "normaliser": normaliseGpuScrapedValues,
        "table": "gpu",
        "categoryUrl": "/pc-components/graphics-cards"
    },
    "ram": {
        "normaliser": normaliseRamScrapedValues,
        "table": "ram",
        "categoryUrl": "/pc-components/memory/desktop-memory"
    },
    "motherboard": {
        "normaliser": normaliseMotherboardScrapedValues,
        "table": "motherboard",
        "categoryUrl": "/pc-components/motherboards"
    },
    "psu": {
        "normaliser": normalisePsuScrapedValues,
        "table": "psu",
        "categoryUrl": "/pc-components/power-supplies"
    },
    "storage": {
        "normaliser": normaliseStorageScrapedValues,
        "table": "storage",
        "categoryUrl": ["/storage/hard-drives", "/storage/solid-state-drives-ssds"]
    },
    "cases": {
        "normaliser": normaliseCaseScrapedValues,
        "table": "cases",
        "categoryUrl": "/pc-components/cases"
    }
}

computerParts = Database("computerParts.db")
computerParts.createDatabaseTables()
computerParts.addInManufacturers(manufacturers)
manufacturerMap = computerParts.getManufacturerMap()

base_url = "https://www.cclonline.com"

class componentScraper(Scraper):
    def __init__(self, baseUrl, database):
        super().__init__(baseUrl, "")
        self.database = database
        self.manufacturerMap = self.database.getManufacturerMap()

    def genericComponentScraper(self, normalisationFunction, componentTableName):
        try:
            links = self.getProductLinks()
            print(f"Found {len(links)} links")

            counter = 0
            for componentLink in links:
                try:
                    counter += 1
                    print(f"\n[{counter}/{len(links)}] -> {componentLink}")
                    self.driver.get(componentLink)

                    time.sleep(random.uniform(10, 20))
                    time.sleep(5)

                    soup = BeautifulSoup(self.driver.page_source, "html.parser")

                    name, partNumber, price, url = self.getNameNumberPriceUrl(componentLink, soup)

                    if not name or not partNumber or not price:
                        print("  Missing info")
                        continue

                    specs = self.extractFromSpecsTable(fieldMapping, soup, componentTableName)

                    if not specs:
                        print("  No specs")
                        continue

                    manufacturerId = self.manufacturerMap.get(specs.get("manufacturer", "").lower()) if specs.get(
                        "manufacturer") else None
                    score = 0
                    normalisedComponent = normalisationFunction(specs, name, manufacturerId, partNumber, price, url,
                                                                score)
                    imageFolder = componentImageFolders.get(componentTableName)
                    imagePath = self.downloadPartImage(soup, partNumber, imageFolder)
                    if imagePath:
                        normalisedComponent["imagePath"] = imagePath
                    normalisedComponent["imagePath"] = imagePath
                    self.database.insertComponent(componentTableName, normalisedComponent)
                    print(f"  {name}")

                    if counter % 5 == 0:
                        extraDelay = random.uniform(3, 15)
                        print(f"  Cooling down {extraDelay:.0f}s...")
                        time.sleep(extraDelay)

                except Exception as e:
                    print(f"  Error: {e}")
                    continue

        except Exception as e:
            print(f"BAD: {e}")
            raise e

    def cpuScraping(self):
        self.categoryUrl = finalFullComponentMap["cpu"]["categoryUrl"]
        self.genericComponentScraper(normaliseCpuScrapedValues, "cpu")

    def gpuScraping(self):
        self.categoryUrl = finalFullComponentMap["gpu"]["categoryUrl"]
        self.genericComponentScraper(normaliseGpuScrapedValues, "gpu")

    def ramScraping(self):
        self.categoryUrl = finalFullComponentMap["ram"]["categoryUrl"]
        self.genericComponentScraper(normaliseRamScrapedValues, "ram")

    def psuScraping(self):
        self.categoryUrl = finalFullComponentMap["psu"]["categoryUrl"]
        self.genericComponentScraper(normalisePsuScrapedValues, "psu")

    def storageScraping(self):
        for i in finalFullComponentMap["storage"]["categoryUrl"]:
            self.categoryUrl = i
            self.genericComponentScraper(normaliseStorageScrapedValues, "storage")

    def caseScraping(self):
        self.categoryUrl = finalFullComponentMap["cases"]["categoryUrl"]
        self.genericComponentScraper(normaliseCaseScrapedValues, "cases")

    def motherboardScraping(self):
        self.categoryUrl = finalFullComponentMap["motherboard"]["categoryUrl"]
        self.genericComponentScraper(normaliseMotherboardScrapedValues, "motherboard")

    def scrapeAllComponents(self):
        for componentType, config in finalFullComponentMap.items():
            try:
                self.categoryUrl = config["categoryUrl"]
                self.genericComponentScraper(config["normalizer"], config["table"])
            except Exception as e:
                print(f"{componentType} failed: {e}")

scraper = componentScraper("https://www.cclonline.com", computerParts)
scraper.scrapeAllComponents()
scraper.driver = None


#Fix the scraper
#Put all stuff in Database
#Start on build list
