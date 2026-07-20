import os

from plugins.editorial_manager_transfer_service import logger_messages, consts
from utils.logger import get_logger

logger = get_logger(__name__)

def create_export_folder() -> bool:
    # Create the export folder.
    try:
        logger.info(logger_messages.export_folder_creating())
        os.makedirs(consts.EXPORT_FILE_PATH)
    except FileExistsError:
        logger.info(logger_messages.export_folder_created())
        return False
    except Exception as e:
        logger.error("Unable to create export folder due to an unknown exception.", e)
        return False

    return True

def create_import_folder() -> bool:
    # Create the import folder.
    try:
        logger.info(logger_messages.import_folder_creating())
        os.makedirs(consts.IMPORT_FILE_PATH)
    except FileExistsError:
        logger.info(logger_messages.import_folder_created())
        return False
    except Exception as e:
        logger.error("Unable to create import folder due to an unknown exception.", e)
        return False

    return True
