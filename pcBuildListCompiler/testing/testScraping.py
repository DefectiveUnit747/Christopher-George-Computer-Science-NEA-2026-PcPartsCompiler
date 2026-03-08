import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import io
import sys
import mockImports
import os
from pcBuildListCompiler.scrapingTools.scraper import Scraper
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add the project root to sys.path so Python can find scraper.py



# The field mapping from scrapeComponents.py - needed by extractFromSpecsTable
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
    "motherboard": {
        "Manufacturer": "manufacturer",
        "Power Requirement (auto)": "tdp",
        "Socket": "socket",
        "Motherboard Form Factor": "formFactor",
        "Memory Slot": "memorySlots",
        "Memory Type": "memoryType",
        "Maximum RAM": "maxMemory"
    },
    "ram": {
        "Manufacturer": "manufacturer",
        "Memory Size": "capacityGb",
        "Memory DIMM Count": "numberOfModules",
        "Memory Speed": "speedMhz",
        "Memory Type": "ddrType",
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
    "psu": {
        "Manufacturer": "manufacturer",
        "Power": "wattage",
        "80Plus Rated": "efficiencyRating",
        "PSU Form Factor": "formFactor",
        "Modular Cables": "modularity"
    }
}


class TestScraper(unittest.TestCase):

    def setUp(self):

        with patch.object(Scraper, "_initialiseDriver", return_value=MagicMock()):
            self.scraper = Scraper("https://www.cclonline.com", "/pc-components/cpu-processors/")
        # self.scraper._driver is now a MagicMock fake browser

    def test_extractsValidProductUrls(self):

        self.scraper._driver.page_source = """
        <div class="productListContainer">
            <a href="/product/amd-ryzen-7">AMD Ryzen 7</a>
            <a href="/product/intel-i9">Intel i9</a>
        </div>
        """
        self.scraper._driver.find_element.side_effect = Exception("No next button")

        result = self.scraper.getProductLinks()

        self.assertIn("https://www.cclonline.com/product/amd-ryzen-7", result)
        self.assertIn("https://www.cclonline.com/product/intel-i9", result)

    def test_handlesPaginationCorrectly(self):

        page1Html = """
        <div class="productListContainer">
            <a href="/product/cpu-page1">CPU Page 1</a>
        </div>
        """
        page2Html = """
        <div class="productListContainer">
            <a href="/product/cpu-page2">CPU Page 2</a>
        </div>
        """

        self.scraper._driver.page_source = page1Html

        mockNextButton = MagicMock()

        callCount = {"n": 0}

        def findElementSideEffect(*args, **kwargs):
            callCount["n"] += 1
            if callCount["n"] == 1:
                self.scraper._driver.page_source = page2Html
                return mockNextButton
            else:
                raise Exception("No more pages")

        self.scraper._driver.find_element.side_effect = findElementSideEffect

        result = self.scraper.getProductLinks()

        self.assertIn("https://www.cclonline.com/product/cpu-page1", result)
        self.assertIn("https://www.cclonline.com/product/cpu-page2", result)
        # Products from both pages should be in the final set

    def test_filtersOutSoldOutItems(self):
        """Test #3: getProductLinks() excludes links wrapped in pnlSoldOut"""

        self.scraper._driver.page_source = """
        <div class="productListContainer">
            <a href="/product/in-stock">In Stock CPU</a>
            <div id="pnlSoldOut">
                <a href="/product/sold-out">Sold Out CPU</a>
            </div>
        </div>
        """
        self.scraper._driver.find_element.side_effect = Exception("No next button")

        result = self.scraper.getProductLinks()

        self.assertIn("https://www.cclonline.com/product/in-stock", result)
        self.assertNotIn("https://www.cclonline.com/product/sold-out", result)
        # Sold-out product must be absent from results

    def test_acceptCookiesClicksButton(self):
        """Test #4: _acceptCookies() clicks the accept button when popup appears"""

        with patch("pcBuildListCompiler.scrapingTools.scraper.WebDriverWait") as mockWait:
            mockClickable = MagicMock()

            # WebDriverWait(...).until(...) should return the clickable element
            mockWait.return_value.until.return_value = mockClickable

            # Call the real method
            self.scraper._acceptCookies()

            # Assert click was called exactly once
            mockClickable.click.assert_called_once()

    def test_acceptCookiesHandlesMissingPopup(self):
        """Test #4b: _acceptCookies() does not crash when cookie popup is absent"""

        with patch("scrapingTools.scraper.WebDriverWait") as mockWait:
            mockWait.return_value.until.side_effect = Exception("Timeout")
            # Simulate the popup never appearing

            try:
                self.scraper._acceptCookies()
            except Exception:
                self.fail("_acceptCookies() raised an exception when popup was missing")
            # If any exception escapes the method, this test fails

    def test_getNameNumberPriceUrlExtractsAllFields(self):
        """Test #5: getNameNumberPriceUrl() extracts name, part number, price and url"""

        html = """
        <div id="pnlTitle"><span class="px-0">AMD Ryzen 7 7800X3D</span></div>
        <div id="pnlPartNumber"><h2>100-000000589</h2></div>
        <div id="pnlPriceText">
            <span>379</span><span>.</span><span>99</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        link = "https://www.cclonline.com/product/amd-ryzen-7-7800x3d"

        name, partNumber, price, url = self.scraper.getNameNumberPriceUrl(link, soup)
        # Call the REAL method

        self.assertEqual(name, "AMD Ryzen 7 7800X3D")
        self.assertEqual(partNumber, "100-000000589")
        self.assertIsNotNone(price)
        # Price should have been extracted (exact value depends on parsing logic)
        self.assertEqual(url, link)

    def test_getNameNumberPriceUrlHandlesMissingFields(self):
        """Test #6: getNameNumberPriceUrl() returns None for each missing field"""

        html = """
        <div id="pnlTitle"><span class="px-0">Some Product</span></div>
        """
        # Only name is present - part number and price divs are absent

        soup = BeautifulSoup(html, "html.parser")
        link = "https://www.cclonline.com/product/test"

        name, partNumber, price, url = self.scraper.getNameNumberPriceUrl(link, soup)

        self.assertEqual(name, "Some Product")
        # Name was in the HTML so should be returned correctly
        self.assertIsNone(partNumber)

        self.assertIsNone(price)


    def test_extractFromSpecsTableCpu(self):
        """Test #7: extractFromSpecsTable() extracts all CPU specs correctly"""

        html = """
        <table>
            <tr><td>CPU Base Speed</td><td>3.8 GHz</td></tr>
            <tr><td>Number of Cores</td><td>8</td></tr>
            <tr><td>Cache</td><td>96 MB</td></tr>
            <tr><td>Socket</td><td>AM5</td></tr>
            <tr><td>CPU Base TDP</td><td>120W</td></tr>
            <tr><td>CPU Threads</td><td>16</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "cpu")
        # Call the REAL method - soup and fieldMapping are passed in directly

        self.assertEqual(result["coreClock"], "3.8 GHz")
        self.assertEqual(result["coreCount"], "8")
        self.assertEqual(result["cache"], "96 MB")
        self.assertEqual(result["socket"], "AM5")
        self.assertEqual(result["tdp"], "120W")
        self.assertEqual(result["threads"], "16")

    def test_extractFromSpecsTableGpu(self):
        """Test #8: extractFromSpecsTable() extracts all GPU specs correctly"""

        html = """
        <table>
            <tr><td>Chipset Manufacturer</td><td>NVIDIA</td></tr>
            <tr><td>Memory Size</td><td>16 GB</td></tr>
            <tr><td>Memory Type</td><td>GDDR6X</td></tr>
            <tr><td>GPU Length</td><td>304mm</td></tr>
            <tr><td>Power Consumption</td><td>320W</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "gpu")

        self.assertEqual(result["manufacturer"], "NVIDIA")
        self.assertEqual(result["memoryGb"], "16 GB")
        self.assertEqual(result["memoryType"], "GDDR6X")
        self.assertEqual(result["length"], "304mm")
        self.assertEqual(result["tdpWatts"], "320W")

    def test_extractFromSpecsTableMotherboard(self):
        """Test #9: extractFromSpecsTable() extracts all motherboard specs correctly"""

        html = """
        <table>
            <tr><td>Manufacturer</td><td>ASUS</td></tr>
            <tr><td>Socket</td><td>AM5</td></tr>
            <tr><td>Motherboard Form Factor</td><td>ATX</td></tr>
            <tr><td>Memory Slot</td><td>4</td></tr>
            <tr><td>Memory Type</td><td>DDR5</td></tr>
            <tr><td>Maximum RAM</td><td>128 GB</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "motherboard")

        self.assertEqual(result["manufacturer"], "ASUS")
        self.assertEqual(result["socket"], "AM5")
        self.assertEqual(result["formFactor"], "ATX")
        self.assertEqual(result["memorySlots"], "4")
        self.assertEqual(result["memoryType"], "DDR5")
        self.assertEqual(result["maxMemory"], "128 GB")

    def test_extractFromSpecsTableRam(self):
        """Test #10: extractFromSpecsTable() extracts all RAM specs correctly"""

        html = """
        <table>
            <tr><td>Manufacturer</td><td>Corsair</td></tr>
            <tr><td>Memory Size</td><td>32 GB</td></tr>
            <tr><td>Memory DIMM Count</td><td>2</td></tr>
            <tr><td>Memory Speed</td><td>6000 MHz</td></tr>
            <tr><td>Memory Type</td><td>DDR5</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "ram")

        self.assertEqual(result["manufacturer"], "Corsair")
        self.assertEqual(result["capacityGb"], "32 GB")
        self.assertEqual(result["numberOfModules"], "2")
        self.assertEqual(result["speedMhz"], "6000 MHz")
        self.assertEqual(result["ddrType"], "DDR5")

    def test_extractFromSpecsTableStorage(self):
        """Test #11: extractFromSpecsTable() extracts all storage specs correctly"""

        html = """
        <table>
            <tr><td>Manufacturer</td><td>Samsung</td></tr>
            <tr><td>Drive Capacity</td><td>1 TB</td></tr>
            <tr><td>Read Speed</td><td>7000 MB/s</td></tr>
            <tr><td>Write Speed</td><td>5000 MB/s</td></tr>
            <tr><td>Storage Type</td><td>M.2 NVMe</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "storage")

        self.assertEqual(result["manufacturer"], "Samsung")
        self.assertEqual(result["capacityGb"], "1 TB")
        self.assertEqual(result["readSpeed"], "7000 MB/s")
        self.assertEqual(result["writeSpeed"], "5000 MB/s")
        self.assertEqual(result["formFactor"], "M.2 NVMe")

    def test_extractFromSpecsTablePsu(self):
        """Test #12: extractFromSpecsTable() extracts all PSU specs correctly"""

        html = """
        <table>
            <tr><td>Manufacturer</td><td>Corsair</td></tr>
            <tr><td>Power</td><td>850W</td></tr>
            <tr><td>80Plus Rated</td><td>Gold</td></tr>
            <tr><td>PSU Form Factor</td><td>ATX</td></tr>
            <tr><td>Modular Cables</td><td>Fully Modular</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "psu")

        self.assertEqual(result["manufacturer"], "Corsair")
        self.assertEqual(result["wattage"], "850W")
        self.assertEqual(result["efficiencyRating"], "Gold")
        self.assertEqual(result["formFactor"], "ATX")
        self.assertEqual(result["modularity"], "Fully Modular")

    def test_extractFromSpecsTableMissingTable(self):
        """Test #13: extractFromSpecsTable() returns empty dict when table is absent"""

        html = "<div>No specs table here</div>"
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "cpu")

        self.assertEqual(result, {})
        # No rows to parse so the result should be an empty dict

    def test_extractFromSpecsTableUnknownType(self):
        """Test #13b: extractFromSpecsTable() returns empty dict for unknown component type"""

        html = "<table><tr><td>Socket</td><td>AM5</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "unknownType")

        self.assertEqual(result, {})
        # "unknownType" has no entry in fieldMapping so nothing can be extracted

    # -------------------------------------------------------------------
    # TESTS 14, 15, 16 - downloadPartImage()
    # -------------------------------------------------------------------

    def test_downloadPartImageDownloadsAndSaves(self):
        """Test #14: downloadPartImage() downloads image and returns a valid path"""

        html = """
        <div class="owl-item active">
            <img id="imgImage" data-src="https://example.com/cpu.jpg">
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Build a real in-memory JPEG to use as the fake HTTP response body
        testImage = Image.new("RGB", (100, 100), color="red")
        imgBytes = io.BytesIO()
        testImage.save(imgBytes, format="JPEG")
        imgBytes.seek(0)
        # seek(0) resets the cursor to the start so getvalue() reads all bytes

        with patch("scrapingTools.scraper.requests.get") as mockGet:
            # Patch requests.get inside scraper.py so no real HTTP request is made
            mockGet.return_value.content = imgBytes.getvalue()
            # The fake response returns our test image bytes

            with patch("scrapingTools.scraper.os.makedirs"):
                # Stop makedirs creating real folders during the test
                with patch.object(Image.Image, "save"):
                    # Stop image.save writing a real file during the test
                    result = self.scraper.downloadPartImage(soup, "100-000000589", "cpuImages")

        self.assertIsNotNone(result)
        # A path string should be returned, not None

        self.assertIn("100-000000589", result)
        # Part number should appear in the returned path

        self.assertIn("cpuImages", result)
        # Component folder name should appear in the returned path

    def test_downloadPartImageConvertsRgbaToRgb(self):
        """Test #15: downloadPartImage() converts RGBA images to RGB before saving"""

        html = """
        <div class="owl-item active">
            <img id="imgImage" data-src="https://example.com/cpu.png">
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        # Create a PNG with an alpha (transparency) channel - mode is RGBA
        rgbaImage = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        imgBytes = io.BytesIO()
        rgbaImage.save(imgBytes, format="PNG")
        imgBytes.seek(0)

        convertedModes = []
        # List to capture the mode of the image after conversion

        originalConvert = Image.Image.convert
        # Hold a reference to the real convert method

        def captureConvert(selfImg, mode):
            converted = originalConvert(selfImg, mode)
            convertedModes.append(converted.mode)
            return converted
        # Wrapper: calls real convert() but records the resulting mode

        with patch("scrapingTools.scraper.requests.get") as mockGet:
            mockGet.return_value.content = imgBytes.getvalue()
            with patch("scrapingTools.scraper.os.makedirs"):
                with patch.object(Image.Image, "save"):
                    with patch.object(Image.Image, "convert", captureConvert):
                        self.scraper.downloadPartImage(soup, "TEST-123", "cpuImages")

        self.assertIn("RGB", convertedModes)
        # convert("RGB") must have been called on the RGBA image

    def test_downloadPartImageReturnsNoneWhenNoImageTag(self):
        """Test #16a: downloadPartImage() returns None when there is no img tag"""

        html = "<div>No image here</div>"
        soup = BeautifulSoup(html, "html.parser")

        result = self.scraper.downloadPartImage(soup, "TEST-123", "cpuImages")

        self.assertIsNone(result)
        # No img tag found so the method should return None without crashing

    def test_downloadPartImageHandlesDownloadError(self):
        """Test #16b: downloadPartImage() returns None when the HTTP request fails"""

        html = """
        <div class="owl-item active">
            <img id="imgImage" data-src="https://example.com/image.jpg">
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        with patch("scrapingTools.scraper.requests.get") as mockGet:
            mockGet.side_effect = Exception("Network error")
            # Force requests.get to raise an exception

            result = self.scraper.downloadPartImage(soup, "TEST-123", "cpuImages")

        self.assertIsNone(result)
        # Download failed so None should be returned cleanly

if __name__ == "__main__":
    unittest.main(verbosity=2)