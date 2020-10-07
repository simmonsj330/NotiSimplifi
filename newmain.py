#!/usr/bin/env python3

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QSplashScreen, QTabBar, QInputDialog
from PyQt5.QtCore import QEventLoop, QTimer, Qt, QSize, pyqtSlot
from mainwindow import Ui_MainWindow

class TabBar(QTabBar):
    def __init__(self, parent):
        super(TabBar, self).__init__()
        self.parent = parent;
        # timer = QTimer(self)
        # timer.timeout.connect(self.displayCloseButton)
        # timer.start(100)
        # self.setTabsClosable(False)
        self.setStyleSheet("""
            QTabBar::close-button { 
                image: url(delete_tab.png); 
                subcontrol-position: left; 
                }
            """)
        # self.setMouseTracking(True)

    # def enterEvent(self, event):
    #     self.setTabsClosable(True)
    #     mpos = event.pos()
    #     idx = self.tabAt(mpos)
    #     if idx != -1:
    #         self.setTabsClosable(True)
    #         self.tabButton(idx, QTabBar.LeftSide).resize(20, 20)
    #     
    #     event.ignore()
    #     return

    # def leaveEvent(self, event):
    #     self.setTabsClosable(True)
    #     mpos = event.pos()
    #     idx = self.tabAt(mpos)
    #     if idx != -1:
    #         self.setTabsClosable(True)
    #         self.tabButton(idx, QTabBar.LeftSide).resize(0, 0)


    #     event.ignore()
    #     return

    # def mouseMoveEvent(self, event):
    #     mpos = event.pos()
    #     idx = self.tabAt(mpos)
    #     if idx != -1:
    #         # self.setTabButton(idx, QtGui.QtabBar.RightSide, None)
    #         self.setTabsClosable(True)
    #         self.tabButton(idx, QTabBar.LeftSide).resize(20, 20)

    #     else:
    #         self.setTabsClosable(False)
    #         self.tabButton(self.currentIndex(), QTabBar.LeftSide).resize(0, 0)

    #     event.ignore()
    #     return

    # def displayCloseButton(self):
    #     if self.underMouse():
    #         print("At index:", self.currentIndex(), ", the width is", self.width())
    #         self.setTabButton(idx, QtGui.QtabBar.RightSide, None)

    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
 
        # Need this on startup to avoid division by 0 error
        if self.parent.count() == 0:
            return QSize(size.width(), size.height())
 
        # this takes the parent widgets width and divides it by
        # the number of tabs to prevent the tabbar expanding past
        # its tab widget parent
        max_width = int(self.parent.parent.width())
        width = int(max_width/self.parent.count())

        return QSize(width, size.height())

    # based on https://stackoverflow.com/questions/44450775/pyqt-gui-with-multiple-tabs
    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.LeftButton:
            super(TabBar, self).mouseDoubleClickEvent(event)

        index = self.currentIndex()
        ok = True
        self.input_dialog = QInputDialog()

        newName, ok = QInputDialog.getText(self, '','New file name:')

        if ok:
            self.setTabText(index, newName)

class NotesTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super(NotesTabWidget, self).__init__(parent)
        self.parent = parent;
        self.initUI();

    def initUI(self):
        self.tab = TabBar(self)
        self.setTabBar(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setObjectName("tabWidget")
        addTabButton = QtWidgets.QToolButton()
        addTabButton.setToolTip('Add New Tab')
        addTabButton.clicked.connect(lambda: self.add_new_tab())
        addTabButton.setIcon(QtGui.QIcon('resources/noun_Plus_icon.png'))
        self.setCornerWidget(addTabButton, QtCore.Qt.TopRightCorner)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.add_new_tab()

    def add_new_tab(self, label="unititled.txt"):
        self.tab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setObjectName("tab")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.horizontalLayout_7.addWidget(self.plainTextEdit)
        self.addTab(self.tab, label)
 
    def close_tab(self, index):
        if self.count() < 2:
            return

        self.removeTab(index)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(747, 601)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Box = QtWidgets.QWidget(self.centralwidget)
        self.Box.setObjectName("Box")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.Box)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Menu_Notes_Tags = QtWidgets.QVBoxLayout()
        self.Menu_Notes_Tags.setObjectName("Menu_Notes_Tags")
        self.Menu = QtWidgets.QFrame(self.Box)
        self.Menu.setMaximumSize(QtCore.QSize(16777215, 80))
        self.Menu.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Menu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Menu.setObjectName("Menu")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.Menu)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.widget = QtWidgets.QWidget(self.Menu)
        self.widget.setObjectName("widget")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(0, 0, 71, 71))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("resources/logo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(self.Menu)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.pushButton_2 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_2.setMaximumSize(QtCore.QSize(80, 16777215))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_5.addWidget(self.pushButton_2)
        self.pushButton = QtWidgets.QPushButton(self.widget_2)
        self.pushButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_5.addWidget(self.pushButton)
        self.horizontalLayout_4.addWidget(self.widget_2)
        self.widget_3 = QtWidgets.QWidget(self.Menu)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_4.addWidget(self.widget_3)
        self.Menu_Notes_Tags.addWidget(self.Menu)
        self.Notes_Tags = QtWidgets.QWidget(self.Box)
        self.Notes_Tags.setObjectName("Notes_Tags")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.Notes_Tags)
        self.horizontalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.Tags = QtWidgets.QFrame(self.Notes_Tags)
        self.Tags.setMaximumSize(QtCore.QSize(200, 16777215))
        self.Tags.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Tags.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Tags.setObjectName("Tags")
        self.horizontalLayout_3.addWidget(self.Tags)
        self.Notes = QtWidgets.QWidget(self.Notes_Tags)
        self.Notes.setObjectName("Notes")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.Notes)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.Notes.setSizePolicy(sizePolicy)
 
        # Custom TabWidget for notes
        self.tabWidget = NotesTabWidget(self.Notes) 

        self.horizontalLayout_6.addWidget(self.tabWidget)
        self.horizontalLayout_3.addWidget(self.Notes)
        self.Tools = QtWidgets.QFrame(self.Notes_Tags)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Tools.sizePolicy().hasHeightForWidth())
        self.Tools.setSizePolicy(sizePolicy)
        self.Tools.setMaximumSize(QtCore.QSize(25, 120))
        self.Tools.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Tools.setObjectName("Tools")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.Tools)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.toolButton = QtWidgets.QToolButton(self.Tools)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/italics.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon)
        self.toolButton.setObjectName("toolButton")
        self.verticalLayout.addWidget(self.toolButton)
        self.toolButton_2 = QtWidgets.QToolButton(self.Tools)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("resources/bold.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_2.setIcon(icon1)
        self.toolButton_2.setObjectName("toolButton_2")
        self.verticalLayout.addWidget(self.toolButton_2)
        self.toolButton_3 = QtWidgets.QToolButton(self.Tools)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("resources/underline.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton_3.setIcon(icon2)
        self.toolButton_3.setObjectName("toolButton_3")
        self.verticalLayout.addWidget(self.toolButton_3)
        self.horizontalLayout_9.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addWidget(self.Tools, 0, QtCore.Qt.AlignTop)
        self.Menu_Notes_Tags.addWidget(self.Notes_Tags)
        self.horizontalLayout_2.addLayout(self.Menu_Notes_Tags)
        self.horizontalLayout.addWidget(self.Box)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 747, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_2.setText(_translate("MainWindow", "Home"))
        self.pushButton.setText(_translate("MainWindow", "Add"))
        # self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.toolButton.setText(_translate("MainWindow", "..."))
        self.toolButton_2.setText(_translate("MainWindow", "..."))
        self.toolButton_3.setText(_translate("MainWindow", "..."))

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
    sys.exit(app.exec_())
