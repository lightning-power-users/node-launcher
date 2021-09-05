from node_launcher.constants import StringConstant


class Status(StringConstant):
    pass


class NodeStatus(object):
    CHECKING_DOWNLOAD = StringConstant('CHECKING_DOWNLOAD')
    DOWNLOADING_SOFTWARE = StringConstant('DOWNLOADING_SOFTWARE')
    SOFTWARE_DOWNLOADED = StringConstant('SOFTWARE_DOWNLOADED')
    INSTALLING_SOFTWARE = StringConstant('INSTALLING_SOFTWARE')
    SOFTWARE_INSTALLED = StringConstant('SOFTWARE_INSTALLED')
    SOFTWARE_READY = StringConstant('SOFTWARE_READY')

    LOADING_CONFIGURATION = StringConstant('LOADING_CONFIGURATION')
    CHECKING_CONFIGURATION = StringConstant('CHECKING_CONFIGURATION')
    CONFIGURATION_READY = StringConstant('CONFIGURATION_READY')

    STARTING_PROCESS = StringConstant('STARTING_PROCESS')
    PROCESS_STARTED = StringConstant('PROCESS_STARTED')

    UNLOCK_READY = StringConstant('UNLOCK_READY')
    SYNCING = StringConstant('SYNCING')
    SYNCED = StringConstant('SYNCED')

    STOPPED = StringConstant('STOPPED')
    RUNTIME_ERROR = StringConstant('RUNTIME_ERROR')
    RESTART = StringConstant('RESTART')


SoftwareStatus = NodeStatus
