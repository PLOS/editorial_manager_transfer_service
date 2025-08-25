from utils import plugins

PLUGIN_NAME = 'Editorial Manager Transfer Service Plugin'
DISPLAY_NAME = 'Editorial Manager Transfer Service'
DESCRIPTION = 'A plugin to provide information for Aries' Editorial Manager to enable automatic transfers.'
AUTHOR = 'PLOS'
VERSION = '0.1'
SHORT_NAME = 'editorial_manager_transfer_service'
MANAGER_URL = 'editorial_manager_transfer_service_manager'
JANEWAY_VERSION = "1.3.8"



class EditorialManagerTransferServicePlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME
    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION
    


def install():
    EditorialManagerTransferServicePlugin.install()


def hook_registry():
    EditorialManagerTransferServicePlugin.hook_registry()


def register_for_events():
    pass
