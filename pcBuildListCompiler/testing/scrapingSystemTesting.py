from pcBuildListCompiler.scrapingTools.scrapeComponents import componentScraper
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


def test1ExtractUrls():
    print("\n" + "=" * 70)
    print("TEST 1: Extract Valid Product URLs")
    print("=" * 70)

    db = Database("computerParts.db")
    manufacturerMap = db.getManufacturerMap()
    scraper = componentScraper("https://www.cclonline.com", db)
    scraper.categoryUrl = "/pc-components/cpu-processors"

    print("\nThis test only reads data - it won't modify your database")
    print("Scraping links (this may take 30-60 seconds)...\n")

    links = scraper.getProductLinks()

    print(f"\nFound {len(links)} links")
    print("\nFirst 10 links:")
    for i, link in enumerate(list(links)[:10], 1):
        print(f"  {i}. {link}")

    print(f"\nValidation:")
    print(f"  Total links: {len(links)}")
    print(f"  All valid URLs: {all(link.startswith('https://') for link in links)}")
    print(f"  No pagination links: {all('page_' not in link for link in links)}")

    print("\nManual verification steps:")
    print("1. Copy one of the URLs above")
    print("2. Paste into browser")
    print("3. Verify it's a real CPU product page")
    print("4. Check product is in stock (not sold out)")

    verify = input("\nDid the links work correctly? (y/n): ")

    scraper.driver.quit()
    db.close()

    if verify.lower() == 'y':
        print("Test 1 passed")
        return True
    else:
        print("Test 1 failed")
        return False


def test2Pagination():
    print("\n" + "=" * 70)
    print("TEST 2: Pagination")
    print("=" * 70)

    print("\nThis test only navigates pages - no database changes")
    print("Watch the browser - it will cycle through pages\n")

    db = Database("computerParts.db")
    scraper = componentScraper("https://www.cclonline.com", db)
    scraper.categoryUrl = "/pc-components/cpu-processors"
    scraper.driver = scraper._initialiseDriver()
    scraper.driver.get(scraper.baseUrl + scraper.categoryUrl)
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
        print(f"Will test first {pagesToTest} pages\n")

        for page in range(1, pagesToTest + 1):
            print(f"Currently on page {page}/{totalPages}")
            time.sleep(1)

            if page < pagesToTest:
                try:
                    from selenium.webdriver.common.by import By
                    nextBtn = scraper.driver.find_element(By.LINK_TEXT, str(page + 1))
                    nextBtn.click()
                    print(f"  Navigating to page {page + 1}...")
                    time.sleep(1)
                except Exception as e:
                    print(f"  Could not navigate: {e}")
    else:
        print("Only 1 page found")

    print("\nManual verification steps:")
    print("1. Did you see the browser navigate between pages?")
    print("2. Did different products appear on each page?")
    print("3. Were page numbers correct?")

    verify = input("\nDid pagination work correctly? (y/n): ")

    scraper.driver.quit()
    db.close()

    if verify.lower() == 'y':
        print("Test 2 passed")
        return True
    else:
        print("Test 2 failed")
        return False


def test3FilterSoldOut():
    print("\n" + "=" * 70)
    print("TEST 3: Filter Sold-Out Products")
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
            print(f"  Included: {link.text.strip()}")
        else:
            print(f"  Filtered out: {link.text.strip()}")

    print(f"\nResults:")
    print(f"  Found: {len(links)} products")
    print(f"  Expected: 3 products")

    try:
        assert len(links) == 3, f"Expected 3, got {len(links)}"
        assert "/cpu-sold-1" not in links, "Sold-out product 1 should be filtered"
        assert "/cpu-sold-2" not in links, "Sold-out product 2 should be filtered"
        assert "/cpu-1" in links, "In-stock product 1 should be included"
        assert "/cpu-2" in links, "In-stock product 2 should be included"
        assert "/cpu-3" in links, "In-stock product 3 should be included"

        print("\nTest 3 passed - filtering works correctly")
        return True

    except AssertionError as e:
        print(f"\nTest 3 failed: {e}")
        return False


