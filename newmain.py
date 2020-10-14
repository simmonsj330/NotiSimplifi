#!/usr/bin/env python3

import sys
import os
import glob
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtWidgets import QSplashScreen, QTabBar, QInputDialog, QAction
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
            newName = self.parent.get_valid_name(newName)
            self.setTabText(index, newName)

class TabPlainTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super(TabPlainTextEdit, self).__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setObjectName("textEdit")
        # self.textChanged.connect(self.parent.parent.save_tab)
        

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

    # this prevents duplicate file names so that way we don't overwrite
    # any existing note files
    def get_valid_name(self, label):
        # remove leading and trailing whitespace
        label = label.strip()

        # create list of all current file names
        current_tab_names = [self.tabBar().tabText(i) for i in range(self.count())]
        saved_file_names = [os.path.basename(name) for name in glob.glob("saved_notes/*.txt")]
    
        # combines the two lists above into a single list of unique values
        used_names = list(set(current_tab_names + saved_file_names))

        taken = True
        base_name = label
        num = 1 
        while True:
            label += '.txt'

            # This try catch is necessary because {list}.index() will return 
            # a ValueError if a match isn't found. If a ValueError is returned
            # then we know that a file name is valid and we can break out of 
            # the loop.
            try:
                temp = used_names.index(label)
            except ValueError:
                break

            # if we get here name is taken
            label = base_name + str(num)
            num+=1

        return label
 
    def add_new_tab(self, label="untitled"):
        self.tab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setObjectName("tab")
        self.tab.setAccessibleName("tab")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        
        self.tab.plainTextEdit = TabPlainTextEdit(self.tab)
        self.tab.plainTextEdit.textChanged.connect(self.save_tab)
        self.horizontalLayout_7.addWidget(self.tab.plainTextEdit)

        label = self.get_valid_name(label)
        
        self.addTab(self.tab, label)

        self.setCurrentWidget(self.tab)
	
    def setItalic(self):
        italic = self.currentWidget().plainTextEdit.fontItalic()
        for i in range(self.count()):
            if italic:
                self.widget(i).plainTextEdit.setFontItalic(False)
            else:
                self.widget(i).plainTextEdit.setFontItalic(True)

    def setBold(self):
        # get current text edit font weight
        weight = self.currentWidget().plainTextEdit.fontWeight()

        # set weight for all tabs
        for i in range(self.count()):
            if weight == QtGui.QFont.Bold:
                self.widget(i).plainTextEdit.setFontWeight(QtGui.QFont.Normal)
            else:
                self.widget(i).plainTextEdit.setFontWeight(QtGui.QFont.Bold)

    def setUnderline(self):
        underline = self.currentWidget().plainTextEdit.fontUnderline()
        for i in range(self.count()):
            if underline:
                self.widget(i).plainTextEdit.setFontUnderline(False)
            else:
                self.widget(i).plainTextEdit.setFontUnderline(True)


    def close_tab(self, index):
        # will not close current tab if it's the only tab open
        if self.count() < 2:
            return
        self.removeTab(index)

    def save_tab(self):
        note_text = self.tab.plainTextEdit.toPlainText()
        # TODO: change this to {current directory}/saved_notes/{note_name}
        file_name = 'saved_notes/' + self.tabText(self.currentIndex())
        with open(file_name, 'w') as note:
            note.write(note_text)
    
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
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Tags)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.treeWidget = QtWidgets.QTreeWidget(self.Tags)
        self.treeWidget.setUniformRowHeights(False)
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.verticalLayout_2.addWidget(self.treeWidget)

        self.widget = QtWidgets.QWidget(self.Tags)
        self.widget.setObjectName("widget")
        self.verticalLayout_2.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(self.Tags)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton = QtWidgets.QPushButton(self.widget_2)
        self.pushButton.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout_2.addWidget(self.widget_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3.addWidget(self.Tags)
        self.Notes = QtWidgets.QWidget(self.Notes_Tags)
        self.Notes.setObjectName("Notes")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.Notes)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")


        #Custom Written to fit within horizontal layout 6
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.Notes.setSizePolicy(sizePolicy)
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

        self.italicButton = QtWidgets.QToolButton(self.Tools)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/italics.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.italicButton.setIcon(icon)
        self.italicButton.setObjectName("italicButton")
        self.verticalLayout.addWidget(self.italicButton)
        self.italicButton.clicked.connect(self.tabWidget.setItalic)

        self.boldButton = QtWidgets.QToolButton(self.Tools)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("resources/bold.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.boldButton.setIcon(icon1)
        self.boldButton.setObjectName("boldButton")
        self.verticalLayout.addWidget(self.boldButton)
        self.boldButton.clicked.connect(self.tabWidget.setBold)

        self.underlineButton = QtWidgets.QToolButton(self.Tools)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("resources/underline.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.underlineButton.setIcon(icon2)
        self.underlineButton.setObjectName("underlineButton")
        self.verticalLayout.addWidget(self.underlineButton)
        self.underlineButton.clicked.connect(self.tabWidget.setUnderline)

        self.horizontalLayout_9.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addWidget(self.Tools, 0, QtCore.Qt.AlignTop)
        
        self.Menu_Notes_Tags.addWidget(self.Notes_Tags)
        self.horizontalLayout_2.addLayout(self.Menu_Notes_Tags)
        self.horizontalLayout.addWidget(self.Box)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)

        #Added this line to show menu bar in the app window
        self.menubar.setNativeMenuBar(False)      

        #Initializing menu bar
        self.menubar.setGeometry(QtCore.QRect(0, 0, 747, 22))
        self.menubar.setObjectName("menubar")
        self.menu_Notisimplifi = QtWidgets.QMenu(self.menubar)
        self.menu_Notisimplifi.setObjectName("menu_Notisimplifi")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        MainWindow.setMenuBar(self.menubar)

        #Initializing menu bar 'Notisimplifi' drop down actions
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")

        #Initializing menu bar 'File' drop down actions
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")

        #Setting layout and seperators of 'File' drop down actions
        self.menu_Notisimplifi.addAction(self.actionAbout)
        self.menu_Notisimplifi.addSeparator()
        self.menu_Notisimplifi.addAction(self.actionQuit)

        #Setting layout and seperators of 'File' drop down actions
        self.menu_File.addAction(self.actionOpen)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionSave)

        #Adding actions to menu actions that can take place
        self.menubar.addAction(self.menu_Notisimplifi.menuAction())
        self.menubar.addAction(self.menu_File.menuAction())
        
        # self.statusbar = QtWidgets.QStatusBar(MainWindow)
        # self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Add"))
        # self.toolButton.setText(_translate("MainWindow", "..."))
        # self.toolButton_2.setText(_translate("MainWindow", "..."))
        # self.toolButton_3.setText(_translate("MainWindow", "..."))

        self.menu_Notisimplifi.setTitle(_translate("MainWindow", "&Notisimplifi"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))

        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Senior Courses"))
        #__sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("MainWindow", "Senior Design"))
        self.treeWidget.topLevelItem(0).child(0).setText(0, _translate("MainWindow", "Intro to Course"))
        self.treeWidget.topLevelItem(0).child(1).setText(0, _translate("MainWindow", "Resume/CV"))
        self.treeWidget.topLevelItem(0).child(2).setText(0, _translate("MainWindow", "Project Management"))
        self.treeWidget.topLevelItem(1).setText(0, _translate("MainWindow", "Software Engineering"))
        self.treeWidget.topLevelItem(1).child(0).setText(0, _translate("MainWindow", "Project Iterations"))
        self.treeWidget.topLevelItem(1).child(1).setText(0, _translate("MainWindow", "Process"))
        self.treeWidget.topLevelItem(1).child(2).setText(0, _translate("MainWindow", "Usability"))

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
    QTimer.singleShot(1000, loop.quit)
    loop.exec_()

    w = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(w)

    w.show()

    # stop showing splashscreen once main form has loaded in
    splashScreen.finish(w)
    sys.exit(app.exec_())
