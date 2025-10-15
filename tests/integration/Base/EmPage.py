import logging
import time

from plos_test.CustomException import ElementDoesNotExistAssertionError
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from . import Config as Config
from .resources import documents
from plos_test.BasePage import BasePage
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.file_detector import LocalFileDetector

__author__ = 'vkulgavyi@plos.org'

class EmPage(BasePage):
    def __init__(self, driver, journal, scenario, article_type):
        super(EmPage, self).__init__(driver)

        if not hasattr(self._driver, 'navigated'):

            base_url = 'https://www.editorialmanager.com/{}/default2.aspx'.format(journal)
            try:
                self._driver.get(base_url)
                self._driver.navigated = True
            except TimeoutException as toe:
                print(
                    '\t[WebDriver Error] WebDriver timed out while trying to load the requested '
                    'web page "%s".' % base_url)
                raise toe

        self.journal = journal
        self.scenario = scenario
        self.article_type = article_type
        self.em_credentials = Config.em_credentials[journal]

        self.one_journals = ['PONETEST']

        self._driver.file_detector = LocalFileDetector()

        self.editor_locator_template = "{} a.cke_button.cke_button__paste"
        self.editor_dialog_locator_template = '.{} iframe.cke_pasteframe'
        self.editor_dialog_ok_button_locator_template = '.{} div.cke_dialog_body span.cke_dialog_ui_button'

        # Login screen
        self._user_name = (By.ID, "username")
        self._password = (By.ID, "passwordTextbox")
        self._author_button = (By.NAME, "authorLogin")

    def login(self):
        self._driver.switch_to.frame("content")
        self._driver.switch_to.frame("login")
        if self.scenario == 'R4LA':
            username = self.em_credentials['username_r4la']
            password = self.em_credentials['password_r4la']
        elif self.scenario == 'R4LB':
            username = self.em_credentials['username_r4lb']
            password = self.em_credentials['password_r4lb']
        else:
            username = self.em_credentials['username_regular']
            password = self.em_credentials['password_regular']
        self._get(self._user_name).send_keys(username)
        self._get(self._password).send_keys(password)
        self._get(self._author_button).click()
        time.sleep(4)

    def handle_frames(self):
        time.sleep(4)
        self._driver.switch_to.default_content()
        self._driver.switch_to.frame("content")

    def handle_select(self, locator, text):
        # self.scroll_into_view(locator)
        element = self._get(locator)
        # element.click()
        # Select(element).select_by_visible_text(text)
        result = self._driver.execute_script("""
        var found = false;
        for (var i = 0; i < arguments[0].options.length; i++) {
            if (arguments[0].options[i].text === '""" + text + """') {
                arguments[0].selectedIndex = i;
                arguments[0].dispatchEvent(new Event('change'));
                found = true;
                break;
            }
        }
        return found;
        """, element)

        if not result:
            raise NoSuchElementException(f"Option '{text}' was not found")

    def fill_textarea(self, locator, text):
        element = self._get(locator)
        self._driver.execute_script("""
        arguments[0].value = '""" + text + """';
        arguments[0].dispatchEvent(new Event('change'));""", element)

        time.sleep(0.5)

    def fill_editor(self, locator_string, dialog_locator_string, text):
        driver = self._driver
        locator = (By.CSS_SELECTOR, self.editor_locator_template.format(locator_string))
        self._get(locator).click()
        dialog_locator = (By.CSS_SELECTOR, self.editor_dialog_locator_template.format(dialog_locator_string))
        driver.switch_to.frame(self._get(dialog_locator))
        element = driver.find_element_by_css_selector('body')
        driver.execute_script("arguments[0].innerHTML = arguments[1];", element, text)
        driver.switch_to.parent_frame()
        dialog_ok_button_locator = (By.CSS_SELECTOR, self.editor_dialog_ok_button_locator_template.format(dialog_locator_string))
        self._get(dialog_ok_button_locator).click()

    def scroll_into_view(self, locator):
        element = self._driver.find_element(*locator)
        self._driver.execute_script("javascript:arguments[0].scrollIntoView()",
                                     element)
        time.sleep(1)

    def wait_for_page(self):
        WebDriverWait(self._driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def _get(self, locator):
        try:
            return self._wait.until(EC.element_to_be_clickable(
                locator)).wrapped_element
        except TimeoutException:
            logging.error(
                '\t[WebDriver Error] WebDriver timed out while trying to '
                'identify '
                'element by {0!s}.'.format(locator))
            raise ElementDoesNotExistAssertionError(locator)

    def js_click(self, locator):
        element = self._get(locator)
        self._driver.execute_script("arguments[0].click();", element);

    def is_element_present(self, locator):
        timeout = 1
        self.set_timeout(timeout)
        try:
            self._wait.until(EC.visibility_of_element_located(
                locator))
            return True
        except Exception:
            return False
        finally:
            self.restore_timeout()






