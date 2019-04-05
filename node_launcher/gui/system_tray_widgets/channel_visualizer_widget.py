# noinspection PyPackageRequirements
from datetime import datetime

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QDialog

from node_launcher.gui.components.grid_layout import QGridLayout
from node_launcher.node_set import NodeSet
from node_launcher.node_set.lnd_client import LndClient


class ChannelVisualizerWidget(QDialog):
    def __init__(self, node_set: NodeSet, system_tray):
        super().__init__()
        self.setWindowTitle('Channel Visualizer')
        self.node_set = node_set
        self.system_tray = system_tray
        self.client = LndClient(self.node_set.lnd)

        self.layout = QGridLayout()
        self.chart = QtCharts.QChart()
        self.chart_view = QtCharts.QChartView(self.chart)
        self.layout.addWidget(self.chart_view)
        self.setLayout(self.layout)

    def show(self):
        channels = self.client.list_channels()
        forwarding_history = self.client.forwarding_history(
            start_time=1,
            end_time=int(datetime.now().timestamp()),
            num_max_events=10000
        )
        forwarding_events = forwarding_history.forwarding_events
        payments = self.client.list_payments().payments
        invoices = self.client.list_invoices().invoices

        for channel in channels:
            current_local_balance = channel.local_balance
            current_time = int(datetime.utcnow().timestamp())

        for forwarding_event in forwarding_events:
            print(forwarding_event.timestamp)

        line_series = QtCharts.QLineSeries()
        for payment in payments:
            line_series.append(payment.creation_date, payment.value)

        self.chart.addSeries(line_series)
        self.chart.createDefaultAxes()
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        for invoice in invoices:
            if invoice.settle_date:
                print(invoice.settle_date)

        self.showMaximized()
        self.raise_()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
