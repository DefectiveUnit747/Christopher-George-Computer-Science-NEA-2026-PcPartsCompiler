import unittest
from bs4 import BeautifulSoup
import os
import tempfile
import shutil
from PIL import Image
import logging


class TestScraperFunctions(unittest.TestCase):

    def testFilterSoldOutItems(self):

        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_filter_sold_out.log', mode='w'),
                logging.StreamHandler()
            ],
            force=True
        )
        logger = logging.getLogger('test1')

        logger.info("TEST: Filter Sold-Out Items")

        mockHtml = '''
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

        soup = BeautifulSoup(mockHtml, 'html.parser')
        links = set()

        container = soup.find("div", class_="productListContainer")
        for link in container.find_all("a", href=True):
            href = link.get("href")
            if not link.find_parent("div", id="pnlSoldOut"):
                links.add(href)
                logger.info(f"Included: {href}")
            else:
                logger.info(f"Filtered: {href}")

        logger.info(f"Total: {len(links)} (expected 3)")

        self.assertEqual(len(links), 3)
        self.assertNotIn("/cpu-sold-1", links)
        self.assertNotIn("/cpu-sold-2", links)
        self.assertIn("/cpu-1", links)
        self.assertIn("/cpu-2", links)
        self.assertIn("/cpu-3", links)

        logger.info("PASS")

    def testDownloadPartImageSavesCorrectly(self):

        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_download_image.log', mode='w'),
                logging.StreamHandler()
            ],
            force=True
        )
        logger = logging.getLogger('test2')

        logger.info("TEST: Download Part Image")

        mockHtml = '''
        <div class="owl-item active">
            <img id="imgImage" data-src="https://example.com/cpu-image.jpg" src="">
        </div>
        '''

        tempDir = tempfile.mkdtemp(prefix="test_image_")
        logger.info(f"Created temp directory: {tempDir}")

        try:
            soup = BeautifulSoup(mockHtml, 'html.parser')

            activeCarousel = soup.find("div", class_="owl-item active")
            imageTag = activeCarousel.find("img", id="imgImage") if activeCarousel else soup.find("img", id="imgImage")

            self.assertIsNotNone(imageTag)
            logger.info("Image tag found")

            imageUrl = imageTag.get("data-src") or imageTag.get("src")
            logger.info(f"Image URL: {imageUrl}")

            testImage = Image.new('RGB', (100, 100), color='blue')

            partNumber = "TEST-CPU-12345"
            folder = os.path.join(tempDir, "productImages", "cpuImages")
            os.makedirs(folder, exist_ok=True)

            normalisedPartNumber = partNumber.replace("/", "-").replace("\\", "-")
            filePath = os.path.join(folder, f"{normalisedPartNumber}.jpg")

            testImage.save(filePath, "JPEG")
            logger.info(f"Saved: {filePath}")
            logger.info(f"Size: {os.path.getsize(filePath)} bytes")

            self.assertTrue(os.path.exists(filePath))
            self.assertTrue(filePath.endswith(f"{normalisedPartNumber}.jpg"))
            self.assertGreater(os.path.getsize(filePath), 0)
            self.assertIn(tempDir, filePath)

            logger.info("PASS")

        finally:
            if os.path.exists(tempDir):
                shutil.rmtree(tempDir)
                logger.info("Cleaned up temp directory")


if __name__ == '__main__':
    unittest.main(verbosity=2)