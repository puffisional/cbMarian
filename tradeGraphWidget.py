import pyqtgraph as pg
import sys
from collections import OrderedDict

import dateutil.parser
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHeaderView, QLabel
from pyqtgraph import mkPen

from cbMarian.ui.tradeTableWidget import Ui_Form
from cbMarian.productBroker import ProductBroker

class TradeGraph(pg.PlotWidget):

    sigRefreshData = pyqtSignal()

    def __init__(self, broker, dealTypes=["opened", "closed"]):
        self.broker = broker
        self.dealTypes = dealTypes
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', "k")
        pg.PlotWidget.__init__(self, title=broker.product)

        self._initPlot()

        self.sigRefreshData.connect(self.refreshData)

        self.refreshDeals(self.broker.brokerDeals)
        self.broker.sigDealsRefresh.connect(self.refreshDeals)

    def _initPlot(self):
        penRed = mkPen(color=(255, 0, 0))
        penGreen = mkPen(color=(0, 255, 0))

        self.setLabel("bottom", "Point")
        self.showGrid(x=True, y=True, alpha=0.1)
        curve_item_buy = pg.PlotDataItem([], pen=penGreen, antialias=False, autoDownsample=True, clipToView=True,
                                          symbolPen='w', symbol='h', symbolSize=3)
        curve_item_sell = pg.PlotDataItem([], pen=penRed, antialias=False, autoDownsample=True, clipToView=True,
                                          symbolPen='w', symbol='h', symbolSize=3)
        self.addItem(curve_item_buy)
        self.addItem(curve_item_sell)

        self.dealPlots = {
            "buy": [curve_item_buy, [], []],
            "sell": [curve_item_sell, [], []],
        }

    @pyqtSlot(object)
    def refreshDeals(self, deals):

        for dealTypes in self.dealTypes:
            if len(deals[dealTypes]) == 0: continue

            x1, x2, y, z = [], [], [], []
            for deal in deals[dealTypes]:
                typeLabel = QLabel(deal["side"])
                if deal["side"] == "buy":
                    y.append(float(deal["price"]))
                    x1.append(int(dateutil.parser.parse(deal["created_at"]).timestamp()))
                else:
                    z.append(float(deal["price"]))
                    x2.append(int(dateutil.parser.parse(deal["created_at"]).timestamp()))

        self.dealPlots["buy"][1], self.dealPlots["buy"][2] = x1, y
        self.dealPlots["sell"][1], self.dealPlots["sell"][2] = x2, z

        self.sigRefreshData.emit()

    @pyqtSlot()
    def refreshData(self):
        self.dealPlots["buy"][0].setData(self.dealPlots["buy"][1], self.dealPlots["buy"][2])
        self.dealPlots["sell"][0].setData(self.dealPlots["sell"][1], self.dealPlots["sell"][2])

if __name__ == "__main__":
    app = QApplication(sys.argv)

    broker = ProductBroker("BCH-BTC", *ProductBroker.getCredentials())

    win = QMainWindow()

    widget = TradeGraph(broker)
    win.setCentralWidget(widget)

    win.show()
    app.exec_()