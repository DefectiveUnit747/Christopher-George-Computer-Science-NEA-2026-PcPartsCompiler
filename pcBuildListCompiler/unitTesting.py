import unittest
from unittest.mock import Mock, patch, MagicMock, call
from bs4 import BeautifulSoup
import io
from PIL import Image
import os
import sys

class TestGetProductLinks(unittest.TestCase):

    def parseLinks(self, html, baseUrl="https://www.cclonline.com"):
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        container = soup.find("div", class_="productListContainer")
        # Find the one div that holds all the product links on the page

        if container:
            # Only proceed if the container div actually exists

            for link in container.find_all("a", href=True):
                # Loop through every <a> tag that has an href attribute

                href = link.get("href")
                # Pull the href value out of the tag, e.g. "/product/amd-ryzen-7"

                if "page_" in href or "javascript" in href or "#" in href:
                    continue
                # Skip pagination links, javascript links, and anchor links
                # "continue" jumps straight to the next iteration of the loop

                if link.find_parent("div", id="pnlSoldOut"):
                    continue
                # If this link is inside a sold-out div, skip it
                # find_parent() walks up the HTML tree looking for that div

                links.add(baseUrl + href)
                # Prepend the base URL to make a full valid URL
                # e.g. "https://www.cclonline.com" + "/product/amd-ryzen-7"

        return links
        # Return the complete set of valid, in-stock product URLs

    # ---------------------------------------------------------------

    def test_extractsValidProductUrls(self):
        """Test #1: Returns valid product URLs from productListContainer"""

        html = """
        <div class="productListContainer">
            <a href="/product/amd-ryzen-7">AMD Ryzen 7</a>
            <a href="/product/intel-i9">Intel i9</a>
            <a href="/product/amd-ryzen-5">AMD Ryzen 5</a>
        </div>
        """
        # Our fake HTML - three normal in-stock product links

        result = self.parseLinks(html)
        # Call our helper with the fake HTML

        self.assertEqual(len(result), 3)
        # Assert exactly 3 links were returned

        self.assertIn("https://www.cclonline.com/product/amd-ryzen-7", result)
        self.assertIn("https://www.cclonline.com/product/intel-i9", result)
        self.assertIn("https://www.cclonline.com/product/amd-ryzen-5", result)
        # Assert each expected full URL is present in the result set

    # ---------------------------------------------------------------

    def test_filtersSoldOutItems(self):
        """Test #3: Skips links inside pnlSoldOut div"""

        html = """
        <div class="productListContainer">
            <a href="/product/in-stock">In Stock CPU</a>
            <div id="pnlSoldOut">
                <a href="/product/sold-out">Sold Out CPU</a>
            </div>
        </div>
        """
        # One in-stock link, one sold-out link wrapped in pnlSoldOut

        result = self.parseLinks(html)

        self.assertEqual(len(result), 1)
        # Only 1 link should come back

        self.assertIn("https://www.cclonline.com/product/in-stock", result)
        # The in-stock link should be present

        self.assertNotIn("https://www.cclonline.com/product/sold-out", result)
        # The sold-out link must NOT be present

    # ---------------------------------------------------------------

    def test_skipsPaginationLinks(self):
        """Test #2: Skips page_, javascript, and # links"""

        html = """
        <div class="productListContainer">
            <a href="/product/valid">Valid Product</a>
            <a href="/product/page_2">Page 2</a>
            <a href="javascript:void(0)">JS Link</a>
            <a href="#top">Anchor</a>
        </div>
        """
        # One valid product link mixed in with three invalid link types

        result = self.parseLinks(html)

        self.assertEqual(len(result), 1)
        # Only the one valid link should come back

        self.assertIn("https://www.cclonline.com/product/valid", result)
        # And it should be the correct one

    # ---------------------------------------------------------------

    def test_returnsEmptyWhenNoContainer(self):
        """Returns empty set when productListContainer is missing"""

        html = "<div>No product container here</div>"
        # HTML with no productListContainer div at all

        result = self.parseLinks(html)

        self.assertEqual(result, set())
        # Should return an empty set, not crash


if __name__ == "__main__":
    unittest.main(verbosity=2)
    # verbosity=2 prints each test name and result as it runs