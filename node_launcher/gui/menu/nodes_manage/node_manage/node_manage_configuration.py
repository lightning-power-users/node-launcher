from node_launcher.gui.menu.nodes_manage.manage_dialogs.configuration import ConfigurationDialog
from node_launcher.gui.menu.nodes_manage.manage_dialogs.console import ConsoleDialog
from node_launcher.gui.menu.nodes_manage.manage_dialogs.logs import LogsDialog

node_tabs = {
    'tor': [
        {
            'title': 'Logs',
            'class': LogsDialog
        },
        {
            'title': 'Configuration',
            'class': ConfigurationDialog
        }
    ],
    'bitcoin': [
        {
            'title': 'Logs',
            'class': LogsDialog
        },
        {
            'title': 'Configuration',
            'class': ConfigurationDialog
        },
        {
            'title': 'Console',
            'class': ConsoleDialog
        }
    ],
    'lnd': [
        {
            'title': 'Logs',
            'class': LogsDialog
        },
        {
            'title': 'Configuration',
            'class': ConfigurationDialog
        },
        {
            'title': 'Console',
            'class': ConsoleDialog
        }
    ],
}
