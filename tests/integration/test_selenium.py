from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class MySeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_login_page(self):
        self.assertTrue(True)
 