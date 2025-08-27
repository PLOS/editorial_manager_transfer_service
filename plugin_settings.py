"""
A plugin to provide information for Aries' Editorial Manager to enable automatic transfers.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os
from utils.logger import get_logger
from django.conf import settings
from utils import plugins
import logger_messages

PLUGIN_NAME = 'Editorial Manager Transfer Service Plugin'
DISPLAY_NAME = 'Editorial Manager Transfer Service'
DESCRIPTION = 'A plugin to provide information for Aries\' Editorial Manager to enable automatic transfers.'
AUTHOR = 'PLOS'
VERSION = '0.1'
SHORT_NAME = 'editorial_manager_transfer_service'
MANAGER_URL = 'editorial_manager_transfer_service_manager'
JANEWAY_VERSION = "1.8.0"

EXPORT_FILE_PATH = os.path.join(settings.BASE_DIR, 'files', 'plugins', 'editorial-manager-transfer-service', 'export')
IMPORT_FILE_PATH = os.path.join(settings.BASE_DIR, 'files', 'plugins', 'editorial-manager-transfer-service', 'import')

logger = get_logger(__name__)

class EditorialManagerTransferServicePlugin(plugins.Plugin):
    """
    The plugin class for the Editorial Manager Transfer Service.
    """
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME
    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION

def install():
    """
    Installs the Editorial Manager Transfer Service.
    """
    logger.info(logger_messages.plugin_installation_beginning())
    plugin, created = EditorialManagerTransferServicePlugin.install()

    if created:
        # Create the export folder.
        try:
            logger.info(logger_messages.export_folder_creating())
            os.makedirs(EXPORT_FILE_PATH)
        except FileExistsError:
            logger.info(logger_messages.export_folder_created())
            pass

        # Create the import folder.
        try:
            logger.info(logger_messages.import_folder_creating())
            os.makedirs(IMPORT_FILE_PATH)
        except FileExistsError:
            logger.info(logger_messages.import_folder_created())
            pass

        # Log the plugin was installed.
        logger.info(logger_messages.plugin_installed())
    else:
        logger.info(logger_messages.plugin_already_installed())


def hook_registry():
    EditorialManagerTransferServicePlugin.hook_registry()


def register_for_events():
    pass
