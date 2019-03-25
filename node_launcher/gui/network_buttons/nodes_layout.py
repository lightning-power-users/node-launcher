from PySide2.QtWidgets import QPushButton

from node_launcher.gui.network_buttons.advanced.advanced_widget import AdvancedWidget
from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.horizontal_line import HorizontalLine
from node_launcher.gui.components.image_label import ImageLabel
from node_launcher.gui.components.section_name import SectionName
from node_launcher.gui.network_buttons.lnd_output_widget import LndOutputWidget
from node_launcher.node_set import NodeSet


class NodesLayout(QGridLayout):
    def __init__(self, node_set: NodeSet):
        super(NodesLayout, self).__init__()
        self.node_set = node_set
        self.advanced_widget = AdvancedWidget(node_set)
        self.lnd_output_widget = LndOutputWidget(self.node_set,
                                                 self.node_set.lnd.process)

        self.columns = 2
        self.image_label = ImageLabel()
        self.image_label.set_image(f'bitcoin-{self.node_set.bitcoin.network}.png')
        self.addWidget(self.image_label, row_span=5)

        self.addWidget(SectionName('Nodes'), column=self.columns)
        # Bitcoin-Qt button
        self.bitcoin_qt_button = QPushButton('Launch Bitcoin')
        # noinspection PyUnresolvedReferences
        self.bitcoin_qt_button.clicked.connect(self.node_set.bitcoin.launch)
        self.addWidget(self.bitcoin_qt_button, column=self.columns)

        # LND button
        self.lnd_button = QPushButton('See LND Output')
        # noinspection PyUnresolvedReferences
        self.lnd_button.clicked.connect(self.lnd_output_widget.show)
        self.node_set.lnd.process.readyReadStandardError.connect(
            self.lnd_output_widget.handle_error
        )
        self.node_set.lnd.process.readyReadStandardOutput.connect(
            self.lnd_output_widget.handle_output
        )
        self.addWidget(self.lnd_button, column=self.columns)

        # Advanced button
        self.advanced_button = QPushButton('Advanced...')
        # noinspection PyUnresolvedReferences
        self.advanced_button.clicked.connect(self.advanced_widget.show)
        self.addWidget(self.advanced_button, column=self.columns)

        self.addWidget(HorizontalLine(), column=self.columns)

    def set_button_state(self):
        # Can not launch Bitcoin
        self.bitcoin_qt_button.setDisabled(
            self.node_set.bitcoin.running
        )

        # Need to have Bitcoin running to launch LND
        disable_lnd_launch = (self.node_set.lnd.running
                              or not self.node_set.bitcoin.running)
        self.lnd_button.setDisabled(disable_lnd_launch)
