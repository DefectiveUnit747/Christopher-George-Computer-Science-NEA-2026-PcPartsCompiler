# fakes selenium/undetected_chromedriver so tests run without installs
from unittest.mock import MagicMock
import sys

for mod in [
    "selenium", "selenium.webdriver", "selenium.webdriver.support",
    "selenium.webdriver.support.ui", "selenium.webdriver.support.expected_conditions",
    "selenium.webdriver.common", "selenium.webdriver.common.by",
    "selenium.common", "selenium.common.exceptions",
    "undetected_chromedriver"]:
    sys.modules[mod] = MagicMock()