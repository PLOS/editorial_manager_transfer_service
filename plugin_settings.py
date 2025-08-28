"""
A plugin to provide information for Aries' Editorial Manager to enable automatic transfers.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import os

import plugins.editorial_manager_transfer_service.consts as consts
import plugins.editorial_manager_transfer_service.logger_messages as logger_messages
from utils import plugins
from utils.logger import get_logger

logger = get_logger(__name__)


class EditorialManagerTransferServicePlugin(plugins.Plugin):
    """
    The plugin class for the Editorial Manager Transfer Service.
    """
    plugin_name = consts.PLUGIN_NAME
    display_name = consts.DISPLAY_NAME
    description = consts.DESCRIPTION
    author = consts.AUTHOR
    short_name = consts.SHORT_NAME
    manager_url = consts.MANAGER_URL

    version = consts.VERSION
    janeway_version = consts.JANEWAY_VERSION


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
            os.makedirs(consts.EXPORT_FILE_PATH)
        except FileExistsError:
            logger.info(logger_messages.export_folder_created())
            pass

        # Create the import folder.
        try:
            logger.info(logger_messages.import_folder_creating())
            os.makedirs(consts.IMPORT_FILE_PATH)
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
