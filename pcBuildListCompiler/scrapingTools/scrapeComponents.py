from pcBuildListCompiler.createDatabase import pcParts
from pcBuildListCompiler.scrapingTools.dataNormalisationFunctions import normaliseCpuScrapedValues
from scraper import Scraper
import sqlite3
from bs4 import BeautifulSoup
import time
from dataNormalisationFunctions import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#ADD IN LOGGING

base_url = "https://www.cclonline.com"
category_url = "/pc-components/graphics-cards"

conn = sqlite3.connect('pcParts.db')
cursor = conn.cursor()

cursor.execute("SELECT manufacturerId, name from manufacturer")
manufacturerMap = {
    name.lower(): manufacturerId
    for manufacturerId, name in cursor.fetchall()
    if name is not None}

fieldMapping = {
            "cpu": {
                "CPU Base Speed": "coreClock",
                "CPU Manufacturer": "manufacturer",
                "CPU Base TDP": "tdp",
                "Cache": "cache",
                "Socket": "socket",
                "Number of Cores": "coreCount"
            },

            "motherboard": {
                "Manufacturer": "manufacturer",
                "Power Requirement (auto)": "tdp",
                "Socket": "socket",
                "Motherboard Form Factor": "formFactor",
                "Memory Slot": "memorySlots",
                "Memory Type": "memoryType"
            },

            "gpu": {
                "Chipset Manufacturer": "manufacturer",
                "Memory Size": "memoryGb",
                "Memory Type": "memoryType",
                "Depth": "length",
                "Number of Cores": "coreCount",
                "Power Consumption": "tdp",
                "Base Chip Clock": "coreClock",
            },

            "psu": {
                "Manufacturer": "manufacturer",
                "Power": "wattage",
                "80Plus Rated": "efficiencyRating",
                "PSU Form Factor": "formFactor",
            },

            "pcCase": {
                "Manufacturer": "manufacturer",
                "Maximum Motherboard Size Supported": "formFactorSupport",
                "GPU Length": "gpuMaxLength",
            },

            "storage": {
                "Manufacturer": "manufacturer",
                "Drive Capacity": "capacityGb",
                "Read Speed": "readSpeed",
                "Write Speed": "writeSpeed",
            },

            "ram": {
                "Manufacturer": "manufacturer",
                "Memory Size": "capacityGb",
                "Memory DIMM Count": "numberOfModules",
                "Memory Speed": "speedMhz",
                "Memory Type": "ddrType",
            }
        }

class componentScraper(Scraper):
    def __init__(self, componentName, categoryUrl, manufacturerMap):
        super().__init__("https://www.cclonline.com", categoryUrl)
        self.componentName = componentName.lower()
        self.manufacturerMap = manufacturerMap
        self.database = pcParts
        self.manufacturerMap - pcParts.getManufacturerMap()

    def cpuScraping(self):
        cpuLinks = self.getProductLinks()
        for cpuLink in cpuLinks:
            self.driver.get(cpuLink)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            name, partNumber, price, url = self.getNameNumberPriceUrl(cpuLink, soup)
            specs = self.extractFromSpecsTable(fieldMapping, soup, self.componentName)
            manufacturerId = self.manufacturerMap.get(specs.get("manufacturer").lower()) if specs.get("manufacturer") else None
            score = 0
            cpu = normaliseCpuScrapedValues(specs, name, manufacturerId, partNumber, price, url, score)
            pcParts.insertComponent("cpu", cpu)

    def motherboardScraping(self):
        motherboardLinks = self.getProductLinks()
        for motherboardLink in motherboardLinks:
            self.driver.get(motherboardLink)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            name, partNumber, price, url = self.getNameNumberPriceUrl(motherboardLink, soup)
            specs = self.extractFromSpecsTable(fieldMapping, soup, self.componentName)
            manufacturerId = self.manufacturerMap.get(specs.get("manufacturer").lower()) if specs.get("manufacturer") else None
            motherboard = normaliseMotherboardScrapedValues(specs, name, manufacturerId, partNumber, price, url, 0)
            pcParts.insertComponent("motherboard", motherboard)

    def memoryScraping(self):
        memoryLinks = self.getProductLinks()
        for memoryLink in memoryLinks:
            self.driver.get(memoryLink)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            name, partNumber, price, url = self.getNameNumberPriceUrl(memoryLink, soup)
            specs = self.extractFromSpecsTable(fieldMapping, soup, self.componentName)
            manufacturerId = self.manufacturerMap.get(specs.get("manufacturer").lower()) if specs.get("manufacturer") else None
            ramKit = normaliseRamScrapedValues(specs, name, manufacturerId, partNumber, price, url, 0)
            pcParts.insertComponent("memory", ramKit)

    def gpuScraping(self):
        gpuLinks = self.getProductLinks()
        for gpuLink in gpuLinks:
            self.driver.get(gpuLink)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            name, partNumber, price, url = self.getNameNumberPriceUrl(gpuLink, soup)
            specs = self.extractFromSpecsTable(fieldMapping, soup, self.componentName)
            manufacturerId = self.manufacturerMap.get(specs.get("manufacturer").lower()) if specs.get("manufacturer") else None
            gpu = normaliseGpuScrapedValues(specs, name, manufacturerId, partNumber, price, url, 0)
            pcParts.insertComponent("gpu", gpu)

    def powerSupplyScraping(self):
        powerSupplyLinks = self.getProductLinks()
        for powerSupplyLink in powerSupplyLinks:
            self.driver.get(powerSupplyLink)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            name, partNumber, price, url = self.getNameNumberPriceUrl(powerSupplyLink, soup)
            specs = self.extractFromSpecsTable(fieldMapping, soup, self.componentName)
            manufacturerId = self.manufacturerMap.get(specs.get("manufacturer").lower()) if specs.get("manufacturer") else None
            psu = normalisePsuScrapedValues(specs, name, manufacturerId, partNumber, price, url, 0)
            pcParts.insertComponent("psu", psu)

    def caseScraping(self):
        caseLinks = self.getProductLinks()
        for caseLink in caseLinks:
            self.driver.get(caseLink)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            name, partNumber, price, url = self.getNameNumberPriceUrl(caseLink, soup)
            specs = self.extractFromSpecsTable(fieldMapping, soup, self.componentName)
            manufacturerId = self.manufacturerMap.get(specs.get("manufacturer").lower()) if specs.get("manufacturer") else None
            pcCase = normaliseCaseScrapedValues(specs, name, manufacturerId, price, url)
            pcParts.insertComponent("pcCase", pcCase)

    def storageScraping(self):
        storageLinks = self.getProductLinks()
        for storageLink in storageLinks:
            self.driver.get(storageLink)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            name, partNumber, price, url = self.getNameNumberPriceUrl(storageLink, soup)
            specs = self.extractFromSpecsTable(fieldMapping, soup, self.componentName)
            manufacturerId = self.manufacturerMap.get(specs.get("manufacturer").lower()) if specs.get("manufacturer") else None
            storage = normaliseStorageScrapedValues(specs, name, manufacturerId, price, url)
            pcParts.insertComponent("storage", storage)

conn.close()

scraper = componentScraper(
    componentName="gpu",
    categoryUrl=category_url,
    manufacturerMap=manufacturerMap
)

# Call the scraping method
scraper.gpuScraping()