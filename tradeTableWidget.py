import sys
from collections import OrderedDict
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHeaderView, QLabel
from cbMarian.ui.tradeTableWidget import Ui_Form
from cbMarian.productBroker import ProductBroker

class TradeTableWidget(QWidget, Ui_Form):

    def __init__(self, broker, sides=["opened", "closed"], parent=None):
        QWidget.__init__(self, parent)
        self.broker = broker
        self.broker.sigDealsRefresh.connect(self.refreshDeals)
        self.sides = sides
        self.deals = {}
        self.setupUi(self)

        self.refreshDeals(self.broker.brokerDeals)

    def setupUi(self, Form):
        Ui_Form.setupUi(self, self)

        self.tableWidget.horizontalHeader().resizeSection(0, 70)
        self.tableWidget.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)
        self.tableWidget.horizontalHeader().resizeSection(5, 250)
        self.tableWidget.horizontalHeader().resizeSection(6, 70)
        self.tableWidget.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)

    @pyqtSlot(object)
    def refreshDeals(self, deals):
        for side in self.sides:
            if len(deals[side]) == 0: continue
            for deal in deals[side]:
                row = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(row + 1)
                self.tableWidget.setCellWidget(row, 0, QLabel(deal["side"]))
                self.tableWidget.setCellWidget(row, 1, QLabel(deal["product_id"]))
                self.tableWidget.setCellWidget(row, 2, QLabel(deal["size"]))
                self.tableWidget.setCellWidget(row, 3, QLabel(deal["price"]))
                self.tableWidget.setCellWidget(row, 4, QLabel(deal["fee"]))
                self.tableWidget.setCellWidget(row, 5, QLabel(deal["created_at"]))
                # self.tableWidget.setCellWidget(row, 6, QLabel(deal["settled"]))

        self.deals = deals

if __name__ == "__main__":
    app = QApplication(sys.argv)

    broker = ProductBroker("ETH-BTC", *ProductBroker.getCredentials())

    win = QMainWindow()
    widget = TradeTableWidget(broker)
    win.setCentralWidget(widget)

    win.show()
    app.exec_()
