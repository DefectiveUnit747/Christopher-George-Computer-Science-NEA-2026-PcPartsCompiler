import time
import io
import requests
from PIL import Image
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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
        self.projectRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

    def acceptCookies(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
        except:
            pass

    def getProductLinks(self):
        links = set()
        try:
            self.driver.get(self.baseUrl + self.categoryUrl)
            time.sleep(2)
            self.acceptCookies()

            while True:
                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                # Get links from current page
                container = soup.find("div", class_="productListContainer")
                if container:
                    for link in container.find_all("a", href=True):
                        href = link.get("href")
                        if "page_" in href or "javascript" in href or "#" in href:
                            continue
                        if link.find_parent("div", id="pnlSoldOut"):
                            continue
                        links.add(self.baseUrl + href)

                # Try to find the "next" button
                from selenium.webdriver.common.by import By
                try:
                    next_button = self.driver.find_element(By.LINK_TEXT, "Next")
                    # Scroll down so the button is visible
                    self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
                    time.sleep(0.5)
                    next_button.click()
                    time.sleep(1)
                except:
                    # No "Next" button → last page reached
                    break

        except Exception as e:
            print(f"Failed to get product links: {e}")

        print(f"Collected {len(links)} links")
        return links

    def extractFromSpecsTable(self, fieldMapping, soup, componentType):
        componentMapping = fieldMapping.get(componentType)
        if not componentMapping:
            return {}
        specs = {}
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            label = cells[0].text.strip()
            value = cells[1].text.strip()
            field = componentMapping.get(label)
            if field:
                if isinstance(field, list):
                    for f in field:
                        specs[f] = value
                else:
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
        activeCarousel = soup.find("div", class_="owl-item active")
        imageTag = activeCarousel.find("img", id="imgImage") if activeCarousel else soup.find("img", id="imgImage")
        if not imageTag:
            return None

        imageUrl = imageTag.get("data-src") or imageTag.get("src")
        if imageUrl.startswith("/"):
            imageUrl = self.baseUrl + imageUrl
        imageUrl = imageUrl.split("?")[0]

        imageContent = requests.get(imageUrl).content
        imageFile = io.BytesIO(imageContent)
        image = Image.open(imageFile)
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")

        folder = os.path.join(self.projectRoot, "productImages", componentSpecificDownloadPath)
        os.makedirs(folder, exist_ok=True)

        normalisedPartNumber = partNumber.replace("/", "-").replace("\\", "-")
        filePath = os.path.join(folder, f"{normalisedPartNumber}.jpg")
        image.save(filePath, "JPEG")
        print(f"Saved to: {filePath}")

        return os.path.join("productImages", componentSpecificDownloadPath, f"{normalisedPartNumber}.jpg")


