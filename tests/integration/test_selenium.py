import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

class BasicSeleniumTest(unittest.TestCase):
    def setUp(self):
        chromedriver_autoinstaller.install()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

    def test_homepage_title(self):
        self.driver.get("http://localhost:8000")  # Adjust URL if needed
        self.assertIn("Janeway", self.driver.title)

    def tearDown(self):
        self.driver.quit()
