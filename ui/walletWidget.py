# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'walletWidget.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(488, 71)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.currencyLabel = QtWidgets.QLabel(Form)
        self.currencyLabel.setMaximumSize(QtCore.QSize(70, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.currencyLabel.setFont(font)
        self.currencyLabel.setStyleSheet("padding:10px;background:#6caac8")
        self.currencyLabel.setObjectName("currencyLabel")
        self.horizontalLayout.addWidget(self.currencyLabel)
        self.holdLabel = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.holdLabel.setFont(font)
        self.holdLabel.setStyleSheet("padding:10px;background:#c87b6c")
        self.holdLabel.setObjectName("holdLabel")
        self.horizontalLayout.addWidget(self.holdLabel)
        self.balanceLabel = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.balanceLabel.setFont(font)
        self.balanceLabel.setStyleSheet("padding:10px;background:#c8c36c")
        self.balanceLabel.setObjectName("balanceLabel")
        self.horizontalLayout.addWidget(self.balanceLabel)
        self.availableLabel = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.availableLabel.setFont(font)
        self.availableLabel.setStyleSheet("padding:10px;background:#88c86c")
        self.availableLabel.setObjectName("availableLabel")
        self.horizontalLayout.addWidget(self.availableLabel)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.currencyLabel.setText(_translate("Form", "C"))
        self.holdLabel.setText(_translate("Form", "H"))
        self.balanceLabel.setText(_translate("Form", "B"))
        self.availableLabel.setText(_translate("Form", "A"))

