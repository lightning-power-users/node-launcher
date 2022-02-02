from node_launcher.gui.qt import QCoreApplication, QGuiApplication, QMenu, QProgressBar, QWidgetAction, QWidget, \
    QVBoxLayout, QLabel

from node_launcher.gui.reveal_directory import reveal_directory
from node_launcher.node_set import NodeSet
from node_launcher.node_set.lnd.lnd_process import ProgressBarStatus


class Menu(QMenu):
    def __init__(self, node_set: NodeSet, system_tray, parent):
        super().__init__()
        self.node_set = node_set
        self.system_tray = system_tray

        widget = QWidget()
        layout = QVBoxLayout()
        self.bar = QProgressBar()
        self.bar.setMaximum(0)
        self.bar.setMinimum(0)
        layout.addWidget(self.bar)
        self.eta_label = QLabel('Calculating remaining time...')
        layout.addWidget(self.eta_label)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        widget.setLayout(layout)
        berAction = QWidgetAction(self)
        berAction.setDefaultWidget(widget)
        self.addAction(berAction)

        self.addSeparator()
        # Todo: add debug

        self.node_set.lnd_node.process.set_progress_bar.connect(
            self.set_progress_bar
        )

        # Quit
        self.quit_action = self.addAction('Quit')
        self.quit_action.triggered.connect(
            lambda _: QCoreApplication.exit(0)
        )

    def set_progress_bar(self, status: ProgressBarStatus):
        self.bar.setMaximum(100)
        self.bar.setMinimum(0)
        self.bar.setValue(status.percentage)
        self.eta_label.setText(status.humanized_eta)

    def copy_rest_url(self):
        QGuiApplication.clipboard().setText(self.node_set.lnd_node.configuration.rest_url)

    def reveal_macaroon_path(self):
        reveal_directory(self.node_set.lnd_node.configuration.macaroon_path)
