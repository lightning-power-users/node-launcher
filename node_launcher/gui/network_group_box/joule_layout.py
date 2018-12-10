from PySide2 import QtWidgets

from node_launcher.gui.components.layouts import QGridLayout
from node_launcher.gui.horizontal_line import HorizontalLine
from node_launcher.gui.network_group_box.section_name import SectionName
from node_launcher.gui.utilities import copy_to_clipboard, reveal
from node_launcher.node_set import NodeSet


class JouleLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(JouleLayout, self).__init__()
        self.node_set = node_set
        columns = 2

        self.addWidget(SectionName('Joule'), column_span=columns)

        # Copy REST API URL button
        self.rest_url_copy_button = QtWidgets.QPushButton('Node URL (REST)')
        # noinspection PyUnresolvedReferences
        self.rest_url_copy_button.clicked.connect(
            lambda: copy_to_clipboard(self.node_set.lnd.rest_url)
        )
        self.addWidget(self.rest_url_copy_button)

        # Show Macaroons button
        self.show_macaroons_button = QtWidgets.QPushButton('Show Macaroons')
        # noinspection PyUnresolvedReferences
        self.show_macaroons_button.clicked.connect(
            lambda: reveal(self.node_set.lnd.macaroon_path)
        )
        self.addWidget(self.show_macaroons_button, same_row=True, column=columns)
        self.addWidget(HorizontalLine(), column_span=columns)
