import time
import io
import requests
from PIL import Image
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import logging

logger = logging.getLogger(__name__)

baseUrl = "https://www.cclonline.com"
componentLinksToAddOn = [
    "/pc-components/cpu-processors", "/pc-components/motherboards",
    "/pc-components/graphics-cards", "/pc-components/cases",
    "/pc-components/power-supplies", "/storage",
    "/pc-components/memory/desktop-memory"
]

class Scraper:
    def __init__(self, url, categoryUrl):
        logger.info("Initialising scraper for category %s", categoryUrl)

        self.baseUrl = url
        self.categoryUrl = categoryUrl
        self._driver = self._initialiseDriver()
        self._projectRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._requestSession = None

    def _initialiseDriver(self):
        logger.info("Launching Chrome driver")
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        return uc.Chrome(options=options)

    def initialiseRequestSession(self):
        logger.info("Initialising request session with browser cookies")

        session = requests.Session()
        for cookie in self._driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])

        session.headers.update({
            "User-Agent": self._driver.execute_script("return navigator.userAgent;"),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.cclonline.com/"
        })

        self._requestSession = session
        logger.info("Request session initialised")

    def _acceptCookies(self):
        try:
            logger.info("Attempting to accept cookies")
            WebDriverWait(self._driver, 5).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click() #Waits for cookies thing to pop up
            logger.info("Cookies accepted")
        except Exception:
            logger.warning("Cookie popup not found or could not be clicked") #Not fatal error, still can scrape if cookies didn't pop up

    def getProductLinks(self):
        logger.info("Scraping product links for %s", self.categoryUrl)
        links = set()
        try:
            self._driver.get(self.baseUrl + self.categoryUrl)
            time.sleep(2)
            self._acceptCookies()

            while True:
                soup = BeautifulSoup(self._driver.page_source, "html.parser")
                container = soup.find("div", class_="productListContainer")

                if container:
                    for link in container.find_all("a", href=True):
                        href = link.get("href")
                        if "page_" in href or "javascript" in href or "#" in href:
                            continue
                        if link.find_parent("div", id="pnlSoldOut"):
                            continue
                        links.add(self.baseUrl + href)

                try:
                    next_button = self._driver.find_element(By.LINK_TEXT, "Next")
                    self._driver.execute_script("arguments[0].scrollIntoView();", next_button)
                    time.sleep(0.5)
                    next_button.click()
                    time.sleep(1)
                except Exception:
                    logger.info("Reached last page for %s", self.categoryUrl)
                    break

        except Exception as e:
            logger.error("Failed to get product links: %s", e)

        logger.info("Collected %d product links", len(links))
        return links

    def extractFromSpecsTable(self, fieldMapping, soup, componentType):
        logger.info("Extracting specs for component type %s", componentType)

        componentMapping = fieldMapping.get(componentType)
        if not componentMapping:
            logger.warning("No field mapping found for %s", componentType) #If there is a missing type in the mapping from above
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
                    specs[field] = valuecro

        logger.info("Extracted %d specs for %s", len(specs), componentType)
        return specs

    def getNameNumberPriceUrl(self, link, soup):
        logger.info("Extracting name, part number, and price from %s", link)

        url = link
        nameTag = soup.select_one("div#pnlTitle span.px-0") or soup.select_one("h1.product-name-mobile span.px-0")
        name = nameTag.get_text(strip=True) if nameTag else None

        partTag = soup.select_one("div#pnlPartNumber h2") or soup.select_one("div#pnlPartNumberMobile h2")
        partNumber = partTag.get_text(strip=True) if partTag else None

        priceContainer = soup.select_one("div#pnlPriceText")
        price = None
        if priceContainer:
            spans = [span.get_text(strip=True) for span in priceContainer.find_all("span")]
            numeric_parts = [s for s in spans if s.replace(",", "").replace(".", "").isdigit()]
            price_str = "".join(numeric_parts)
            if price_str:
                price = float(price_str.replace(",", ""))

        return name, partNumber, price, url

    def downloadPartImage(self, soup, partNumber, componentSpecificDownloadPath):
        logger.info("Downloading image for part %s", partNumber)

        activeCarousel = soup.find("div", class_="owl-item active")
        imageTag = activeCarousel.find("img", id="imgImage") if activeCarousel else soup.find("img", id="imgImage")

        if not imageTag:
            logger.warning("No image found for part %s", partNumber)
            return None

        imageUrl = imageTag.get("data-src") or imageTag.get("src")
        if imageUrl.startswith("/"):
            imageUrl = self.baseUrl + imageUrl
        imageUrl = imageUrl.split("?")[0]

        try:
            imageContent = requests.get(imageUrl).content
        except Exception as e:
            logger.error("Failed to download image for %s: %s", partNumber, e)
            return None

        imageFile = io.BytesIO(imageContent)
        image = Image.open(imageFile)
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")

        folder = os.path.join(self._projectRoot, "productImages", componentSpecificDownloadPath)
        os.makedirs(folder, exist_ok=True)

        normalisedPartNumber = partNumber.replace("/", "-").replace("\\", "-")
        filePath = os.path.join(folder, f"{normalisedPartNumber}.jpg")
        image.save(filePath, "JPEG")

        logger.info("Saved image for %s to %s", partNumber, filePath)

        return os.path.join("productImages", componentSpecificDownloadPath, f"{normalisedPartNumber}.jpg")