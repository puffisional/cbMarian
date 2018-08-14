import time
from collections import deque

import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout
from pyqtgraph import mkPen

from cbMarian.ui.mainWidget import Ui_Form
from tradeGraphWidget import TradeGraph
from tradeTableWidget import TradeTableWidget
from walletWidget import WalletWidget


class MainWidget(QWidget, Ui_Form):
    sigReplot = pyqtSignal()

    def __init__(self, brokers, parent=None):
        QWidget.__init__(self, parent=parent)
        self.brokers = brokers
        self.setupUi(self)
        self.setupGraphs()

        # self.broker.sigRateDiff.connect(self.onRateDiff)

    def setupUi(self, Form):
        Ui_Form.setupUi(self, self)

        for broker in self.brokers:
            container = QWidget()
            wLayout = QGridLayout()
            container.setLayout(wLayout)
            wLayout.addWidget(TradeGraph(broker, dealTypes=["closed"]))
            wLayout.addWidget(TradeTableWidget(broker, dealTypes=["opened", "closed"]))
            wLayout.addWidget(WalletWidget(broker, broker.baseCurrency))
            wLayout.addWidget(WalletWidget(broker, broker.quotedCurrency))
            self.brokerTabs.addTab(container, broker.product)


    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject")
    def onRateDiff(self, broker, rateDiff, rateDiffPercent, currentRate, lastBrokerRate):
        self.plots[broker][1].append(time.time())
        self.plots[broker][2].append(rateDiffPercent)
        self.plots[broker][0].setData(self.plots[broker][1], self.plots[broker][2])

    def setupGraphs(self):
        self.plots = {}

        for broker in self.brokers:
            pen1 = mkPen(color=(0, 72, 255))
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', "k")

            dialog = pg.PlotWidget(title=broker.product)
            # dialog = pg.PlotWidget(title="a")

            dialog.setLabel("bottom", "Point")
            dialog.showGrid(x=True, y=True, alpha=0.1)
            curve_item_high = pg.PlotDataItem([], pen=pen1, antialias=False, autoDownsample=True, clipToView=True,
                                              symbols=None)
            dialog.addItem(curve_item_high)

            self.graphListWidget.layout().addWidget(dialog)
            self.plots[broker] = (
                curve_item_high, deque(maxlen=3600 * 10), deque(maxlen=3600 * 10))

            broker.sigRateDiff.connect(self.onRateDiff)
