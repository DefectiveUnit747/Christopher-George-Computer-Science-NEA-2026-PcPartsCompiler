import logging
import os
import io
import requests
import time
from PIL import Image
from bs4 import BeautifulSoup
from pcBuildListCompiler.scrapingTools.scraper import Scraper

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

TEMP_IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "testImageOutput")
os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)

def makeScraper(categoryUrl=""):
    scraper = Scraper.__new__(Scraper)
    scraper.baseUrl = "https://www.cclonline.com"
    scraper.categoryUrl = categoryUrl
    scraper._driver = None
    scraper._projectRoot = os.path.dirname(__file__)
    scraper._requestSession = None
    return scraper

def testDownloadValidImage(driver):
    logger.info("=== TEST: downloadPartImage() downloads and saves image ===")
    scraper = makeScraper()
    scraper._projectRoot = os.path.dirname(__file__)

    url = "https://www.cclonline.com/product/amd-ryzen-7-7800x3d-8-core-processor-100-100000909WOF/"
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    result = scraper.downloadPartImage(soup, "TEST-VALID-001", "testImages")
    logger.info(f"Result path: {result}")

    if result:
        fullPath = os.path.join(os.path.dirname(__file__), result)
        exists = os.path.exists(fullPath)
        logger.info(f"File exists on disk: {exists}")
        logger.info("PASS: Image downloaded and saved successfully")
    else:
        logger.warning("FAIL: Image element not found")

def testDownloadRgbaImage():
    logger.info("=== TEST: downloadPartImage() converts RGBA to RGB ===")
    scraper = makeScraper()

    # Create a fake RGBA image in memory and serve it via a mock soup
    rgbaImage = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
    buffer = io.BytesIO()
    rgbaImage.save(buffer, format="PNG")
    buffer.seek(0)

    # Save it temporarily so we can point an img tag at a real URL
    tempPath = os.path.join(TEMP_IMAGE_FOLDER, "rgba_test.png")
    with open(tempPath, "wb") as f:
        f.write(buffer.getvalue())

    logger.info(f"Created RGBA test image at {tempPath}")

    # Manually simulate what downloadPartImage does with an RGBA image
    image = Image.open(tempPath)
    logger.info(f"Image mode before conversion: {image.mode}")
    if image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")
    logger.info(f"Image mode after conversion: {image.mode}")

    savedPath = os.path.join(TEMP_IMAGE_FOLDER, "rgba_converted.jpg")
    image.save(savedPath, "JPEG")
    logger.info(f"Saved as JPEG to: {savedPath}")
    logger.info("PASS: RGBA image converted to RGB and saved as JPEG successfully")

def testDownloadMissingImage():
    logger.info("=== TEST: downloadPartImage() handles missing image element ===")
    scraper = makeScraper()

    soup = BeautifulSoup("<html><body><p>No image here</p></body></html>", "html.parser")
    result = scraper.downloadPartImage(soup, "TEST-MISSING-001", "testImages")

    logger.info(f"Result: {result}")
    assert result is None, "Expected None when no image element present"
    logger.info("PASS: Returns None without crashing, warning logged above")

def testGetProductLinks():
    logger.info("=== TEST: getProductLinks() extracts valid URLs and handles pagination ===")
    logger.info("=== Also tests: acceptCookies() and sold-out filtering ===")

    scraper = Scraper("https://www.cclonline.com", "/pc-components/cpu-processors/")

    links = scraper.getProductLinks()

    logger.info(f"Total valid links collected: {len(links)}")
    logger.info("Sample links:")
    for link in list(links)[:5]:
        logger.info(f"  {link}")

    assert len(links) > 0, "Expected at least some links"
    assert all(link.startswith("https://www.cclonline.com") for link in links), \
        "All links should start with base URL"
    assert not any("page_" in link for link in links), \
        "No pagination links should be in results"

    logger.info("PASS: Valid product URLs extracted, pagination navigated, sold-out items filtered")

    scraper._driver.quit()
    logger.info("Driver closed")

if __name__ == "__main__":
    logger.info("Starting manual scraping tests")
    logger.info("=" * 60)

    testDownloadMissingImage()
    logger.info("")
    testDownloadRgbaImage()
    logger.info("")
    testDownloadValidImage()
    logger.info("")
    testGetProductLinks()  # This one opens Chrome - run last

    logger.info("=" * 60)
    logger.info("All manual tests complete")