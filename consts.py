import os

from django.conf import settings

# Plugin Settings
PLUGIN_NAME = 'Editorial Manager Transfer Service Plugin'
DISPLAY_NAME = 'Editorial Manager Transfer Service'
DESCRIPTION = 'A plugin to provide information for Aries\' Editorial Manager to enable automatic transfers.'
AUTHOR = 'PLOS'
VERSION = '0.1'
SHORT_NAME = 'editorial_manager_transfer_service'
MANAGER_URL = 'editorial_manager_transfer_service_manager'
JANEWAY_VERSION = "1.8.0"

# Setting Configuration
PLUGIN_SETTINGS_GROUP_NAME = "plugin:editorial_manager_transfer_service"
PLUGIN_SETTINGS_LICENSE_CODE = "license_code"
PLUGIN_SETTINGS_JOURNAL_CODE = "journal_code"
PLUGIN_SETTINGS_SUBMISSION_PARTNER_CODE = "submission_partner_code"

# Import and export filepaths
EXPORT_FILE_PATH = os.path.join(settings.BASE_DIR, 'files', 'plugins', 'editorial-manager-transfer-service', 'export')
IMPORT_FILE_PATH = os.path.join(settings.BASE_DIR, 'files', 'plugins', 'editorial-manager-transfer-service', 'import')

# XML File
GO_FILE_ELEMENT_TAG_GO = "GO"
GO_FILE_GO_ELEMENT_ATTRIBUTE_XMLNS_XSI_KEY = "xmlns:xsi"
GO_FILE_GO_ELEMENT_ATTRIBUTE_XMLNS_XSI_VALUE = "http://www.w3.org/2001/XMLSchema-instance"
GO_FILE_GO_ELEMENT_ATTRIBUTE_SCHEMA_LOCATION_KEY = "xsi:noNamespaceSchemaLocation"
GO_FILE_GO_ELEMENT_ATTRIBUTE_SCHEMA_LOCATION_VALUE = "app://Aries.EditorialManager/Resources/XmlDefineTransformFiles/aries_import_go_file.xsd"
