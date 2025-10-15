import pytest, time, logging
from pytest_bdd import scenario, given, when, then, parsers

from ..Base.EmAuthorPage import EmAuthorPage

@scenario("EM_Workflows.feature", "New Manuscript creation for PCLMTEST", features_base_dir="integration/Features")
def test_new_manuscript_pclmtest(driver_get_bdd):
    pass

@scenario("EM_Workflows.feature", "New Manuscript creation", features_base_dir="integration/Features")
def test_new_manuscript(driver_get_bdd):
    pass

@scenario("EM_Workflows.feature", "New Manuscript creation for PONETEST", features_base_dir="integration/Features")
def test_new_manuscript_ponetest(driver_get_bdd):
    pass

@scenario("EM_Workflows.feature", "PFA scenario", features_base_dir="integration/Features")
def test_pfa_scenario(driver_get_bdd):
    pass

@when(parsers.re("User logins to EM for journal (?P<journal>[a-zA-Z]*) for article type '(?P<article_type>[a-zA-Z() ]*)' and scenario (?P<scenario>[a-zA-Z0-9]*)"))
def user_logins_to_em_with_article_type(driver_get_bdd, journal, scenario, article_type):
    driver = driver_get_bdd
    pytest.driver = driver
    pytest.test_page = EmAuthorPage(driver, journal, scenario, article_type)
    pytest.test_page.login()

@when(parsers.re("User logins to EM for journal (?P<journal>[a-zA-Z]*) for scenario (?P<scenario>[a-zA-Z0-9]*)"))
def user_logins_to_em(driver_get_bdd, journal, scenario):
    driver = driver_get_bdd
    pytest.driver = driver
    pytest.test_page = EmAuthorPage(driver, journal, scenario)
    pytest.test_page.login()

@when("100 manuscripts are created")
def manuscripts_are_created():
    for i in range(74, 101):
        pytest.i = i
        user_clicks_new_manuscript()
        user_selects_article_type()
        user_attaches_files()
        user_enters_general_information()
        User_skips_Review_Preferences()
        User_enters_Additional_Information()
        User_enters_Comments()
        User_enters_Manuscript_Data()
        pytest.test_page.click_main_manuscript_menu()
        with open("output.txt", "w") as file:
            file.write(f"{i}\n")

@when("User clicks New Manuscript")
def user_clicks_new_manuscript():
    pytest.test_page.handle_frames()
    pytest.test_page.create_new_manuscript()

@when("User selects Article Type")
def user_selects_article_type():
    pytest.test_page.handle_frames()
    pytest.test_page.select_article_type()

@when("User attaches files")
def user_attaches_files():
    pytest.test_page.handle_frames()
    pytest.test_page.attach_files()

@when("User enters General Information")
def user_enters_general_information():
    pytest.test_page.handle_frames()
    pytest.test_page.enter_general_information()

@when("User enters Review Preferences")
def User_skips_Review_Preferences():
    pytest.test_page.handle_frames()
    pytest.test_page.enter_review_preferences()

@when(parsers.re("User enters Additional Information"))
def User_enters_Additional_Information():
    pytest.test_page.handle_frames()
    pytest.test_page.enter_additional_information()

@when("User enters Comments")
def User_enters_Comments():
    pytest.test_page.handle_frames()
    pytest.test_page.enter_comments()

@when("User enters Manuscript Data")
def User_enters_Manuscript_Data():
    pytest.test_page.handle_frames()
    pytest.test_page.enter_manuscript_data()

@then("Proceed button is disabled")
def proceed_button_is_disabled():
    # time.sleep(6)
    pytest.test_page.handle_frames()
    assert pytest.test_page.check_if_proceed_button_is_disabled(), 'Proceed Button is enabled'
    # pytest.test_page.open_waivers_screen()

@then(parsers.re("Charges correspond to scenario (?P<scenario>[a-zA-Z]*)"))
def charges_correspond_to_scenario(scenario):
    pytest.test_page.open_waivers_screen()
    pytest.test_page.charges_correspond_to_scenario()

@when("User accepts Charges")
def user_accepts_charges():
    pytest.test_page.accept_charges()
    time.sleep(3)

@then("Proceed button is enabled")
def proceed_button_is_disabled():
    pytest.test_page.handle_frames()
    assert not pytest.test_page.check_if_proceed_button_is_disabled(), 'Proceed Button is disabled'

@then("Charges are accepted in Waivers window")
def charges_are_accepted_in_waivers_window():
    pytest.test_page.charges_are_accpted()

@when("User completed Manuscript")
def User_accepts_Charges():
    pytest.test_page.handle_frames()
    pytest.test_page.complete_manuscript()

@when(parsers.re("User applies for PFA with (?P<answers>[a-zA-Z]*) answers"))
def user_applies_for_pfa(answers):
    pytest.current_step = 1
    pytest.test_page.open_waivers_screen()
    pytest.test_page.apply_for_pfa(answers)

@then("Alchemer page is opened")
def alchemer_page_is_opened():
    time.sleep(5)
    pytest.test_page.verify_url('alchemer.com')

@when("User uploads a file to Alchemer")
def user_uploads_file_to_lchemer():
    pytest.test_page.upload_file_to_alchemer()

@then("Upload is successfull")
def upload_is_successfull():
    pytest.test_page._billing_page.upload_is_successfull()
    pytest.driver.switch_to.window(pytest.driver.window_handles[0])

@then("SalesForce Case has corrent information")
def salesforce_case_has_corrent_information():
    pytest.test_page.query_salesforce()









