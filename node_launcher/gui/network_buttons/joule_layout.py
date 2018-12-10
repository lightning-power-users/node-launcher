from PySide2 import QtWidgets

from node_launcher.gui.components.copy_button import CopyButton
from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.network_buttons.section_name import SectionName
from node_launcher.gui.utilities import reveal
from node_launcher.node_set import NodeSet


class JouleLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(JouleLayout, self).__init__()
        self.node_set = node_set
        columns = 2

        self.addWidget(SectionName('<a href="https://github.com/wbobeirne/joule-extension/wiki/How-to:-Install-Extension-Manually">Joule Chrome Extension</a>'), column_span=columns)

        self.copy_rest = CopyButton('Node URL (REST)',
                                    self.node_set.lnd.rest_url)
        self.addLayout(self.copy_rest)

        self.show_macaroons_button = QtWidgets.QPushButton('Show Macaroons')
        # noinspection PyUnresolvedReferences
        self.show_macaroons_button.clicked.connect(
            lambda: reveal(self.node_set.lnd.macaroon_path)
        )
        self.addWidget(self.show_macaroons_button, same_row=True,
                       column=columns)
        self.addWidget(HorizontalLine(), column_span=columns)
