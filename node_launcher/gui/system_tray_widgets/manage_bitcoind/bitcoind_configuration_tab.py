from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QWidget, QLabel, QCheckBox, QVBoxLayout


from node_launcher.constants import Network
from node_launcher.gui.system_tray_widgets.settings.data_directories.data_directory_box import DataDirectoryBox
from node_launcher.node_set.bitcoin import Bitcoin


class BitcoindConfigurationTab(QWidget):
    change_network = Signal(Network)

    def __init__(self, bitcoin: Bitcoin):
        super().__init__()

        self.bitcoin = bitcoin

        self.bitcoin_layout = QVBoxLayout()

        self.data_directory_group_box = DataDirectoryBox(bitcoin=self.bitcoin)
        self.data_directory_group_box.file_dialog.new_data_directory.connect(
            self.change_datadir
        )

        self.bitcoin_layout.addWidget(self.data_directory_group_box)
        self.bitcoin_layout.setAlignment(self.data_directory_group_box, Qt.AlignHCenter)

        self.enable_wallet_label = QLabel('Enable wallet')
        self.enable_wallet_widget = QCheckBox('Enable Wallet')
        self.enable_wallet_widget.setChecked(not self.bitcoin.file['disablewallet'])
        self.enable_wallet_widget.stateChanged.connect(
            lambda x: self.update_config('disablewallet', not bool(x))
        )
        self.bitcoin_layout.addWidget(self.enable_wallet_widget)

        self.setLayout(self.bitcoin_layout)

    def change_datadir(self, new_datadir: str):
        self.bitcoin.file['datadir'] = new_datadir
        self.bitcoin.set_prune()
        self.data_directory_group_box.set_datadir(
            self.bitcoin.file['datadir'],
            self.bitcoin.file['prune']
        )

    @staticmethod
    def set_checked(widget: QCheckBox, state: bool):
        if state is None:
            widget.setChecked(False)
            return
        widget.setChecked(state)
