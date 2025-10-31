import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

baseUrl = "https://www.cclonline.com"
componentLinksToAddOn = ["/pc-components/cpu-processors", "/pc-components/motherboards",
                         "/pc-components/graphics-cards", "/pc-components/cases", "/pc-components/power-supplies",
                         "/storage", "/pc-components/memory/desktop-memory"]

class Scraper:
    def __init__(self, url, categoryUrl):
        self.baseUrl = url
        self.categoryUrl = categoryUrl
        self.driver = self._initialiseDriver()
        self.conn = sqlite3.connect("pcParts.db")
        self.cursor = self.conn.cursor()

    def _initialiseDriver(self):
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        return webdriver.Chrome(options=options)

    def _loadManufacturers(self):
        self.cursor.execute("SELECT manufacturerId, name FROM manufacturer")
        return {
            name.lower(): manufacturerId
            for manufacturerId, name in self.cursor.fetchall()
            if name is not None}

    def getProductLinks(self):
        links = set() #avoids duplicate links

        self.driver.get(self.baseUrl + self.categoryUrl)
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        pageItems = soup.find_all("li", class_="notSelected")
        if len(pageItems) >= 2:
            lastPage = int(pageItems[-2].text.strip())
        else:
            lastPage = 1

        for page in range(1, lastPage + 1):
            cpuLinks = []
            pageUrl = f"{self.baseUrl}{self.categoryUrl}/page_{page}/"
            self.driver.get(pageUrl)
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            cpuList = soup.find_all("div", class_="productListContainer")
            for item in cpuList:
                if item.find("div", id="pnlSoldOut"): #Checks for out of stock items
                    continue  # Skip out-of-stock items
                for link in item.find_all("a", href=True):
                    cpuLinks.append(self.baseUrl + link["href"])
            links.update(cpuLinks)

        return links

    def extractFromSpecsTable(self, fieldMapping, soup, componentType):
        componentMapping = fieldMapping.get(componentType.lower())
        specs = {}
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            label = cells[0].text.strip()
            value = cells[1].text.strip()

            field = componentMapping.get(label)
            if field:  # Only add if label is mapped
                specs[field] = value
        return specs

    def getNameNumberPriceUrl(self, link, soup):
        time.sleep(1)
        url = link
        nameTag = soup.find("span", class_="px-0")
        name = nameTag.text.strip() if nameTag else None
        print(name)

        partTag = soup.find("div", id="pnlPartNumber", class_="partnumber")
        partNumber = partTag.find("h2").text.strip() if partTag else None
        print(partNumber)
        priceContainer = soup.find("div", id="pnlPriceText", class_="price")
        if not priceContainer:
            return None, None, None, link

        price = float("".join(span.text for span in priceContainer.find_all("span")[:3]).replace("£", "").replace(",", ""))
        print(price)
        return name, partNumber, price, url

