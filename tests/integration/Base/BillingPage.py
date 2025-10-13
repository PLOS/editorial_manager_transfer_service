__author__ = "Joshua Lavarine"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from . import Config as Config
from .resources import documents
from plos_test.BasePage import BasePage

class BillingPage(BasePage):
    def __init__(self, driver, document='', urlSuffix=''):
        super(BillingPage, self).__init__(driver)

        # Locators - Instance variables unique to each instance
        self._title= (By.XPATH, "//h1[text()='PLOS Publication Fee']")
        self._description_heading= (By.XPATH, "//h1[text()='Review your publication fee']")
        self._fee_heading = (By.XPATH, "//h1[text()='Expected Publication Fee:']")
        self._accept_button = (By.XPATH, "//span[contains(@class, 'mantine-Button-label') and text()='I agree to pay the publication fee']")
        self._ok_button = (By.XPATH, "//span[contains(@class, 'mantine-Button-label') and text()='OK']")
        self._unable_to_pay_link = (By.LINK_TEXT, "I am unable to pay")
        self._fee = (By.ID, "price")
        self._deal_details = (By.ID, "deal-details")

    def select_element_locator(self, element_name):
        if element_name == "Title":
            element = self._title
        elif element_name == "Description Heading":
            element = self._description_heading
        elif element_name == "Fee Heading":
            element = self._fee_heading
        elif element_name == "OK Button":
            element = self._ok_button
        elif element_name == "Accept Button":
            element = self._accept_button
        elif element_name == "Unable To Pay Link":
            element = self._unable_to_pay_link
        elif element_name == "Fee":
            element = self._fee
        elif element_name == "Deal Details":
            element = self._deal_details
        else:
            raise ValueError('Element {0} is not described in Page class'.format(element_name))
        return element

    def element_is_present(self, element_name):
        self._get(self.select_element_locator(element_name))

    def element_is_not_present(self, element_name):
        self._check_for_absence_of_element_not_visibility(self.select_element_locator(element_name))

    def element_is_not_visible(self, element_name):
        self._check_for_absence_of_element(self.select_element_locator(element_name))

    def click_on_element(self, element_name):
        self._get(self.select_element_locator(element_name)).click()

    def element_has_test(self, element_name, expected_text):
        element = self._get(self.select_element_locator(element_name))
        actual_text = element.text
        assert str(expected_text) in actual_text, 'Element {0} doesn\'t have text {1}'.format(element_name, expected_text)

