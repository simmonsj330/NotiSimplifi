#!/usr/bin/env python3

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtCore import QEventLoop, QTimer, Qt

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(260, 20, 113, 32))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(410, 20, 113, 32))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 51, 51))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("resources/logo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(70, 30, 71, 16))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(0, 60, 1361, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(170, 70, 1191, 711))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab)
        self.plainTextEdit.setGeometry(QtCore.QRect(0, 0, 1191, 681))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setAutoFillBackground(False)
        self.plainTextEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.plainTextEdit.setReadOnly(False)
        self.plainTextEdit.setOverwriteMode(False)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.plainTextEdit_2 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.plainTextEdit_2.setGeometry(QtCore.QRect(0, 0, 1191, 681))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.plainTextEdit_2.setFont(font)
        self.plainTextEdit_2.setAutoFillBackground(False)
        self.plainTextEdit_2.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.plainTextEdit_2.setReadOnly(False)
        self.plainTextEdit_2.setOverwriteMode(False)
        self.plainTextEdit_2.setObjectName("plainTextEdit_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tabWidget.raise_()
        self.pushButton.raise_()
        self.pushButton_2.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.line.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Add"))
        self.pushButton_2.setText(_translate("MainWindow", "Home"))
        self.label_2.setText(_translate("MainWindow", "NotiSimplifi"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))

#executes program
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    
    # Splash screen & logo
    logo_path = os.path.dirname(os.path.realpath(__file__))
    pixmap = QPixmap('/'.join([logo_path, 'resources/logo.png']))
    splashScreen = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splashScreen.show()

    # this checks for button clicks while main form is loading
    # keeping for future use
    app.processEvents()

		# delay main form from showing until 2 seconds has passed
    loop = QEventLoop()
    QTimer.singleShot(2000, loop.quit)
    loop.exec_()
    
    w = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(w)
    
    w.show()
    
		# stop showing splashscreen once main form has loaded in
    splashScreen.finish(w)
    sys.exit(app.exec_())# -*- coding: utf-8 -*-
