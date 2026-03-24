import unittest
import logging
import io
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from PIL import Image
from pcBuildListCompiler.scrapingTools.scraper import Scraper

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

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
        "Base Chip Clock": "coreClock",
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
        "Read Speed": "readSpeed",
        "Write Speed": "writeSpeed",
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


def makeScraper():
    scraper = Scraper.__new__(Scraper)
    scraper.baseUrl = "https://www.cclonline.com"
    scraper.categoryUrl = ""
    scraper._driver = None
    scraper._projectRoot = "/tmp"
    scraper._requestSession = None
    return scraper


def makeHtml(rows):
    rowHtml = ""
    for label, value in rows:
        rowHtml += f"<tr><td>{label}</td><td>{value}</td></tr>"
    return f"<html><body><table>{rowHtml}</table></body></html>"


def makeFakeImageBytes():
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestGetNameNumberPriceUrl(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsAllProductFields(self):
        html = """
        <html><body>
            <div id="pnlTitle"><span class="px-0">AMD Ryzen 7 7800X3D</span></div>
            <div id="pnlPartNumber"><h2>100-000000589</h2></div>
            <div id="pnlPriceText"><span>800</span></div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        name, partNumber, price, url = self.scraper.getNameNumberPriceUrl("https://www.cclonline.com/product", soup)
        logger.info(f"name={name}, partNumber={partNumber}, price={price}")
        self.assertEqual(name, "AMD Ryzen 7 7800X3D")
        self.assertEqual(partNumber, "100-000000589")
        self.assertEqual(price, 800.0)
        self.assertEqual(url, "https://www.cclonline.com/product")

    def testHandlesMissingPriceReturnsNone(self):
        html = """
        <html><body>
            <div id="pnlTitle"><span class="px-0">AMD Ryzen 5 7600</span></div>
            <div id="pnlPartNumber"><h2>100-000000599</h2></div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        name, partNumber, price, url = self.scraper.getNameNumberPriceUrl("https://www.cclonline.com/product", soup)
        logger.info(f"name={name}, partNumber={partNumber}, price={price}")
        self.assertEqual(name, "AMD Ryzen 5 7600")
        self.assertEqual(partNumber, "100-000000599")
        self.assertIsNone(price)


class TestExtractFromSpecsTableCpu(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsCpuSpecs(self):
        html = makeHtml([
            ("CPU Socket", "AM5"),
            ("Number of Cores", "8"),
            ("CPU Base Speed", "4.2 GHz"),
            ("CPU Threads", "16"),
            ("Cache", "96MB"),
            ("CPU Base TDP", "120W"),
            ("CPU Manufacturer", "AMD")
        ])
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "cpu")
        logger.info(f"CPU specs extracted: {result}")
        self.assertEqual(result["socket"], "AM5")
        self.assertEqual(result["coreCount"], "8")
        self.assertEqual(result["coreClock"], "4.2 GHz")
        self.assertEqual(result["threads"], "16")
        self.assertEqual(result["cache"], "96MB")
        self.assertEqual(result["tdp"], "120W")
        self.assertEqual(result["manufacturer"], "AMD")


class TestExtractFromSpecsTableGpu(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsGpuSpecs(self):
        html = makeHtml([
            ("Chipset Manufacturer", "Nvidia"),
            ("Memory Size", "12 GB"),
            ("Memory Type", "GDDR6X"),
            ("Power Consumption", "200W"),
            ("Base Chip Clock", "2310 MHz"),
            ("GPU Length", "336mm")
        ])
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "gpu")
        logger.info(f"GPU specs extracted: {result}")
        self.assertEqual(result["manufacturer"], "Nvidia")
        self.assertEqual(result["memoryGb"], "12 GB")
        self.assertEqual(result["memoryType"], "GDDR6X")
        self.assertEqual(result["tdpWatts"], "200W")
        self.assertEqual(result["coreClock"], "2310 MHz")
        self.assertEqual(result["length"], "336mm")


class TestExtractFromSpecsTableMotherboard(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsMotherboardSpecs(self):
        html = makeHtml([
            ("Manufacturer", "ASUS"),
            ("Socket", "AM5"),
            ("Motherboard Form Factor", "ATX"),
            ("Memory Type", "DDR5"),
            ("Memory Slot", "4"),
            ("Maximum RAM", "128GB"),
            ("Power Requirement (auto)", "15W")
        ])
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "motherboard")
        logger.info(f"Motherboard specs extracted: {result}")
        self.assertEqual(result["manufacturer"], "ASUS")
        self.assertEqual(result["socket"], "AM5")
        self.assertEqual(result["formFactor"], "ATX")
        self.assertEqual(result["memoryType"], "DDR5")
        self.assertEqual(result["memorySlots"], "4")
        self.assertEqual(result["maxMemory"], "128GB")


class TestExtractFromSpecsTableRam(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsRamSpecs(self):
        html = makeHtml([
            ("Manufacturer", "Corsair"),
            ("Memory Size", "32GB"),
            ("Memory DIMM Count", "2"),
            ("Memory Speed", "3200MHz"),
            ("Memory Type", "DDR5")
        ])
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "ram")
        logger.info(f"RAM specs extracted: {result}")
        self.assertEqual(result["manufacturer"], "Corsair")
        self.assertEqual(result["capacityGb"], "32GB")
        self.assertEqual(result["numberOfModules"], "2")
        self.assertEqual(result["speedMhz"], "3200MHz")
        self.assertEqual(result["ddrType"], "DDR5")


class TestExtractFromSpecsTableStorage(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsStorageSpecs(self):
        html = makeHtml([
            ("Manufacturer", "Samsung"),
            ("Drive Capacity", "1TB"),
            ("Read Speed", "7000 MB/s"),
            ("Write Speed", "6500 MB/s"),
            ("Storage Type", "M.2")
        ])
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "storage")
        logger.info(f"Storage specs extracted: {result}")
        self.assertEqual(result["manufacturer"], "Samsung")
        self.assertEqual(result["capacityGb"], "1TB")
        self.assertEqual(result["readSpeed"], "7000 MB/s")
        self.assertEqual(result["writeSpeed"], "6500 MB/s")
        self.assertEqual(result["formFactor"], "M.2")


class TestExtractFromSpecsTablePsu(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsPsuSpecs(self):
        html = makeHtml([
            ("Manufacturer", "Corsair"),
            ("Power", "850W"),
            ("80Plus Rated", "Gold"),
            ("PSU Form Factor", "ATX"),
            ("Modular Cables", "Fully Modular")
        ])
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "psu")
        logger.info(f"PSU specs extracted: {result}")
        self.assertEqual(result["manufacturer"], "Corsair")
        self.assertEqual(result["wattage"], "850W")
        self.assertEqual(result["efficiencyRating"], "Gold")
        self.assertEqual(result["formFactor"], "ATX")
        self.assertEqual(result["modularity"], "Fully Modular")


class TestExtractFromSpecsTableCase(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testExtractsCaseSpecs(self):
        html = makeHtml([
            ("Manufacturer", "NZXT"),
            ("Maximum Motherboard Size Supported", "ATX"),
            ("GPU Length", "380mm"),
            ("PSU Form Factor", "ATX")
        ])
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "cases")
        logger.info(f"Case specs extracted: {result}")
        self.assertEqual(result["manufacturer"], "NZXT")
        self.assertEqual(result["formFactorSupport"], "ATX")
        self.assertEqual(result["gpuMaxLength"], "380mm")
        self.assertEqual(result["psuFormFactorSupport"], "ATX")


class TestExtractFromSpecsTableMissingTable(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testReturnsEmptyDictWhenNoTablePresent(self):
        html = "<html><body><p>No specs here</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = self.scraper.extractFromSpecsTable(fieldMapping, soup, "cpu")
        logger.info(f"Result with no table: {result}")
        self.assertEqual(result, {})


class TestDownloadPartImage(unittest.TestCase):

    def setUp(self):
        logger.info(f"Running {self._testMethodName}")
        self.scraper = makeScraper()

    def testDownloadsAndSavesImage(self):
        html = """
        <html><body>
            <div class="owl-item active">
                <img id="imgImage" data-src="https://example.com/cpu-image.jpg" />
            </div>
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")

        with patch("pcBuildListCompiler.scrapingTools.scraper.requests.get") as mockGet:
            mockGet.return_value.content = makeFakeImageBytes()

            import tempfile
            with tempfile.TemporaryDirectory(prefix="test_image_") as tmpDir:
                logger.info(f"Created temp directory: {tmpDir}")
                self.scraper._projectRoot = tmpDir

                imageTag = soup.find("img", id="imgImage")
                logger.info(f"Image tag found")
                logger.info(f"Image URL: {imageTag.get('data-src')}")

                result = self.scraper.downloadPartImage(soup, "TEST-001", "cpuImages")

                logger.info(f"Returned path: {result}")
                self.assertIsNotNone(result)
                self.assertIn("TEST-001.jpg", result)
                self.assertIn("cpuImages", result)

                import os
                fullPath = os.path.join(tmpDir, result)
                self.assertTrue(os.path.exists(fullPath))
                logger.info(f"Image saved successfully at: {fullPath}")


if __name__ == "__main__":
    unittest.main()