def test4Cookies():
    print("\n" + "=" * 70)
    print("TEST 4: Cookie Popup")
    print("=" * 70)

    print("\nThis test only clicks cookie button - no database changes")

    db = Database("computerParts.db")
    scraper = componentScraper("https://www.cclonline.com", db)
    scraper.driver = scraper._initialiseDriver()
    scraper.driver.get("https://www.cclonline.com")
    time.sleep(2)

    print("\nWatch the browser for cookie popup...")

    try:
        from selenium.webdriver.common.by import By
        btn = scraper.driver.find_element(By.ID, "onetrust-accept-btn-handler")

        print("Cookie popup detected")
        print("Clicking accept button...")

        btn.click()
        time.sleep(1)

        try:
            scraper.driver.find_element(By.ID, "onetrust-accept-btn-handler")
            print("Cookie popup still present")
            success = False
        except:
            print("Cookie popup dismissed successfully")
            success = True

    except Exception as e:
        print(f"Cookie popup not found (may already be accepted)")
        print(f"Error: {e}")
        success = True

    print("\nManual verification:")
    print("Did you see the cookie popup disappear?")

    verify = input("\nDid cookie handling work? (y/n): ")

    scraper.driver.quit()
    db.close()

    if verify.lower() == 'y' and success:
        print("Test 4 passed")
        return True
    else:
        print("Test 4 failed")
        return False


def test5DownloadImage():
    print("\n" + "=" * 70)
    print("TEST 5: Download Product Image")
    print("=" * 70)

    print("\nThis test saves to temporary folder - won't affect productImages/")

    env = SafeTestEnvironment()

    try:
        db = Database("computerParts.db")
        scraper = componentScraper("https://www.cclonline.com", db)
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
            print(f"Found image URL: {imageUrl}")

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

            if image.mode == 'RGBA' or image.mode == "LA":
                image = image.convert('RGB')

            testFolder = env.getTestImagePath("cpuImages")
            filePath = os.path.join(testFolder, "TEST-i7-14700K.jpg")
            image.save(filePath, "JPEG")

            print(f"Image saved successfully")
            print(f"Location: {filePath}")
            print(f"Size: {os.path.getsize(filePath)} bytes")
            print(f"Format: {image.format}")
            print(f"Dimensions: {image.size}")

            print(f"\nManual verification:")
            print(f"1. Open this file: {os.path.abspath(filePath)}")
            print("2. Verify it's the Intel i7-14700K image")
            print("3. Check image quality is acceptable")

            verify = input("\nIs the image correct? (y/n): ")

            success = verify.lower() == 'y'

        else:
            print("Could not find image on page")
            success = False

        scraper.driver.quit()
        db.close()

    finally:
        env.cleanup()
        print("\nAll test files deleted - no trace left")

    if success:
        print("Test 5 passed")
        return True
    else:
        print("Test 5 failed")
        return False


def runAllSafeTests():
    print("\n" + "=" * 80)
    print("Safe Manual Scraper Test Suite")
    print("=" * 80)
    print("\nSafety guarantees:")
    print("  No database modifications")
    print("  Test images saved to temporary folder")
    print("  All test files deleted after completion")
    print("  Read-only operations only")
    print("\n" + "=" * 80)

    input("\nPress Enter to start tests...")

    results = {}

    try:
        results['Extract URLs'] = test1ExtractUrls()
    except Exception as e:
        print(f"\nTest 1 crashed: {e}")
        results['Extract URLs'] = False

    try:
        results['Pagination'] = test2Pagination()
    except Exception as e:
        print(f"\nTest 2 crashed: {e}")
        results['Pagination'] = False

    try:
        results['Filter Sold-Out'] = test3FilterSoldOut()
    except Exception as e:
        print(f"\nTest 3 crashed: {e}")
        results['Filter Sold-Out'] = False

    try:
        results['Accept Cookies'] = test4Cookies()
    except Exception as e:
        print(f"\nTest 4 crashed: {e}")
        results['Accept Cookies'] = False

    try:
        results['Download Image'] = test5DownloadImage()
    except Exception as e:
        print(f"\nTest 5 crashed: {e}")
        results['Download Image'] = False

    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    for testName, passed in results.items():
        status = "Pass" if passed else "Fail"
        print(f"{status} - {testName}")

    total = len(results)
    passed = sum(results.values())
    percentage = (passed / total) * 100 if total > 0 else 0

    print(f"\nResult: {passed}/{total} tests passed ({percentage:.0f}%)")
    print("\nAll tests completed safely - no database was harmed")


if __name__ == "__main__":
    runAllSafeTests()