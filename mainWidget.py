import time
from collections import deque

import pyqtgraph as pg
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget
from pyqtgraph import mkPen

from cbMarian.ui.mainWidget import Ui_Form


class MainWidget(QWidget, Ui_Form):

    sigReplot = pyqtSignal()

    def __init__(self, broker, parent=None):
        QWidget.__init__(self, parent=parent)
        self.broker = broker
        self.setupUi(self)
        self.setupGraphs()

        self.broker.sigRateDiff.connect(self.onRateDiff)

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    def onRateDiff(self, product_id, rates):
        self.plots[product_id][2].append(time.time())
        self.plots[product_id][3].append(rates[0])
        self.plots[product_id][4].append(rates[1])

        # self.plots[product_id][0].setData(self.plots[product_id][2], self.plots[product_id][3])
        self.plots[product_id][1].setData(self.plots[product_id][2], self.plots[product_id][4])

    def setupGraphs(self):
        self.plots = {}

        for product_id, product in self.broker.products.items():
            pen1 = mkPen(color=(0, 72, 255))
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', "k")

            # dialog = pg.PlotWidget(title=product_id)
            dialog = pg.PlotWidget(title="a")

            dialog.setLabel("bottom", "Point")
            dialog.showGrid(x=True, y=True, alpha=0.1)
            curve_item_low = pg.PlotDataItem([], pen=pen1, antialias=False, autoDownsample=True, clipToView=True,
                                             symbols=None)
            curve_item_high = pg.PlotDataItem([], pen=pen1, antialias=False, autoDownsample=True, clipToView=True,
                                              symbols=None)
            dialog.addItem(curve_item_low)
            dialog.addItem(curve_item_high)

            self.graphListWidget.layout().addWidget(dialog)
            self.plots[product_id] = (
            curve_item_low, curve_item_high, deque(maxlen=3600 * 10), deque(maxlen=3600 * 10), deque(maxlen=3600 * 10))