import random
import time

from bs4 import BeautifulSoup

from pcBuildListCompiler.databasing.createDatabase import *
from pcBuildListCompiler.scrapingTools.dataNormalisationFunctions import *
from pcBuildListCompiler.scrapingTools.scraper import Scraper
from pcBuildListCompiler.databasing.createDatabase import Database
import logging

logger = logging.getLogger(__name__)


manufacturers = [
    "ADATA", "Aerocool", "AMD", "Antec", "ASRock", "ASUS", "be quiet!", "Biostar",
    "CaseLabs", "CiT", "Colorful", "Cooler Master", "Corsair", "Cougar", "Crucial", "CWT",
    "Deepcool", "ECS", "Enermax", "EVGA", "Foxconn", "Fractal", "Gainward",
    "GALAX", "Gigabyte", "G.Skill", "HAVN", "HIS", "Hyte", "Hitachi", "In Win", "Inno3D", "Intel",
    "Kingston", "Lian Li", "Matrox", "Montech", "MSI", "Mushkin", "NVIDIA", "NZXT", "Palit",
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

            "gpu": {
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
                "Storage Type": "formFactor"
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

computerParts = Database()
computerParts.createDatabaseTables()
computerParts.addInManufacturers(manufacturers)
manufacturerMap = computerParts.getManufacturerMap()

ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(ROOT_DIRECTORY, "computerParts.db")

class ComponentScraper(Scraper):
    def __init__(self, baseUrl, database):
        logger.info("Initialising component scraper")
        super().__init__(baseUrl, "")
        self.database = database
        self.manufacturerMap = self.database.getManufacturerMap()
        logger.info("Loaded %d manufacturers into map", len(self.manufacturerMap))

    def genericComponentScraper(self, normalisationFunction, componentTableName):
        logger.info("Starting scrape for component type '%s'", componentTableName)

        try:
            links = self.getProductLinks()
            logger.info("Found %d product links for %s", len(links), componentTableName)

            counter = 0
            for componentLink in links:
                try:
                    counter += 1
                    logger.info("[%d/%d] Scraping %s", counter, len(links), componentLink)

                    self.driver.get(componentLink)
                    time.sleep(random.uniform(10, 20))
                    time.sleep(5)

                    soup = BeautifulSoup(self.driver.page_source, "html.parser")

                    name, partNumber, price, url = self.getNameNumberPriceUrl(componentLink, soup)

                    if not name or not partNumber or not price:
                        logger.warning("Missing info for %s — skipping", componentLink)
                        continue

                    specs = self.extractFromSpecsTable(fieldMapping, soup, componentTableName)

                    if not specs or None in specs.values():
                        logger.warning("Specs missing or incomplete for %s — skipping", partNumber)
                        continue

                    manufacturerId = self.manufacturerMap.get(specs.get("manufacturer", "").lower())
                    if not manufacturerId:
                        logger.warning("Unknown manufacturer '%s' for part %s — skipping",
                                       specs.get("manufacturer"), partNumber)
                        continue

                    score = 0
                    normalisedComponent = normalisationFunction(
                        specs, name, manufacturerId, partNumber, price, url, score
                    )

                    imageFolder = componentImageFolders.get(componentTableName)
                    imagePath = self.downloadPartImage(soup, partNumber, imageFolder)

                    if imagePath:
                        normalisedComponent["imagePath"] = imagePath
                        logger.info("Image saved for %s", partNumber)
                    else:
                        logger.warning("No image saved for %s", partNumber)

                    self.database.insertComponent(componentTableName, normalisedComponent)
                    logger.info("Inserted %s into table '%s'", partNumber, componentTableName)

                    if counter % 5 == 0:
                        extraDelay = random.uniform(3, 15)
                        logger.info("Cooling down for %.0f seconds", extraDelay)
                        time.sleep(extraDelay)

                except Exception as e:
                    logger.error("Error scraping %s: %s", componentLink, e)
                    continue

        except Exception as e:
            logger.critical("Fatal error in genericComponentScraper for %s: %s",
                            componentTableName, e)
            raise e

    def cpuScraping(self):
        logger.info("Starting CPU scraping")
        self.driver = self._initialiseDriver()
        self.categoryUrl = finalFullComponentMap["cpu"]["categoryUrl"]
        self.genericComponentScraper(normaliseCpuScrapedValues, "cpu")

    def gpuScraping(self):
        logger.info("Starting GPU scraping")
        self.driver = self._initialiseDriver()
        self.categoryUrl = finalFullComponentMap["gpu"]["categoryUrl"]
        self.genericComponentScraper(normaliseGpuScrapedValues, "gpu")

    def ramScraping(self):
        logger.info("Starting RAM scraping")
        self.driver = self._initialiseDriver()
        self.categoryUrl = finalFullComponentMap["ram"]["categoryUrl"]
        self.genericComponentScraper(normaliseRamScrapedValues, "ram")

    def psuScraping(self):
        logger.info("Starting PSU scraping")
        self.driver = self._initialiseDriver()
        self.categoryUrl = finalFullComponentMap["psu"]["categoryUrl"]
        self.genericComponentScraper(normalisePsuScrapedValues, "psu")

    def storageScraping(self):
        logger.info("Starting storage scraping")
        for url in finalFullComponentMap["storage"]["categoryUrl"]:
            self.driver = self._initialiseDriver()
            self.categoryUrl = url
            self.genericComponentScraper(normaliseStorageScrapedValues, "storage")

    def caseScraping(self):
        logger.info("Starting case scraping")
        self.driver = self._initialiseDriver()
        self.categoryUrl = finalFullComponentMap["cases"]["categoryUrl"]
        self.genericComponentScraper(normaliseCaseScrapedValues, "cases")

    def motherboardScraping(self):
        logger.info("Starting motherboard scraping")
        self.driver = self._initialiseDriver()
        self.categoryUrl = finalFullComponentMap["motherboard"]["categoryUrl"]
        self.genericComponentScraper(normaliseMotherboardScrapedValues, "motherboard")

    def scrapeAllComponents(self):
        logger.info("Starting full scrape of all component types")

        for componentType, config in finalFullComponentMap.items():
            try:
                logger.info("Scraping %s", componentType)
                self.driver = self._initialiseDriver()

                if isinstance(config["categoryUrl"], list):
                    for url in config["categoryUrl"]:
                        self.categoryUrl = url
                        self.genericComponentScraper(config["normaliser"], config["table"])
                else:
                    self.categoryUrl = config["categoryUrl"]
                    self.genericComponentScraper(config["normaliser"], config["table"])

                logger.info("%s scraping completed", componentType)

            except Exception as e:
                logger.error("%s scraping failed: %s", componentType, e)

            finally:
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception:
                        logger.warning("Driver quit failed — ignoring")
                    self.driver = None

scraper = ComponentScraper("https://www.cclonline.com", computerParts)
