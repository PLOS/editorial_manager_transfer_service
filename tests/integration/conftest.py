from plos_test.conftest.Web import *
from plos_test.conftest.Bdd import *
from pytest_bdd import given, when, then, parsers

from .Base.BillingPage import BillingPage

@given(parsers.re("User opens (?P<document>[a-zA-Z0-9]*) Billing page"))
@when(parsers.re("User opens (?P<document>[a-zA-Z0-9]*) Billing page"))
def logn_page_is_opened(driver_get_bdd, document):
    pytest.driver = driver_get_bdd
    pytest.test_page = BillingPage(pytest.driver, document)
    pytest.document = document

@then(parsers.re(r"Element '(?P<name>[a-zA-Z0-9_ ]*)' is present"))
@then(parsers.re(r"Element '(?P<name>[a-zA-Z0-9_ ]*)' is present and correct"))
@then(parsers.re(r"Element '(?P<name>[a-zA-Z0-9_ ]*)' is visible"))
def element_is_present(name):
    pytest.test_page.element_is_present(name)

@then(parsers.re(r"Element '(?P<name>[a-zA-Z0-9_ ]*)' is not present"))
def element_is_not_present(name):
    pytest.test_page.element_is_not_present(name)

@then(parsers.re(r"Element '(?P<name>[a-zA-Z0-9_ ]*)' is not visible"))
def element_is_not_present(name):
    pytest.test_page.element_is_not_visible(name)

@when(parsers.re(r"User clicks on '(?P<name>[a-zA-Z0-9_ ]*)'"))
def user_clicks_on_element(name):
    if name == 'OK Button':
        pytest.current_step += 1
    elif 'Yes Radio Button' in name:
        pytest.if_partial_funding = True
    pytest.test_page.click_on_element(name)




