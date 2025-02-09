from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, Optional, Tuple
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumTestGenerator:
    def __init__(self, headless: bool = True):
        """
        Initialize the Selenium test generator.

        Args:
            headless (bool): Run the browser in headless mode (default: True).
        """
        self.headless = headless
        self.driver = None

    def initialize_driver(self):
        """Initialize the Selenium WebDriver with optional headless mode."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def generate_ui_test(self, ui_element_info: Dict) -> Tuple[bool, Optional[str]]:
        """
        Generate a Selenium-based UI test for a given web element.

        Args:
            ui_element_info (Dict): A dictionary containing the UI element's metadata.

        Returns:
            Tuple[bool, Optional[str]]: (success, test_code)
        """
        if not self.driver:
            self.initialize_driver()

        element_id = ui_element_info.get("id")
        element_xpath = ui_element_info.get("xpath")
        element_name = ui_element_info.get("name", "element")

        try:
            # Generate the test code
            test_code = f"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_{element_name}_interaction(driver):
    driver.get("https://example.com")
    try:
        # Locate the element
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.{'ID' if element_id else 'XPATH'}, "{element_id if element_id else element_xpath}"))
        )
        # Perform actions (e.g., click, type)
        element.click()
        # Add assertions here
        assert element.is_displayed(), "Element is not displayed"
    except Exception as e:
        pytest.fail(f"Test failed: {e}")
"""
            logger.info(f"Generated UI test for element: {element_name}")
            return True, test_code

        except Exception as e:
            logger.error(f"Failed to generate UI test: {e}")
            return False, None

    def execute_ui_test(self, test_code: str) -> bool:
        """
        Execute a generated Selenium test.

        Args:
            test_code (str): The generated test code to execute.

        Returns:
            bool: True if the test passed, False otherwise.
        """
        try:
            # Save the test code to a temporary file
            test_file = Path("temp_ui_test.py")
            with open(test_file, "w") as f:
                f.write(test_code)

            # Execute the test using pytest
            import subprocess
            result = subprocess.run(["pytest", str(test_file)], capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("UI test executed successfully.")
                return True
            else:
                logger.error(f"UI test failed:\n{result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error executing UI test: {e}")
            return False

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed.")