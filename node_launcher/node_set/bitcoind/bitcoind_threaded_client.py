from PySide2.QtCore import QObject, QThreadPool

from node_launcher.gui.components.thread_worker import Worker
from node_launcher.logging import log
from node_launcher.node_set.bitcoind.bitcoind_rpc_client import Proxy


class BitcoindThreadedClient(QObject):
    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration
        self.client = Proxy(btc_conf_file=configuration.file.path,
                            service_port=configuration.rpc_port)
        self.threadpool = QThreadPool()

    def stop(self):
        self.run_command('stop')

    def run_command(self, command: str, **kwargs):
        log.debug('BitcoindThreadedClient call',
                  command=command,
                  kwargs=kwargs)
        worker = Worker(
            fn=self.client_work,
            command=command,
            configuration=self.configuration,
            **kwargs
        )
        worker.signals.finished.connect(self.handle_finished)
        worker.signals.error.connect(self.handle_error)
        worker.signals.result.connect(self.handle_result)
        worker.signals.progress.connect(self.handle_progress)
        self.threadpool.start(worker)

    @staticmethod
    def client_work(command, configuration, **kwargs):
        client = Proxy(btc_conf_file=configuration.file.path,
                       service_port=configuration.rpc_port)
        return getattr(client, command)(**kwargs)

    def handle_finished(self):
        log.debug('BitcoindThreadedClient call finished')

    def handle_error(self, error_tuple):
        exctype, value, traceback = error_tuple
        log.debug(
            'BitcoindThreadedClient call error',
            exctype=exctype,
            value=value,
            traceback=traceback
        )

    def handle_result(self, result):
        log.debug(
            'BitcoindThreadedClient call result',
            result=result
        )

    def handle_progress(self, percentage: int):
        log.debug(
            'BitcoindThreadedClient call progress',
            percentage=percentage
        )
