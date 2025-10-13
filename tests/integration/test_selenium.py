from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from plos_test import WebDriverManager  # Or whatever plos_test provides
from plos_test.pages.BillingPage import BillingPage


class BillingPageTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Use plos_test's driver management
        cls.driver_manager = WebDriverManager()  # Check plos_test docs for actual class
        cls.driver = cls.driver_manager.get_driver()

    @classmethod
    def tearDownClass(cls):
        cls.driver_manager.cleanup()  # Or whatever cleanup method plos_test provides
        super().tearDownClass()

    def test_billing_page_elements(self):
        # Navigate using Django's live server URL
        self.driver.get(f'{self.live_server_url}/billing/')
        
        # Your BillingPage should work as-is
        billing_page = BillingPage(self.driver)
        billing_page.element_is_present("Title")
        billing_page.element_has_test("Fee", "$2950")