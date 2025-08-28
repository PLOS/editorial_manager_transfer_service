"""
Holds all log messages to remove "magic strings" from the codebase and make reviewing confusing messages easier.
"""
__author__ = "Rosetta Reatherford"
__license__ = "AGPL v3"
__maintainer__ = "The Public Library of Science (PLOS)"

from plugins.editorial_manager_transfer_service.consts import PLUGIN_NAME, EXPORT_FILE_PATH, IMPORT_FILE_PATH


def plugin_installation_beginning() -> str:
    """
    Gets the log message for a plugin beginning installation.
    :return: The logger message.
    """
    return '{0} installation beginning...'.format(PLUGIN_NAME)


def plugin_installed() -> str:
    """
    Gets the log message for a plugin being successfully installed.
    :return: The logger message.
    """
    return '{0} installed.'.format(PLUGIN_NAME)


def plugin_already_installed() -> str:
    """
    Gets the log message for a plugin has been previously installed.
    :return: The logger message.
    """
    return '{0} is already installed.'.format(PLUGIN_NAME)


def export_folder_creating() -> str:
    """
    Gets the log message for when an export folder is being created.
    :return: The logger message.
    """
    return '{0} creating export folder (Filepath: \"{1}\")...'.format(PLUGIN_NAME, EXPORT_FILE_PATH)


def export_folder_created() -> str:
    """
    Gets the log message for when an export folder has been created.
    :return: The logger message.
    """
    return '{0} export folder already exists.'.format(PLUGIN_NAME)


def import_folder_creating() -> str:
    """
    Gets the log message for when an import folder is being created.
    :return: The logger message.
    """
    return '{0} creating import folder (Filepath: \"{1}\")...'.format(PLUGIN_NAME, IMPORT_FILE_PATH)


def import_folder_created() -> str:
    """
    Gets the log message for when an import folder has been created.
    :return: The logger message.
    """
    return '{0} import folder already exists.'.format(PLUGIN_NAME)


def process_fetching_article(article_id: str) -> str:
    """
    Gets the log message for when an article is being fetched from the database.
    :param: article_id: The ID of the article being fetched.
    :return: The logger message.
    """
    return "Fetching article from database (ID: {0})...".format(article_id)


def process_failed_fetching_article(article_id: str) -> str:
    """
    Gets the log message for when an article failed to be fetched.
    :param: article_id: The ID of the article being fetched.
    :return: The logger message.
    """
    return "Fetching article from database (ID: {0}) failed. Discontinuing export process.".format(article_id)


def process_failed_fetching_metadata(article_id) -> str:
    """
    Gets the log message for when an article's metadata failed to be fetched.
    :param: article_id: The ID of the article being fetched.
    :return: The logger message.
    """
    return "Fetching article (ID: {0}) metadata failed. Discontinuing export process.".format(article_id)


def process_failed_fetching_article_files(article_id) -> str:
    """
    Gets the log message for when an article's files failed to be fetched.
    :param: article_id: The ID of the article being fetched.
    :return: The logger message.
    """
    return "Fetching files for article (ID: {0}) failed. Discontinuing export process.".format(article_id)


def process_failed_fetching_journal(article_id) -> str:
    """
    Gets the log message for when an article's journal failed to be fetched.
    :param: article_id: The ID of the article.
    :return: The logger message.
     """
    return "Fetching journal where article (ID: {0}) lives failed. Discontinuing export process.".format(article_id)


def process_failed_no_article_id_provided() -> str:
    """
    Gets the log message for when an article ID was not provided.
    :return: The logger message.
    """
    return "No article ID provided. Discontinuing export process."


def export_process_failed_no_export_folder() -> str:
    """
    Gets the log message for when an export folder was not created.
    :return: The logger message.
    """
    return "No export folder provided. Discontinuing export process."
