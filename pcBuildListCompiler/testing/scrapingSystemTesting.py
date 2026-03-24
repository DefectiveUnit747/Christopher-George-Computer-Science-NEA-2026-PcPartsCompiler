from pcBuildListCompiler.scrapingTools.scrapeComponents import ComponentScraper
from pcBuildListCompiler.databasing.createDatabase import Database
from bs4 import BeautifulSoup
import os
import time
import tempfile
import shutil


class SafeTestEnvironment:
    def __init__(self):
        self.tempDir = tempfile.mkdtemp(prefix="scraper_test_")
        print(f"Created temporary test directory: {self.tempDir}")

    def cleanup(self):
        if os.path.exists(self.tempDir):
            shutil.rmtree(self.tempDir)
            print(f"Cleaned up test directory")

    def getTestImagePath(self, folder):
        testFolder = os.path.join(self.tempDir, folder)
        os.makedirs(testFolder, exist_ok=True)
        return testFolder


def test1FilterSoldOut():
    print("\n" + "=" * 70)
    print("TEST 1: Filter Sold-Out Products")
    print("=" * 70)

    print("\nThis test uses mock HTML - no real scraping or database changes")

    html = '''
    <div class="productListContainer">
        <a href="/cpu-1">Intel i7-14700K (In Stock)</a>
        <div id="pnlSoldOut">
            <a href="/cpu-sold-1">Intel i9-14900K (Sold Out)</a>
        </div>
        <a href="/cpu-2">AMD Ryzen 7 7800X3D (In Stock)</a>
        <div id="pnlSoldOut">
            <a href="/cpu-sold-2">AMD Ryzen 9 7950X (Sold Out)</a>
        </div>
        <a href="/cpu-3">Intel i5-14600K (In Stock)</a>
    </div>
    '''

    print("\nMock HTML contains:")
    print("  3 in-stock products")
    print("  2 sold-out products (in pnlSoldOut div)\n")

    soup = BeautifulSoup(html, 'html.parser')
    links = set()

    container = soup.find("div", class_="productListContainer")
    for link in container.find_all("a", href=True):
        if not link.find_parent("div", id="pnlSoldOut"):
            links.add(link.get("href"))
            print(f"  Included: {link.get('href')}")
        else:
            print(f"  Filtered: {link.get('href')}")

    print(f"\nTotal: {len(links)} (expected 3)")

    try:
        assert len(links) == 3
        assert "/cpu-sold-1" not in links
        assert "/cpu-sold-2" not in links
        assert "/cpu-1" in links
        assert "/cpu-2" in links
        assert "/cpu-3" in links
        print("PASS")
        return True
    except AssertionError as e:
        print(f"FAIL: {e}")
        return False


def test2Pagination():
    print("\n" + "=" * 70)
    print("TEST 2: Pagination Through Multiple Pages")
    print("=" * 70)

    print("\nThis test only navigates pages - no database changes")
    print("Watch the browser - it will cycle through pages\n")

    db = Database()
    scraper = ComponentScraper("https://www.cclonline.com", db)
    scraper.driver = scraper._initialiseDriver()
    scraper.driver.get(scraper.baseUrl + "/pc-components/cpu-processors")
    time.sleep(2)

    try:
        from selenium.webdriver.common.by import By
        acceptBtn = scraper.driver.find_element(By.ID, "onetrust-accept-btn-handler")
        acceptBtn.click()
        time.sleep(1)
    except:
        pass

    soup = BeautifulSoup(scraper.driver.page_source, "html.parser")
    pages = soup.find_all("li", class_="notSelected")

    if len(pages) >= 2:
        totalPages = int(pages[-2].text.strip())
        print(f"Found {totalPages} total pages")
        pagesToTest = min(3, totalPages)
        print(f"Testing first {pagesToTest} pages\n")

        for page in range(1, pagesToTest + 1):
            print(f"Currently on page {page}/{totalPages}")
            time.sleep(1)
            if page < pagesToTest:
                try:
                    from selenium.webdriver.common.by import By
                    nextBtn = scraper.driver.find_element(By.LINK_TEXT, str(page + 1))
                    nextBtn.click()
                    print(f"  Navigated to page {page + 1}")
                    time.sleep(1)
                except Exception as e:
                    print(f"  Could not navigate: {e}")
    else:
        print("Only 1 page found")

    print("\nManual verification:")
    print("1. Did the browser navigate between pages?")
    print("2. Did different products appear on each page?")

    verify = input("\nDid pagination work correctly? (y/n): ")

    scraper.driver.quit()
    db.close()

    if verify.lower() == 'y':
        print("PASS")
        return True
    else:
        print("FAIL")
        return False


