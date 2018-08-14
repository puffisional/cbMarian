import sys
from collections import OrderedDict

import dateutil.parser
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHeaderView, QLabel
from cbMarian.ui.tradeTableWidget import Ui_Form
from cbMarian.productBroker import ProductBroker

class TradeTableWidget(QWidget, Ui_Form):

    def __init__(self, broker, dealTypes=["opened", "closed"], parent=None):
        QWidget.__init__(self, parent)
        self.broker = broker
        self.broker.sigDealsRefresh.connect(self.refreshDeals)
        self.dealTypes = dealTypes
        self.deals = {}
        self.setupUi(self)

        self.refreshDeals(self.broker.brokerDeals)

    def setupUi(self, Form):
        Ui_Form.setupUi(self, self)

        self.tableWidget.horizontalHeader().resizeSection(0, 40)
        self.tableWidget.horizontalHeader().resizeSection(1, 70)
        self.tableWidget.horizontalHeader().resizeSection(2, 80)
        self.tableWidget.horizontalHeader().resizeSection(3, 80)
        self.tableWidget.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)
        self.tableWidget.horizontalHeader().resizeSection(4, 130)
        self.tableWidget.horizontalHeader().resizeSection(5, 120)
        self.tableWidget.horizontalHeader().resizeSection(6, 70)
        self.tableWidget.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.tableWidget.setStyleSheet("QLabel {margin-left:5px}")

    @pyqtSlot(object)
    def refreshDeals(self, deals):
        self.tableWidget.setRowCount(0)

        for dealTypes in self.dealTypes:
            if len(deals[dealTypes]) == 0: continue

            for deal in deals[dealTypes]:
                typeLabel = QLabel(deal["side"])
                if deal["side"] == "buy":
                    typeLabel.setStyleSheet("color:green;font-weight:bold")
                else:
                    typeLabel.setStyleSheet("color:red;font-weight:bold")
                dealDate = "{:%d.%m.%Y    %H:%M}".format(dateutil.parser.parse(deal["created_at"]))


                row = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(row + 1)
                self.tableWidget.setCellWidget(row, 0, typeLabel)
                self.tableWidget.setCellWidget(row, 1, QLabel(deal["product_id"]))
                self.tableWidget.setCellWidget(row, 2, QLabel(deal["size"]))
                self.tableWidget.setCellWidget(row, 3, QLabel(deal["price"]))
                self.tableWidget.setCellWidget(row, 4, QLabel(deal["fee"]))
                self.tableWidget.setCellWidget(row, 5, QLabel(dealDate))
                self.tableWidget.setCellWidget(row, 6, QLabel(dealTypes))

        self.deals = deals

if __name__ == "__main__":
    app = QApplication(sys.argv)

    broker = ProductBroker("LTC-BTC", *ProductBroker.getCredentials())

    win = QMainWindow()

    widget = TradeTableWidget(broker)
    win.setCentralWidget(widget)

    win.show()
    app.exec_()
