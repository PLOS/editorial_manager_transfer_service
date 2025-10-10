__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

import plugins.editorial_manager_transfer_service.consts as consts
from journal.models import Journal
from utils import setting_handler
from utils.logger import get_logger

logger = get_logger(__name__)


def get_plugin_settings(journal: Journal):
    """
    Get the plugin settings for the Editorial Manager Transfer Service.
    :param journal: the journal
    """

    logger.debug("Fetching journal settings for the following journal: %s", journal.code)
    submission_partner_code = setting_handler.get_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="submission_partner_code",
        journal=journal,
    ).processed_value
    license_code = setting_handler.get_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="license_code",
        journal=journal,
    ).processed_value
    journal_code = setting_handler.get_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="journal_code",
        journal=journal,
    ).processed_value

    return (
        submission_partner_code,
        license_code,
        journal_code,
    )


def save_plugin_settings(
        submission_partner_code,
        license_code,
        journal_code,
        request,
):
    setting_handler.save_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="submission_partner_code",
        journal=request.journal,
        value=submission_partner_code,
    )
    setting_handler.save_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="license_code",
        journal=request.journal,
        value=license_code,
    )
    setting_handler.save_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="journal_code",
        journal=request.journal,
        value=journal_code,
    )
