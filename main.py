import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from cbMarian.futuresBroker import FuturesBroker
from cbMarian.mainWidget import MainWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    broker = FuturesBroker(*FuturesBroker.getCredentials())
    broker.startPolling()

    win = QMainWindow()
    widget = MainWidget(broker)
    win.setCentralWidget(widget)

    win.show()
    app.exec_()

