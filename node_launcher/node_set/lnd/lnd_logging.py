from node_launcher.constants import StringConstant


class Subsystem(object):
    LTND = StringConstant('LTND')
    LNWL = StringConstant('LNWL')
    PEER = StringConstant('PEER')
    DISC = StringConstant('DISC')
    RPCS = StringConstant('RPCS')
    SRVR = StringConstant('SRVR')
    NTFN = StringConstant('NTFN')
    CHDB = StringConstant('CHDB')
    FNDG = StringConstant('FNDG')
    HSWC = StringConstant('HSWC')
    UTXN = StringConstant('UTXN')
    BRAR = StringConstant('BRAR')
    CMGR = StringConstant('CMGR')
    CRTR = StringConstant('CRTR')
    BTCN = StringConstant('BTCN')
    ATPL = StringConstant('ATPL')
    CNCT = StringConstant('CNCT')
    SPHX = StringConstant('SPHX')
    SWPR = StringConstant('SWPR')
    SGNR = StringConstant('SGNR')
    WLKT = StringConstant('WLKT')
    ARPC = StringConstant('ARPC')
    INVC = StringConstant('INVC')
    NANN = StringConstant('NANN')
    WTWR = StringConstant('WTWR')
    NTFR = StringConstant('NTFR')
    IRPC = StringConstant('IRPC')
    CHBU = StringConstant('CHBU')


class LoggingLevel(object):
    TRACE = StringConstant('TRACE')
    DEBUG = StringConstant('DEBUG')
    INFO = StringConstant('INFO')
    WARN = StringConstant('WARN')
    ERROR = StringConstant('ERROR')
    CRITICAL = StringConstant('CRITICAL')
    OFF = StringConstant('OFF')


DEFAULT_LOGGING_LEVELS = [
    (Subsystem.LTND, LoggingLevel.DEBUG),
    (Subsystem.LNWL, LoggingLevel.INFO),
    (Subsystem.PEER, LoggingLevel.WARN),
    (Subsystem.SRVR, LoggingLevel.WARN),
    (Subsystem.DISC, LoggingLevel.WARN),
    (Subsystem.CHBU, LoggingLevel.DEBUG)
]
