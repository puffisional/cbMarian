import time
from collections import deque

import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout
from pyqtgraph import mkPen

from cbMarian.tradeGraphWidget import TradeGraph
from cbMarian.tradeTableWidget import TradeTableWidget
from cbMarian.ui.mainWidget import Ui_Form
from cbMarian.walletWidget import WalletWidget


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

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    def onRateDiff(self, broker, tradeRates):
        currentRate, lastBrokerRate, rateDiff, rateDiffPercent = tradeRates["sell"]
        self.plots[broker][0][1].append(time.time())
        self.plots[broker][0][2].append(rateDiffPercent)
        self.plots[broker][0][0].setData(self.plots[broker][0][1], self.plots[broker][0][2])

        currentRate, lastBrokerRate, rateDiff, rateDiffPercent = tradeRates["buy"]
        self.plots[broker][1][1].append(time.time())
        self.plots[broker][1][2].append(rateDiffPercent)
        self.plots[broker][1][0].setData(self.plots[broker][1][1], self.plots[broker][1][2])

    def setupGraphs(self):
        self.plots = {}

        for broker in self.brokers:
            penRed = mkPen(color=(255, 0, 0))
            penGreen = mkPen(color=(0, 255, 0))

            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', "k")

            dialog = pg.PlotWidget(title=broker.product)
            # dialog = pg.PlotWidget(title="a")

            # dialog.setLabel("bottom", "Point")
            dialog.showGrid(x=True, y=True, alpha=0.1)
            curve_sell = pg.PlotDataItem([], pen=penRed, antialias=False, autoDownsample=True, clipToView=True,
                                              symbols=None)
            curve_buy = pg.PlotDataItem([], pen=penGreen, antialias=False, autoDownsample=True, clipToView=True,
                                         symbols=None)
            dialog.addItem(curve_sell)
            dialog.addItem(curve_buy)

            self.graphListWidget.layout().addWidget(dialog)
            self.plots[broker] = (
                (curve_sell, deque(maxlen=3600 * 10), deque(maxlen=3600 * 10)),
                (curve_buy, deque(maxlen=3600 * 10), deque(maxlen=3600 * 10))
            )

            broker.sigRateDiff.connect(self.onRateDiff)
