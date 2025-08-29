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
GO_FILE_ELEMENT_TAG_HEADER = "header"
GO_FILE_ELEMENT_TAG_VERSION = "version"
GO_FILE_VERSION_ELEMENT_ATTRIBUTE_NUMBER_KEY = "number"
GO_FILE_VERSION_ELEMENT_ATTRIBUTE_NUMBER_VALUE = "1.0"
GO_FILE_ELEMENT_TAG_JOURNAL = "journal"
GO_FILE_JOURNAL_ELEMENT_ATTRIBUTE_CODE_KEY = "code"
GO_FILE_ELEMENT_TAG_IMPORT_TYPE = "import-type"
GO_FILE_IMPORT_TYPE_ELEMENT_ATTRIBUTE_ID_KEY = "id"
GO_FILE_IMPORT_TYPE_ELEMENT_ATTRIBUTE_ID_VALUE = "2"
GO_FILE_ELEMENT_TAG_PARAMETERS = "parameters"
GO_FILE_ELEMENT_TAG_PARAMETER = "parameter"
GO_FILE_ATTRIBUTE_ELEMENT_NAME_KEY = "name"
GO_FILE_PARAMETER_ELEMENT_NAME_VALUE = "license-code"
GO_FILE_PARAMETER_ELEMENT_VALUE_KEY = "value"
GO_FILE_ELEMENT_TAG_ARCHIVE_FILE = "archive-file"
GO_FILE_ELEMENT_TAG_FILEGROUP = "filegroup"
GO_FILE_ELEMENT_TAG_FILE = "file"
GO_FILE_ELEMENT_TAG_METADATA_FILE = "metadata-file"
