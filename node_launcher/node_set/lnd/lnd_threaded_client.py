from PySide2.QtCore import QObject, QThreadPool

from node_launcher.gui.components.thread_worker import Worker, WorkerSignals
from node_launcher.logging import log
from node_launcher.node_set.lnd.lnd_logging import DEFAULT_LOGGING_LEVELS
from .lnd_client import LndClient


class LndThreadedClient(QObject):
    def __init__(self, configuration=None, lnd_client=None):
        super().__init__()
        self.configuration = configuration
        if lnd_client is not None:
            self.client = lnd_client
        else:
            self.client = LndClient(lnd_configuration=configuration)
        self.threadpool = QThreadPool()
        self.signals = WorkerSignals()

    def stop(self):
        self.run_command('stop')

    def debug_level(self):
        level_spec = ','.join(['='.join([str(i[0]).upper(), str(i[1])]) for i in DEFAULT_LOGGING_LEVELS])
        self.run_command('debug_level', level_spec=level_spec)

    def list_all(self):
        self.run_command('list_all')

    def run_command(self, command: str, **kwargs):
        log.debug('LndThreadedClient call',
                  command=command,
                  kwargs=kwargs)
        worker = Worker(
            fn=self.client_work,
            command=command,
            client=LndClient(lnddir=self.client.lnddir,
                             grpc_host=self.client.grpc_host,
                             grpc_port=self.client.grpc_port),
            **kwargs
        )
        worker.signals.finished.connect(self.handle_finished)
        worker.signals.error.connect(self.handle_error)
        worker.signals.result.connect(self.handle_result)
        worker.signals.progress.connect(self.handle_progress)
        self.threadpool.start(worker)

    @staticmethod
    def client_work(command, client, **kwargs):
        return getattr(client, command)(**kwargs)

    def handle_finished(self):
        log.debug('LndThreadedClient call finished')
        self.signals.finished.emit()

    def handle_error(self, error_tuple):
        self.signals.error.emit(error_tuple)
        exctype, value, traceback = error_tuple
        log.debug(
            'LndThreadedClient call error',
            exctype=exctype,
            value=value,
            traceback=traceback
        )

    def handle_result(self, result):
        log.debug(
            'LndThreadedClient call result emit',
        )
        self.signals.result.emit(result)

    def handle_progress(self, percentage: int):
        log.debug(
            'LndThreadedClient call progress',
            percentage=percentage
        )
