import time
import io
import requests
from PIL import Image
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import logging
import os

baseUrl = "https://www.cclonline.com"
componentLinksToAddOn = ["/pc-components/cpu-processors", "/pc-components/motherboards",
                         "/pc-components/graphics-cards", "/pc-components/cases", "/pc-components/power-supplies",
                         "/storage", "/pc-components/memory/desktop-memory"]

class Scraper:
    def __init__(self, url, categoryUrl):
        self.baseUrl = url
        self.categoryUrl = categoryUrl
        self.driver = self._initialiseDriver()
        self.requestSession = None

    def _initialiseDriver(self):
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = uc.Chrome(options=options)
        return driver

    def initialiseRequestSession(self):
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])

        session.headers.update({
            "User-Agent": self.driver.execute_script("return navigator.userAgent;"),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.cclonline.com/"
        })

        self.requests_session = session

    def getProductLinks(self):
        links = set()
        try:
            self.driver.get(self.baseUrl + self.categoryUrl)
            time.sleep(2)

            # Dismiss cookie banner
            try:
                from selenium.webdriver.common.by import By
                accept_btn = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")
                accept_btn.click()
                time.sleep(1)
            except:
                pass

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            pageItems = soup.find_all("li", class_="notSelected")
            if len(pageItems) >= 2:
                lastPage = int(pageItems[-2].text.strip())
            else:
                lastPage = 1

            for page in range(1, lastPage + 1):
                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                container = soup.find("div", class_="productListContainer")
                if container:
                    for link in container.find_all("a", href=True):
                        href = link.get("href")
                        if "page_" in href or "javascript" in href or "#" in href:
                            continue
                        if link.find_parent("div", id="pnlSoldOut"):
                            continue
                        links.add(self.baseUrl + href)

                if page < lastPage:
                    from selenium.webdriver.common.by import By
                    # Scroll to pagination first
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.5)

                    next_link = self.driver.find_element(By.LINK_TEXT, str(page + 1))
                    next_link.click()
                    time.sleep(1)

        except Exception as e:
            print(f"Failed to get product links: {e}")
        print(links)
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
        url = link

        # Product name: try desktop first, then mobile
        nameTag = soup.select_one("div#pnlTitle span.px-0") or soup.select_one("h1.product-name-mobile span.px-0")
        name = nameTag.get_text(strip=True) if nameTag else None

        # Part number: try desktop first, then mobile
        partTag = soup.select_one("div#pnlPartNumber h2") or soup.select_one("div#pnlPartNumberMobile h2")
        partNumber = partTag.get_text(strip=True) if partTag else None

        # Price
        priceContainer = soup.select_one("div#pnlPriceText")
        price = None
        if priceContainer:
            spans = [span.get_text(strip=True) for span in priceContainer.find_all("span")]
            numeric_parts = [s for s in spans if s.replace(",", "").replace(".", "").isdigit()]
            price_str = "".join(numeric_parts)
            if price_str:
                price = float(price_str.replace(",", ""))

        print(name, partNumber, price)
        return name, partNumber, price, url

    def downloadPartImage(self, soup, partNumber, componentSpecificDownloadPath):
        imageTag = soup.find("img", id = "imgImage") #Gets first image only, select is for css tags
        imageUrl = imageTag.get("data-src") or imageTag.get("src") #Accounts for if the website ever uses lazy load

        if imageUrl.startswith("/"):
            imageUrl = self.baseUrl + imageUrl
        imageUrl = imageUrl.split("?")[0]
        imageContent = requests.get(imageUrl).content
        imageFile = io.BytesIO(imageContent)
        image = Image.open(imageFile)
        folder = (f"productImages/{componentSpecificDownloadPath}")
        os.makedirs(folder, exist_ok=True)
        filePath = os.path.join(folder, f"{partNumber}.jpg")
        image.save(filePath, "JPEG")
        print("saved")
        fileName = f"{partNumber}.jpg"
        return f"productImages/{componentSpecificDownloadPath}/{fileName}"


