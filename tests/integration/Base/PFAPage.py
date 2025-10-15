import time

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from .BillingPage import BillingPage
from .resources import step_label_texts

class PFAPage(BillingPage):
    def __init__(self, driver, urlSuffix=''):
        super(PFAPage, self).__init__(driver)

        self._wait = 1
        self._step_icon_locator_format = "//*[contains(@class,'mantine-Stepper-stepIcon') and @data-progress='true' and text()='{0}']"
        self._step_label_locator_format = "//*[contains(@class,'mantine-Stepper-stepLabel') and text()='{0}']"
        self._step_radio_button_label_locator_format = "//label[contains(@class,'mantine-Radio-label') and text()='{0}']"
        self.radio_button_name_format = 'Step {0} {1} Radio Button'

        self._ok_button = (By.XPATH, "//*[text()='OK']/../parent::button")
        self._ok_button_disabled = (By.CSS_SELECTOR, "button[disabled]")
        self._step_completed_icon = (By.CSS_SELECTOR, '.mantine-Stepper-stepCompletedIcon > svg')

        # Step 1
        self._step1_yes_radio_button = (By.ID, 'radio-intent')

        # Step 2
        self._step2_yes_radio_button = (By.ID, 'radio-open-access-funds')
        self._step2_no_radio_button = (By.ID, 'radio-open-access-funds_pfa')

        # Step 3
        self._step3_yes_radio_button = (By.ID, 'radio-institutional-funds')
        self._step3_no_radio_button = (By.ID, 'radio-institutional-funds_pfa')

        # Step 4
        self._step4_yes_radio_button = (By.ID, 'radio-grant-funds')
        self._step4_no_radio_button = (By.ID, 'radio-grant-funds_pfa')

        # Step 5
        self._step5_yes_radio_button = (By.ID, 'radio-co-author-funds')
        self._step5_no_radio_button = (By.ID, 'radio-co-author-funds_pfa')

        # Step 6
        self._step6_yes_radio_button = (By.ID, 'radio-other-sources')
        self._step6_no_radio_button = (By.ID, 'radio-other-sources_pfa')

        # Step Partial Funding
        self._step_partial_funding_input = (By.CSS_SELECTOR, "input.mantine-Input-input")

        # Step Documentation
        self._file_input_button = (By.ID, 'PFAFormDocumentationButton')
        self._file_input_label = (By.XPATH,"//label[contains(@class,'mantine-FileInput-label') and contains(@for,'mantine-') and text()='Attach Supporting Documentation']")

        #Alchemer

        self._alchemer_file_input = (By.CSS_SELECTOR, "input[type='file']")
        self._alchemer_submit_button= (By.ID, "sg_NextButton")
        self._alchemer_upload_complete = (By.XPATH, "//div[text()='100%' and @class='sg-progress-bar-text']")


    def select_element_locator(self, element_name):
        if element_name == "OK Button":
            element = self._ok_button
        elif element_name == "Step Completed Icon":
            element = self._step_completed_icon
        elif element_name == "Step 1 Yes Radio Button":
            element = self._step1_yes_radio_button
        elif element_name == "Step 2 Yes Radio Button":
            element = self._step2_yes_radio_button
        elif element_name == "Step 2 No Radio Button":
            element = self._step2_no_radio_button
        elif element_name == "Step 3 Yes Radio Button":
            element = self._step3_yes_radio_button
        elif element_name == "Step 3 No Radio Button":
            element = self._step3_no_radio_button
        elif element_name == "Step 4 Yes Radio Button":
            element = self._step4_yes_radio_button
        elif element_name == "Step 4 No Radio Button":
            element = self._step4_no_radio_button
        elif element_name == "Step 5 Yes Radio Button":
            element = self._step5_yes_radio_button
        elif element_name == "Step 5 No Radio Button":
            element = self._step5_no_radio_button
        elif element_name == "Step 6 Yes Radio Button":
            element = self._step6_yes_radio_button
        elif element_name == "Step 6 No Radio Button":
            element = self._step6_no_radio_button
        elif element_name == "Partial Funding Input":
            element = self._step_partial_funding_input
        elif element_name == "File Input Button":
            element = self._file_input_button
        elif element_name == "File Input Label":
            element = self._file_input_label
        else:
            element = BillingPage.select_element_locator(self, element_name)
        return element

    def ok_button_is_disabled(self):
        self._get(self._ok_button_disabled)

    def navigate_to_step(self, step, button_type):
        if step == 'PartialFunding':
            step_number = 7
        else:
            step_number = int(step)
        if step_number == pytest.current_step:
            return
        elif step_number - 1 > pytest.current_step:
            self.navigate_to_step(step_number - 1, button_type)

        if pytest.current_step == 1:
            button_name = self.radio_button_name_format.format(step_number - 1, 'Yes')
        else:
            button_name = self.radio_button_name_format.format(step_number - 1, button_type)

        self.click_on_element(button_name)
        self.click_on_element('OK Button')

        pytest.current_step = step_number

    def step_icon_and_label_are_present(self):
        if pytest.current_step == 7 and pytest.if_partial_funding:
            step = 'Partial Funding'
        elif pytest.current_step >= 7:
            step = 'Documentation'
        else:
            step = str(pytest.current_step)
        icon_locator = self.create_locator_for_step_icon(step)
        label_locator = self.create_locator_for_step_label(step)
        self._get(icon_locator)
        self._get(label_locator)

    def radio_button_label_is_correct(self, bytton_type):
        label_locator = self.create_locator_for_radio_button_label(str(pytest.current_step), bytton_type)
        self._get(label_locator)

    def create_locator_for_step_icon(self, step):
        if step == 'Documentation':
            if pytest.if_partial_funding:
                icon_text = '8'
            else:
                icon_text = '7'
        else:
            icon_text = [x.get("icon_text") for x in step_label_texts if x.get('step') == step][0]

        return (By.XPATH, self._step_icon_locator_format.format(icon_text))

    def create_locator_for_step_label(self, step_number):
        label_text = [x.get("label_text") for x in step_label_texts if x.get('step') == step_number][0]

        return (By.XPATH, self._step_label_locator_format.format(label_text))

    def create_locator_for_radio_button_label(self, step_number, button_type):
        if button_type == 'Yes':
            field = 'yes_label_text'
        else:
            field = 'no_label_text'

        label_text = [x.get(field) for x in step_label_texts if x.get('step') == step_number][0]

        return (By.XPATH, self._step_radio_button_label_locator_format.format(label_text))

    def number_of_completed_step_icons_is_correct(self):
        completed_icons_number = len(self._gets(self._step_completed_icon))

        assert completed_icons_number == pytest.current_step - 1, \
            'Wron number of Checked Step Icons, Expected: {0}. Actual: {1}'.format(completed_icons_number, pytest.current_step - 1)

    def type_value_in_element(self, element_name, value):
        self._get(self.select_element_locator(element_name)).send_keys(value)

    def verify_value_of_partial_funding_input(self, expected_value):
        actual_value = self._get(self.select_element_locator('Partial Funding Input')).get_attribute("value")

        assert expected_value == actual_value, 'Actual value of Partial Funding Input is wrong. Expected: {0}. Actual: {1}'.format(expected_value, actual_value)

    def verify_url(self, expected_url):
        actual_url = self._driver.current_url

        assert expected_url in actual_url, 'URL is wroing. Expected: {0}. Actual: {1}'.format(expected_url, actual_url)

    def get_cloud_guid(self):
        url = self._driver.current_url

    def upload_file_to_alchemer(self, path):
        self._driver.find_element(*self._alchemer_file_input).send_keys(path)
        time.sleep(3)
        self._get(self._alchemer_submit_button).click()

    def upload_is_successfull(self):
        self._get(self._alchemer_upload_complete)

