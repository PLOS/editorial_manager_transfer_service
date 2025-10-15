from datetime import datetime
import pytest
import logging, time
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from . import Config as Config
from .EmPage import EmPage as EmPage
from .BillingPage import BillingPage as BillingPage
from .PFAPage import PFAPage as PFAPage
from .RequestObject.salesforce_json import SaleseForceJSON
from .resources import charges

__author__ = 'vkulgavyi@plos.org'

class EmAuthorPage(EmPage):
    def __init__(self, driver, journal, scenario, article_type = 'Research Article'):
        super(EmAuthorPage, self).__init__(driver, journal, scenario, article_type)

        if scenario == 'PFA':
            self._billing_page = PFAPage(driver)
        else:
            self._billing_page = BillingPage(driver)

        self._proceed_button = (By.ID, "proceedButton")

        # Main menu screen
        self._new_manuscript_link = (By.LINK_TEXT, "Submit New Manuscript")

        # Select Manuscript popup
        self._create_new_manuscript_button = (By.NAME, r"ctl01$ctl00")
        self._not_following_revision_button = (By.ID, r"ctl01_BtnNo")

        # Article Type screen
        self._article_type_select = (By.ID, "ddlArticleType")
        self._article_type_option = "Research Article"

        # Attach files screen
        self._file_input = (By.ID, "fileInput")
        self._submission_type_select = (By.ID, "ddSubmissionItemType")
        self._first_row_select = (By.CSS_SELECTOR, "#tblFileInventory > tbody select")
        self._cover_letter_option = "*Cover Letter"
        self._uploading_progress = (By.ID, "lblOverallProgressNumberOfFiles")

        # General Information screen
        self._section_select = (By.ID, "ddlSection")
        if journal == 'PONETEST':
            self._section_option = "Applied Mathematics"
        elif journal == 'PCLMTEST':
            self._section_option = "Energy"
        else:
            self._section_option = "Global Health Security"
        self._section_next_button = (By.CSS_SELECTOR, "#sectionCategoryNext button")
        self._classifications_button = (By.CSS_SELECTOR, "#pnlClassifications button")
        self._expand_all_link = (By.ID, "SelectorControl_lnkBtnExpand2")
        if journal == 'PGPHTEST':
            self._classifications_checkboxes= (By.CSS_SELECTOR, "#M_SelectorControltreeClassCode_1 input[type='checkbox']")
        else:
            self._classifications_checkboxes= (By.CSS_SELECTOR, "input[type='checkbox']")
        self._add_classifications_button = (By.ID, "SelectorControl_btnAdd")
        self._submit_classifacations_button = (By.ID, "btnSubmit2")

        # Review Preferences screen

        # Additional Information screen
        if self.article_type == 'Clinical Trial':
            locator_prefix = 'QR12'
        elif self.article_type == 'Registered Report Protocol':
            locator_prefix = 'QR16'
        elif self.article_type == 'Registered Report':
            locator_prefix = 'QR17'
        elif self.article_type == 'Lab Protocol':
            locator_prefix = 'QR20'
        elif self.article_type == 'Study Protocol':
            locator_prefix = 'QR21'
        else:
            locator_prefix = 'QR10'

        if journal == 'PONETEST':
            self._us_goverment_select = (By.ID, "{}_1_Q73_RSP_73".format(locator_prefix))
            self._financial_disclosure_textarea = (By.ID, "{}_1_Q54712_Q54713_RSP_54713".format(locator_prefix))
            self._competing_interests_textarea = (By.ID, "{}_1_Q116_RSP_116".format(locator_prefix))
            if self.article_type == 'Registered Report Protocol':
                self._data_availability_textarea = (By.ID, "{}_1_Q44638_RSP_44638".format(locator_prefix))
            elif self.article_type == 'Study Protocol':
                self._data_availability_textarea = (By.ID, "{}_1_Q54008_RSP_54008".format(locator_prefix))
            else:
                self._data_availability_textarea = (By.ID, "{}_1_Q559_RSP_559".format(locator_prefix))
            if self.article_type == 'Clinical Trial' or self.article_type == 'Registered Report Protocol' \
                    or self.article_type == 'Study Protocol':
                self._preprint_select = (By.ID, "{}_1_Q54493_RSP_54493".format(locator_prefix))
                self._prior_to_peer_review_select = (By.ID, "{}_1_Q54493_Q54495_RSP_54495".format(locator_prefix))
                self._prior_to_peer_review_option = 'No - do not post my manuscript to medRxiv'
            elif self.article_type == 'Lab Protocol':
                self._preprint_select = (By.ID, "{}_1_Q54035_RSP_54035".format(locator_prefix))
                self._prior_to_peer_review_select = (By.ID, "{}_1_Q54035_Q54037_RSP_54037".format(locator_prefix))
                self._prior_to_peer_review_option = 'No - do not post my manuscript to bioRxiv'
            else:
                self._preprint_select = (By.ID, "{}_1_Q54441_RSP_54441".format(locator_prefix))
                self._prior_to_peer_review_select = (By.ID, "{}_1_Q54441_Q54443_RSP_54443".format(locator_prefix))
                self._prior_to_peer_review_option = 'No - do not post my manuscript to bioRxiv or medRxiv'
            self._institutional_select = (By.ID, "{}_1_Q54695_RSP_54695".format(locator_prefix))
            self._institutions_select = (By.ID, "{}_1_Q54695_Q54696_RSP_54696".format(locator_prefix))
            self._collections_select = (By.ID, "{}_1_Q54658_RSP_54658".format(locator_prefix))
            self._collections_checkbox = (By.ID, "{}_1_Q54658_Q54659_RSP_54659_0".format(locator_prefix))
        elif self.journal == 'PCLMTEST':
            self._us_goverment_select = (By.ID, "QR4_1_Q2626_RSP_2626")
            self._financial_disclosure_textarea = (By.ID, "QR4_1_Q22_RSP_22")
            self._competing_interests_textarea = (By.ID, "QR4_1_Q23_RSP_23")
            self._data_availability_textarea = (By.ID, "QR4_1_Q24_RSP_24")
            self._related_work_textarea = (By.ID, "QR4_1_Q25_RSP_25")
            self._group_autorship_select = (By.ID, "QR4_1_Q2677_RSP_2677")
            self._preprint_select = (By.ID, "QR4_1_Q2688_RSP_2688")
            self._prior_to_peer_review_select = (By.ID, "QR4_1_Q2688_Q2690_RSP_2690")
            self._prior_to_peer_review_option = 'No - do not post my manuscript to EarthArXiv'
            self._institutional_select = (By.ID, "QR4_1_Q2748_RSP_2748")
            self._institutions_select = (By.ID, "QR4_1_Q2748_Q2749_RSP_2749")
            self._collections_select = (By.ID, "QR4_1_Q2694_RSP_2694")
            self._collections_checkbox = (By.ID, "QR4_1_Q2694_RSP_2694")
        else:
            if self.journal == 'PGPHTEST':
                self._related_work_textarea = (By.ID, "QR4_1_Q2027_RSP_2027")
            self._us_goverment_select = (By.ID, "QR4_1_Q2034_RSP_2034")
            self._financial_disclosure_textarea = (By.ID, "QR4_1_Q2023_RSP_2023")
            self._competing_interests_textarea = (By.ID, "QR4_1_Q2024_RSP_2024")
            self._data_availability_textarea = (By.ID, "QR4_1_Q2025_RSP_2025")
            self._preprint_select = (By.ID, "QR4_1_Q2085_RSP_2085")
            self._prior_to_peer_review_select = (By.ID, "QR4_1_Q2085_Q2087_RSP_2087")
            self._prior_to_peer_review_option = 'No - do not post my manuscript to medRxiv'
            self._institutional_select = (By.ID, "QR4_1_Q2153_RSP_2153")
            self._institutions_select = (By.ID, "QR4_1_Q2153_Q2154_RSP_2154")
            self._collections_select = (By.ID, "QR4_1_Q2181_RSP_2181")
            self._collections_checkbox = (By.ID, "QR4_1_Q2181_Q2182_RSP_2182_0")

        self._instutution_name = "Abertay University - C000AU"


        # PONETEST only

        self._select_all_statements_link = (By.LINK_TEXT, "Select All")
        self._financial_disclosure_select = (By.ID, "{}_1_Q54712_RSP_54712".format(locator_prefix))
        self._financial_disclosure_country_select = (By.ID, "{}_1_Q54712_Q54714_RSP_54714".format(locator_prefix))
        self._ethics_statement_textarea = (By.ID, "{}_1_Q109_RSP_109".format(locator_prefix))
        self._figure_guidelines_checkbox = (By.ID, "{}_1_Q119_RSP_119_0".format(locator_prefix))
        self._dual_publication_textarea = (By.ID, "{}_1_Q108_RSP_108".format(locator_prefix))
        self._clinical_trial_textarea = (By.ID, "{}_1_Q35_RSP_35".format(locator_prefix))
        self._group_authorship_select = (By.ID, "{}_1_Q44550_RSP_44550".format(locator_prefix))
        if self.article_type == 'Registered Report Protocol':
            self._data_availability_select = (By.ID, "{}_1_Q44636_RSP_44636".format(locator_prefix))
            self._data_availability_option = 'Yes - any pilot data reported in this submission are fully available and ' \
                                             'data collected during the study will be made fully available without restriction ' \
                                             'upon study completion'
        elif self.article_type == 'Lab Protocol':
            self._data_availability_select = (By.ID, "{}_1_Q54017_RSP_54017".format(locator_prefix))
            self._data_availability_option = 'Yes - sample data are fully available without restriction'
        elif self.article_type == 'Study Protocol':
            self._data_availability_select = (By.ID, "{}_1_Q54006_RSP_54006".format(locator_prefix))
            self._data_availability_option = 'Yes - Results are reported and the data are fully available'
        else:
            self._data_availability_select = (By.ID, "{}_1_Q560_RSP_560".format(locator_prefix))
            self._data_availability_option = 'Yes - all data are fully available without restriction'
        self._subsection_select = (By.ID, "{}_1_Q53979_RSP_53979".format(locator_prefix))
        self._subsection_select_option = 'Agriculture'
        self._regustered_report_confirmation_checkbox = (By.ID, "{}_1_Q44654_RSP_44654_0".format(locator_prefix))
        self._full_title_textarea = (By.ID, "{}_1_Q44652_RSP_44652".format(locator_prefix))
        self._doi_textarea = (By.ID, "{}_1_Q44650_RSP_44650".format(locator_prefix))
        self._doi_protocols_select = (By.ID, "{}_1_Q53993_RSP_53993".format(locator_prefix))
        self._doi_protocols_checkbox = (By.ID, "{}_1_Q53993_Q53995_RSP_53995_0".format(locator_prefix))
        self._clinical_trial_registration_checkbox = (By.ID, "{}_1_Q53999_RSP_53999_0".format(locator_prefix))


        # Comments screen
        self._comments_textarea = (By.ID, "txtComments")

        # Manuscript Data screen
        self._cancel_extracted_button = (By.ID, "cancelExtractedButton")
        self._cancel_confirm_button = (By.ID, "cancelConfirm")
        self._full_title_string = "#cke_fullTitleHtml"
        self._full_title_dialog_string = "cke_editor_fullTitleHtml_dialog"
        self._short_title_textarea = (By.ID, "txtShortTitle")
        self._title_next_button = (By.CSS_SELECTOR, "button.nextButton.next")
        self._abstract_string = "#cke_abstractHtml"
        self._abstract_dialog_string = "cke_editor_abstractHtml_dialog"
        self._abstract_next_button = (By.CSS_SELECTOR, "#abstractAccordion button.nextButton.next")
        self._keywords_next_button = (By.CSS_SELECTOR, "#keywordsNext button.nextButton.next")
        self._edit_author_link = (By.CSS_SELECTOR, "a[title='Edit This Author']")
        self._edit_roles_button = (By.ID, "EditButton")
        self._author_role_checkbox = (By.CSS_SELECTOR, r"#CheckboxList input")
        self._save_author_link = (By.XPATH, r"(//a[@data-toolname='AuthorSave' and @title='Save This Author'])[2]")
        self._authors_next_button = (By.CSS_SELECTOR, "#authorsNext button.nextButton.next")
        self._add_funding_link = (By.CSS_SELECTOR, "#fundingAccordion span.fl-add1 > a")
        self._find_funder_text_item = (By.ID, r"ctl01_FundRefCtrl_searchText")
        self._first_autocomplete_option= (By.CSS_SELECTOR, "ul.ui-autocomplete.ui-front.ui-menu.ui-widget.ui-widget-content > li")
        self._save_funding_link = (By.CSS_SELECTOR, "a[title='Save This Funding Source']")

        # Accept Charges screen
        self._view_charges_button = (By.ID, "ViewChargesButton")
        self._complete_manuscript_button = (By.ID, "btnProceed")

        self._build_pdf_button = (By.ID, "proceedButtonTextID")

        self._main_menu_item = (By.ID, "MainMenu")

        self._manuscript_path = Config.upload_files_base_path + '1.pdf'
        self._cover_letter_path = Config.upload_files_base_path + '2.pdf'

    def create_new_manuscript(self):
        self._get(self._new_manuscript_link).click()
        if self.is_element_present(self._create_new_manuscript_button):
            self.js_click(self._create_new_manuscript_button)
        elif  self.is_element_present(self._not_following_revision_button):
            self.js_click(self._not_following_revision_button)
        else:
            pass

    def select_article_type(self):
        self.handle_select(self._article_type_select, self.article_type)
        pass
        self.js_click(self._proceed_button)

    def attach_files(self):
        self._driver.find_element(*self._file_input).send_keys(self._manuscript_path)
        time.sleep(3)
        while self._driver.find_element(*self._uploading_progress).is_displayed():
            time.sleep(1)
        if self.journal == 'PONETEST':
            self.handle_select(self._first_row_select, "*Manuscript")
        select = self._get(self._submission_type_select)
        time.sleep(1)
        Select(select).select_by_visible_text("*Cover Letter")
        # self.handle_select(self._submission_type_select, "*Cover Letter")
        time.sleep(1)
        self._driver.find_element(*self._file_input).send_keys(self._cover_letter_path)
        time.sleep(3)
        while self._driver.find_element(*self._uploading_progress).is_displayed():
            time.sleep(1)
        self._get(self._proceed_button).click()

    def enter_general_information(self):
        self.handle_select(self._section_select, self._section_option)
        if self.journal == 'PGPHTEST' or self.journal == 'PCLMTEST':
            self.js_click(self._section_next_button)
            self.js_click(self._classifications_button)
            self._driver.switch_to.window(self._driver.window_handles[1])
            self.js_click(self._expand_all_link)
            time.sleep(0.5)

            classifications = self._gets(self._classifications_checkboxes)
            i = 0
            for classification in classifications:
                classification.click()
                time.sleep(0.2)
                if i > 11: break
                i+=1

            self._get(self._add_classifications_button).click()
            self._get(self._submit_classifacations_button).click()
            self._driver.switch_to.window(self._driver.window_handles[0])

            self.handle_frames()

        self.js_click(self._proceed_button)

    def enter_review_preferences(self):
        self._get(self._proceed_button).click()

    def enter_additional_information(self):
        if self.journal in self.one_journals:
            self.enter_additional_information_one()
            return
        if self.journal == 'PCLMTEST':
            self.enter_additional_information_pclm()
            return
        scenario = self.scenario
        self.handle_select(self._us_goverment_select, 'No - No authors are employees of the U.S. government.')
        self.scroll_into_view(self._financial_disclosure_textarea)
        time.sleep(1)
        self.fill_textarea(self._financial_disclosure_textarea, 'test 1')
        self.scroll_into_view(self._competing_interests_textarea)
        self.fill_textarea(self._competing_interests_textarea, 'test 2')
        self.scroll_into_view(self._data_availability_textarea)
        self.fill_textarea(self._data_availability_textarea, 'test 3')
        self.scroll_into_view(self._related_work_textarea)
        self.fill_textarea(self._related_work_textarea, 'test 4')
        self.scroll_into_view(self._preprint_select)
        time.sleep(1)
        self.handle_select(self._preprint_select, 'No')
        self.scroll_into_view(self._prior_to_peer_review_select)
        time.sleep(1)
        self.handle_select(self._prior_to_peer_review_select, self._prior_to_peer_review_option)
        self.scroll_into_view(self._institutional_select)
        time.sleep(1)
        if scenario == 'Institutional':
            self.handle_select(self._institutional_select , 'Yes')
            time.sleep(1)
            self.handle_select(self._institutions_select , self._instutution_name)
        else:
            self.handle_select(self._institutional_select , 'No')
        self.scroll_into_view(self._collections_select)
        time.sleep(1)
        if scenario == 'Collections':
            self.handle_select(self._collections_select, 'Yes')
            self._get(self._collections_checkbox).send_keys(Keys.SPACE)
        else:
            self.handle_select(self._collections_select, 'No')

        time.sleep(1)

        self.js_click(self._proceed_button)

    def enter_additional_information_pclm(self):
        scenario = self.scenario
        self.handle_select(self._us_goverment_select, 'No - No authors are employees of the U.S. government.')
        self.scroll_into_view(self._financial_disclosure_textarea)
        time.sleep(1)
        self.fill_textarea(self._financial_disclosure_textarea, 'test 1')
        self.scroll_into_view(self._competing_interests_textarea)
        self.fill_textarea(self._competing_interests_textarea, 'test 2')
        self.scroll_into_view(self._data_availability_textarea)
        self.fill_textarea(self._data_availability_textarea, 'test 3')
        self.scroll_into_view(self._related_work_textarea)
        self.fill_textarea(self._related_work_textarea, 'test 4')
        self.scroll_into_view(self._group_autorship_select)
        time.sleep(1)
        self.handle_select(self._group_autorship_select, 'No')
        self.scroll_into_view(self._preprint_select)
        self.handle_select(self._preprint_select, 'No')
        time.sleep(1)
        self.scroll_into_view(self._prior_to_peer_review_select)
        time.sleep(1)
        self.handle_select(self._prior_to_peer_review_select, self._prior_to_peer_review_option)
        time.sleep(1)
        self.scroll_into_view(self._institutional_select)
        time.sleep(1)

        if scenario == 'Collections':
            self.handle_select(self._collections_select, 'Yes')
            self._get(self._collections_checkbox).send_keys(Keys.SPACE)

        time.sleep(1)
        if scenario == 'Institutional':
            self.handle_select(self._institutional_select , 'Yes')
            time.sleep(1)
            self.handle_select(self._institutions_select , self._instutution_name)
        self.scroll_into_view(self._collections_select)
        time.sleep(1)

        self.js_click(self._proceed_button)

    def enter_additional_information_one(self):
        scenario = self.scenario
        self.js_click(self._select_all_statements_link)
        self.scroll_into_view(self._us_goverment_select)
        time.sleep(1)
        self.handle_select(self._us_goverment_select, 'No - No authors are employees of the U.S. government.')
        self.scroll_into_view(self._financial_disclosure_select)
        time.sleep(1)
        self.handle_select(self._financial_disclosure_select, 'Yes')
        time.sleep(1)
        self.fill_textarea(self._financial_disclosure_textarea, 'test 1')
        if scenario == 'R4LA':
            country  = 'ANGOLA - AO'
        elif scenario == 'R4LB':
            country  = 'ALBANIA - AL'
        else:
            country  = 'UNITED STATES - US'
        self.scroll_into_view(self._financial_disclosure_country_select)
        time.sleep(1)
        self.handle_select(self._financial_disclosure_country_select, country)
        self.scroll_into_view(self._competing_interests_textarea)
        self.fill_textarea(self._competing_interests_textarea, 'test 2')
        self.scroll_into_view(self._ethics_statement_textarea)
        self.fill_textarea(self._ethics_statement_textarea, 'test 3')
        self.scroll_into_view(self._figure_guidelines_checkbox)
        self._get(self._figure_guidelines_checkbox).send_keys(Keys.SPACE)
        self.scroll_into_view(self._dual_publication_textarea)
        self.fill_textarea(self._dual_publication_textarea, 'test 4')
        if self.article_type == 'Clinical Trial':
            self.scroll_into_view(self._clinical_trial_textarea)
            self.fill_textarea(self._clinical_trial_textarea, 'test clinical trial')
        else:
            self.scroll_into_view(self._group_authorship_select)
            time.sleep(1)
            self.handle_select(self._group_authorship_select, 'No')
        if self.article_type == 'Study Protocol':
            self.scroll_into_view(self._clinical_trial_registration_checkbox)
            self._get(self._clinical_trial_registration_checkbox).send_keys(Keys.SPACE)
        self.scroll_into_view(self._data_availability_select)
        time.sleep(1)
        self.handle_select(self._data_availability_select, self._data_availability_option)
        self.scroll_into_view(self._data_availability_textarea)
        self.fill_textarea(self._data_availability_textarea, 'test 5')
        self.scroll_into_view(self._preprint_select)
        time.sleep(1)
        self.handle_select(self._preprint_select, 'No')
        time.sleep(1)
        self.scroll_into_view(self._prior_to_peer_review_select)
        time.sleep(1)
        self.handle_select(self._prior_to_peer_review_select, self._prior_to_peer_review_option)
        self.scroll_into_view(self._subsection_select)
        time.sleep(1)
        self.handle_select(self._subsection_select, self._subsection_select_option)
        if self.article_type == 'Registered Report Protocol':
            self.scroll_into_view(self._regustered_report_confirmation_checkbox)
            self._get(self._regustered_report_confirmation_checkbox).send_keys(Keys.SPACE)
        if self.article_type == 'Registered Report':
            self.scroll_into_view(self._full_title_textarea)
            self.fill_textarea(self._full_title_textarea, 'test full title')
            self.scroll_into_view(self._doi_textarea)
            self.fill_textarea(self._doi_textarea, 'test doi')
        if self.article_type == 'Lab Protocol':
            self.scroll_into_view(self._doi_protocols_select)
            time.sleep(1)
            self.handle_select(self._doi_protocols_select, 'No')
            self.scroll_into_view(self._doi_protocols_checkbox)
            self._get(self._doi_protocols_checkbox).send_keys(Keys.SPACE)
        self.scroll_into_view(self._institutional_select)
        time.sleep(1)
        if scenario == 'Institutional':
            self.handle_select(self._institutional_select , 'Yes')
            time.sleep(1)
            self.handle_select(self._institutions_select , self._instutution_name)
        else:
            self.handle_select(self._institutional_select , 'No')
        self.scroll_into_view(self._collections_select)
        time.sleep(1)
        if scenario == 'Collections':
            self.handle_select(self._collections_select, 'Yes')
            self._get(self._collections_checkbox).send_keys(Keys.SPACE)
        else:
            self.handle_select(self._collections_select, 'No')

        time.sleep(1)

        self.js_click(self._proceed_button)

    def enter_comments(self):
        self._get(self._proceed_button).click()

    def enter_manuscript_data(self):
        self.cancel_extraction()
        self.fill_editor(self._full_title_string, self._full_title_dialog_string,
                    r"Test Manuscript #{} - {} - Auto-Test - {}. ".format(pytest.i, self.article_type, current_datetime()))
                    # r"Test Manuscript #{} - {} - Vasyl Kulgavyi - {}. ".format(pytest.i, self.article_type, current_datetime()))
        self._get(self._short_title_textarea).send_keys('Test Short Title')
        self.js_click(self._title_next_button)

        self.fill_editor(self._abstract_string , self._abstract_dialog_string, "Test Abstract")
        self.js_click(self._abstract_next_button)

        self.js_click(self._keywords_next_button)

        self.js_click(self._edit_author_link)
        self.js_click(self._edit_roles_button)
        self._get(self._author_role_checkbox).send_keys(Keys.SPACE)
        self._get(self._save_author_link).click()
        self.js_click(self._authors_next_button)

        self.js_click(self._add_funding_link)
        self._get(self._find_funder_text_item).send_keys('Yale')
        time.sleep(2)
        self._get(self._first_autocomplete_option).click()
        time.sleep(2)
        self.js_click(self._save_funding_link)

        time.sleep(1)

        self.js_click(self._build_pdf_button)

        time.sleep(7)

    def cancel_extraction(self):
        if self.is_element_present(self._cancel_extracted_button):
            self.js_click(self._cancel_extracted_button)
            self.js_click(self._cancel_confirm_button)
            time.sleep(1)

    def check_if_proceed_button_is_disabled(self):
        proceed_button = self._wait.until(EC.visibility_of_element_located(
            self._complete_manuscript_button)).wrapped_element
        value = proceed_button.get_attribute("disabled")
        return value == 'true'

    def open_waivers_screen(self):
        driver = self._driver
        self.js_click(self._view_charges_button)
        time.sleep(4)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(1)
        if self.scenario == 'PFA':
            url = self._driver.current_url
            parsed_url = urlparse(url)
            query_dict = parse_qs(parsed_url.query)
            self.cloud_guid = query_dict.get('cloudGuid', [None])[0]

    def charges_correspond_to_scenario(self):
        if self.journal in self.one_journals and self.scenario == 'APC':
            charge = [x for x in charges if x.get('journal') == self.journal and x.get('scenario') == self.scenario
                      and x.get('articleType') == self.article_type][0]
        else:
            charge = [x for x in charges if x.get('journal') == self.journal and x.get('scenario') == self.scenario][0]
        if charge.get('fee') == 'absent':
            self._billing_page.element_is_not_present('Fee')
        else:
            self._billing_page.element_has_test('Fee', charge.get('fee'))
        self._billing_page.element_has_test('Deal Details', charge.get('details'))

    def accept_charges(self):
        self._billing_page.click_on_element("Accept Button")
        self._driver.switch_to.window(self._driver.window_handles[0])

    def charges_are_accpted(self):
        driver = self._driver
        self.js_click(self._view_charges_button)
        time.sleep(4)
        driver.switch_to.window(driver.window_handles[1])
        # self._billing_page = BillingPage(driver)
        self._billing_page.element_is_not_present('Accept Button')
        self._billing_page.element_is_present('OK Button')
        self._billing_page.click_on_element("OK Button")
        driver.switch_to.window(driver.window_handles[0])

    def complete_manuscript(self):
        self.js_click(self._complete_manuscript_button)
        time.sleep(2)

    def click_main_manuscript_menu(self):
        self._driver.switch_to.default_content()
        self.js_click(self._main_menu_item)
        time.sleep(5)


    def apply_for_pfa(self, answers):
        if answers == 'Yes':
            self.able_to_pay = 100
        else:
            self.able_to_pay = 0

        self._billing_page.click_on_element('Unable To Pay Link')

        self._billing_page.navigate_to_step('7', answers)
        if answers == 'Yes':
            self._billing_page.type_value_in_element('Partial Funding Input', str(self.able_to_pay))
            self._billing_page.click_on_element('OK Button')

        self._billing_page.click_on_element('OK Button')

    def verify_url(self, url):
        self._billing_page.verify_url(url)

    def upload_file_to_alchemer(self):
        self._billing_page.upload_file_to_alchemer(self._manuscript_path)

    def query_salesforce(self):
        sf = SaleseForceJSON(self.journal, self.cloud_guid)
        sf.get_access_token()
        sf.query_cases()
        sf.verify_case(self.able_to_pay)

def current_datetime():
    current_datetime = datetime.now()
    return current_datetime.strftime("%Y-%m-%d %H:%M:%S")







