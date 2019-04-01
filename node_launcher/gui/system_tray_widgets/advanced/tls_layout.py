from pprint import pformat

from PySide2.QtWidgets import QPushButton, QMessageBox

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.gui.components.section_name import SectionName
from node_launcher.node_set import NodeSet


class TlsLayout(QGridLayout):
    node_set: NodeSet

    def __init__(self, node_set: NodeSet):
        super(TlsLayout, self).__init__()
        self.node_set = node_set

        columns = 2
        self.section_name = SectionName('LND TLS Debugging')
        self.addWidget(self.section_name, column_span=columns)

        self.test_tls = QPushButton('Test TLS')
        # noinspection PyUnresolvedReferences
        self.test_tls.clicked.connect(self.test_tls_cert)
        self.addWidget(self.test_tls)

        self.reset_tls = QPushButton('Reset TLS')
        # noinspection PyUnresolvedReferences
        self.reset_tls.clicked.connect(self.node_set.reset_tls)
        self.addWidget(self.reset_tls, same_row=True, column=2)

    def test_tls_cert(self):
        cert = self.node_set.lnd.test_tls_cert()
        message = QMessageBox(self.parentWidget())
        message.setText(pformat(cert))
        message.show()
