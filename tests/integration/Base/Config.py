import logging
from smart_getenv import getenv

# === Logging Level ===
logging.basicConfig(level=logging.INFO)

"""
Set **WEBDRIVER_ENVIRONMENT** env variable/default value run tests against the site 
defined by `base_url` variable

Set **WEBDRIVER_TARGET_URL** env variable/default value to desired URL to run suite against it
"""

# Environment variables
# environment = getenv('WEBDRIVER_ENVIRONMENT', default='dev')
# base_url = getenv('WEBDRIVER_TARGET_URL', default='https://www.editorialmanager.com/pgphtest/default2.aspx/')

pfa_email = 'autotest@plos.org'

upload_files_base_path = getenv('UPLOAD_BASE_PATH', default='/builds/plos/billing-frontend/test/end_to_end/files/')

# API_BASE_HOST = getenv('API_BASE_HOST', default='https://billing-dev.plos.org')

firestore_project_ic = getenv("GCP_PROJECT", default="plos-dev")
firestore_collection_name = getenv("FIRESTORE_COLLECTION_NAME", default="billing-quote")

em_credentials = {
    'PCLMTEST': {
        'username_regular': getenv('PCLMTEST_REG_USERNAME', default='AutoTestAutoTest'),
        'password_regular': getenv('PCLMTEST_REG_PASSWORD'),
    },
    'PGPHTEST': {
        'username_regular': getenv('PGPHTEST_REG_USERNAME', default='AutoTestAutoTest'),
        'password_regular': getenv('PGPHTEST_REG_PASSWORD'),
        'username_r4la': getenv('PGPHTEST_R4LA_USERNAME', default='AutoTest1AutoTest1'),
        'password_r4la': getenv('PGPHTEST_R4LA_PASSWORD'),
        'username_r4lb': getenv('PGPHTEST_R4LB_USERNAME', default='AutoTest2AutoTest2'),
        'password_r4lb': getenv('PGPHTEST_R4LB_PASSWORD')
    },
    'PONETEST': {
        'username_regular': getenv('PONETEST_REG_USERNAME', default='AutoTestAutoTest'),
        'password_regular': getenv('PONETEST_REG_PASSWORD'),
        'username_r4la': getenv('PONETEST_R4LA_USERNAME', default='AutoTest1AutoTest1'),
        'password_r4la': getenv('PONETEST_R4LA_PASSWORD'),
        'username_r4lb': getenv('PONETEST_R4LB_USERNAME', default='AutoTest2AutoTest2'),
        'password_r4lb': getenv('PONETEST_R4LB_PASSWORD')
    }
}

salesforce_credentials = {
    'client_id': getenv('SF_CLIENT_ID'),
    'client_secret': getenv('SF_CLIENT_SECRET'),
    'username': getenv('SF_USERNAME'),
    'password': getenv('SF_PASSWORD'),
    'token': getenv('SF_TOKEN')

}