def test3DownloadImage():
    print("\n" + "=" * 70)
    print("TEST 3: Download Product Image")
    print("=" * 70)

    print("\nThis test saves to a temporary folder - won't affect productImages/")

    env = SafeTestEnvironment()

    try:
        db = Database()
        scraper = ComponentScraper("https://www.cclonline.com", db)
        scraper.driver = scraper._initialiseDriver()
        url = "https://www.cclonline.com/intel-core-i7-14700k-processor-bx8071514700k-253817.html"

        print(f"\nLoading product page...")
        scraper.driver.get(url)
        time.sleep(3)

        try:
            from selenium.webdriver.common.by import By
            acceptBtn = scraper.driver.find_element(By.ID, "onetrust-accept-btn-handler")
            acceptBtn.click()
            time.sleep(1)
        except:
            pass

        soup = BeautifulSoup(scraper.driver.page_source, "html.parser")

        activeCarousel = soup.find("div", class_="owl-item active")
        if activeCarousel:
            imageTag = activeCarousel.find("img", id="imgImage")
        else:
            imageTag = soup.find("img", id="imgImage")

        if imageTag:
            imageUrl = imageTag.get("data-src") or imageTag.get("src")
            print(f"Image tag found")
            print(f"Image URL: {imageUrl}")

            import requests
            from PIL import Image
            import io

            if imageUrl.startswith("/"):
                imageUrl = "https://www.cclonline.com" + imageUrl
            imageUrl = imageUrl.split("?")[0]

            print(f"\nDownloading to temporary folder...")
            imageContent = requests.get(imageUrl).content
            imageFile = io.BytesIO(imageContent)
            image = Image.open(imageFile)

            if image.mode in ('RGBA', 'LA'):
                image = image.convert('RGB')

            testFolder = env.getTestImagePath("cpuImages")
            filePath = os.path.join(testFolder, "TEST-i7-14700K.jpg")
            image.save(filePath, "JPEG")

            print(f"Image saved to: {filePath}")
            print(f"Size: {os.path.getsize(filePath)} bytes")
            print(f"Dimensions: {image.size}")

            print(f"\nManual verification:")
            print(f"1. Open this file: {os.path.abspath(filePath)}")
            print("2. Verify it shows the Intel i7-14700K product image")

            verify = input("\nIs the image correct? (y/n): ")
            success = verify.lower() == 'y'

        else:
            print("Could not find image on page")
            success = False

        scraper.driver.quit()
        db.close()

    finally:
        env.cleanup()
        print("\nAll test files deleted")

    if success:
        print("PASS")
        return True
    else:
        print("FAIL")
        return False


def runAllManualTests():
    print("\n" + "=" * 80)
    print("Manual Scraper Test Suite")
    print("=" * 80)

    results = {}

    try:
        results['Filter Sold-Out'] = test1FilterSoldOut()
    except Exception as e:
        print(f"\nTest 1 crashed: {e}")
        results['Filter Sold-Out'] = False

    try:
        results['Pagination'] = test2Pagination()
    except Exception as e:
        print(f"\nTest 2 crashed: {e}")
        results['Pagination'] = False

    try:
        results['Download Image'] = test3DownloadImage()
    except Exception as e:
        print(f"\nTest 3 crashed: {e}")
        results['Download Image'] = False

    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    for testName, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status} - {testName}")

    total = len(results)
    passed = sum(results.values())
    print(f"\nResult: {passed}/{total} tests passed")


if __name__ == "__main__":
    runAllManualTests()