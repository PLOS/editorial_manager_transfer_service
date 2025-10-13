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
