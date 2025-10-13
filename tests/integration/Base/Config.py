import logging
from smart_getenv import getenv

# === Logging Level ===
logging.basicConfig(level=logging.INFO)

"""
Set **WEBDRIVER_ENVIRONMENT** env variable/default value run tests against the site 
defined by `base_url` variable

Set **WEBDRIVER_TARGET_URL** env variable/default value to desired URL to run suite against it
"""
