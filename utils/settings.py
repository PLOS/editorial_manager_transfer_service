__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from journal.models import Journal
from plugins.editorial_manager_transfer_service import consts
from plugins.production_transporter.utilities import data_fetch
from utils import setting_handler

from utils.logger import get_logger

logger = get_logger(__name__)

def get_submission_partner_code(journal: Journal, fetch_fresh: bool = False) -> str:

    return data_fetch.fetch_setting(journal, consts.PLUGIN_SETTINGS_GROUP_NAME, "submission_partner_code", fetch_fresh=fetch_fresh)

def get_license_code(journal: Journal, fetch_fresh: bool = False) -> str:
    return data_fetch.fetch_setting(journal, consts.PLUGIN_SETTINGS_GROUP_NAME, "license_code", fetch_fresh=fetch_fresh)

def get_journal_code(journal: Journal, fetch_fresh: bool = False) -> str:
    return data_fetch.fetch_setting(journal, consts.PLUGIN_SETTINGS_GROUP_NAME, "journal_code", fetch_fresh=fetch_fresh)

def get_plugin_settings(journal: Journal, fetch_fresh: bool = False):
    """
    Get the plugin settings for the Editorial Manager Transfer Service.
    :param journal: the journal
    :param fetch_fresh: Fetch fresh settings.
    """

    logger.debug("Fetching journal settings for the following journal: %s", journal.code)
    submission_partner_code = get_submission_partner_code(journal, fetch_fresh=fetch_fresh)
    license_code = get_license_code(journal, fetch_fresh=fetch_fresh)
    journal_code = get_journal_code(journal, fetch_fresh=fetch_fresh)

    return (
        submission_partner_code,
        license_code,
        journal_code,
    )

def save_plugin_settings(
        journal: Journal,
        submission_partner_code: str,
        license_code: str,
        em_journal_code: str,
):
    """
    Save the plugin settings for the Editorial Manager Transfer Service.
    :param submission_partner_code: The submission partner code
    :param license_code: The license code
    :param em_journal_code: The journal code
    :param journal: The journal where to save the plugin settings
    :return:
    """
    setting_handler.save_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="submission_partner_code",
        journal=journal,
        value=submission_partner_code,
    )
    setting_handler.save_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="license_code",
        journal=journal,
        value=license_code,
    )
    setting_handler.save_setting(
        setting_group_name=consts.PLUGIN_SETTINGS_GROUP_NAME,
        setting_name="journal_code",
        journal=journal,
        value=em_journal_code,
    )