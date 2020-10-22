#!/usr/bin/env python3

# Source code for NotiSimplifi
# Authors: Team Ironman -- James, Terryl, and Ryan

import glob
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEventLoop, QTimer, Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

class TabBar(QTabBar):
    def __init__(self, parent):
        super(TabBar, self).__init__()
        self.parent = parent
        self.setStyleSheet("""
            QTabBar::close-button { 
                image: url(delete_tab.png); 
                subcontrol-position: left; 
            }
            QTabBar::tab { 
                color: black;
                background: #77dd77; 
                border-left: 1px solid black;
            }
            QTabBar::tab::first {
                border-left: none;
            }
            QTabBar::tab::only-one {
                border-left: none;
            }
            QTabBar::tab::hover {
                background: #8be28b;
            }
            QTabBar::tab::selected {
                background: #b4ecb4;
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
        max_width = int(self.parent.width()) - int(self.parent.addTabButton.width())
        width = int(max_width / self.parent.count()) + 1

        return QSize(width, size.height())

    # based on https://stackoverflow.com/questions/44450775/pyqt-gui-with-multiple-tabs
    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.LeftButton:
            super(TabBar, self).mouseDoubleClickEvent(event)

        index = self.currentIndex()
        ok = True
        self.input_dialog = QInputDialog()

        newName, ok = QInputDialog.getText(self, '', 'New file name:')

        if ok:
            allowNameChange = self.parent.savedTabNameChange(newName)
            if allowNameChange:
                self.setTabText(index, newName)


class TabPlainTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super(TabPlainTextEdit, self).__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setObjectName("textEdit")


class NotesTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super(NotesTabWidget, self).__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        # self.setAutoFillBackground(True)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.Black)
        # self.setPalette(p)

        self.tab = TabBar(self)
        self.setTabBar(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setObjectName("tabWidget")

        self.addTabButton = QtWidgets.QToolButton()
        self.addTabButton.setToolTip('Add New Tab')
        self.addTabButton.clicked.connect(lambda: self.add_new_tab())
        self.addTabButton.setIcon(QtGui.QIcon('resources/plus_icon.png'))
        self.addTabButton.setAutoRaise(True)

        self.addTabButton.setStyleSheet("""
            QToolButton {
                background-color: #77dd77; 
                border-left: 1px solid black;
            }
            QToolButton::hover {
                background-color: #8be28b; 
            }
            QToolButton::pressed {
                background-color: #b4ecb4; 
            }
            """)

        self.setCornerWidget(self.addTabButton, QtCore.Qt.TopRightCorner)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.add_new_tab()
        # self.setStyleSheet("""
        #     QTabWidget::pane {
        #         background-color: #171e24;
        #     }
        #     QTabWidget::tab-bar { 
        #         background: #171e24;
        #     }
        # """)

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
            num += 1

        return label

    def add_new_tab(self, label="untitled"):
        # self.setUpdatesEnabled(False)
        self.tab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setObjectName("tab")
        self.tab.setAccessibleName("tab")

        # adding a "save state" to tab
        # set to 'unsaved' as default
        self.tab.saveState = False

        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.tab.plainTextEdit = TabPlainTextEdit(self.tab)

        # Connecting save tab function to text changed property on text edit page
        self.tab.plainTextEdit.textChanged.connect(self.autoSaveTab)
        self.horizontalLayout_7.addWidget(self.tab.plainTextEdit)

        # getting valid name (i.e. a name that is not being used in one of
        # the open tabs or an already saved note

        # label = self.get_valid_name(label)
        self.addTab(self.tab, label)
        # self.setUpdatesEnabled(True)
        self.setCurrentWidget(self.tab)

    # toolbar functions that make the buttons work
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

    def autoSaveTab(self):
        if self.tab.saveState:
            note_text = self.tab.plainTextEdit.toPlainText()
            # TODO: change this to {current directory}/saved_notes/{note_name}
            file_name = 'saved_notes/' + \
                self.tabText(self.currentIndex()) + '.txt'
            with open(file_name, 'w') as note:
                note.write(note_text)

    def saveTab(self, name=" "):
        # if note has not been saved previously
        if not self.tab.saveState:
            note_text = self.tab.plainTextEdit.toPlainText()

            if not name:
                tab_text = self.tabText(self.currentIndex())
                file_name = 'saved_notes/' + tab_text + '.txt'
            else:
                tab_text = name
                file_name = 'saved_notes/' + name + '.txt'

            # TODO: change this to {current directory}/saved_notes/{note_name}
            # this will present user with an error if a note name is already in use
            if not self.validName(tab_text):
                self.errorDialog = ErrorDialog(self, file_name)
                if self.errorDialog.exec_():
                    # close other matching tab if open
                    current_tab_names = [self.tabBar().tabText(i)
                                         for i in range(self.count())]
                    for i in range(self.count()):
                        if (self.tabBar().tabText(i) == tab_text) and (i != self.currentIndex()):
                            self.removeTab(i)

                    os.remove(file_name)
                    with open(file_name, 'w') as note:
                        note.write(note_text)
                    self.tab.saveState = True
                    return True
                else:
                    return False
            else:
                if name:
                    f_name = 'saved_notes/' + \
                        self.tabText(self.currentIndex()) + '.txt'
                    os.remove(f_name)
                with open(file_name, 'w') as note:
                    note.write(note_text)
                self.tab.saveState = True
                return True

    def savedTabNameChange(self, newName):
        if self.tab.saveState == False:
            return True

        self.tab.saveState = False

        if self.saveTab(newName):
            self.tab.saveState = True
            return True
        else:
            self.tab.saveState = True
            return False

    def validName(self, label):
        # remove leading and trailing whitespace
        label = label.strip() + '.txt'

        # create list of all saved notes
        # TODO: change this to check for duplicates in current directory specified by tree
        # once tree has been implemented
        namesInUse = [os.path.basename(name)
                      for name in glob.glob("saved_notes/*.txt")]

        notInUse = False
        # label += '.txt'
        try:
            temp = namesInUse.index(label)
        except ValueError:
            notInUse = True

            # print('in validName', notInUse)

        return notInUse


class ErrorDialog(QtWidgets.QDialog):
    def __init__(self, parent, message):
        super(ErrorDialog, self).__init__(parent)
        self.parent = parent
        self.text = message
        self.initUI()

    def initUI(self):
        temp = "WARNING: '" + self.text + "' already exists!"
        self.label = QLabel(temp)

        rBtn = QPushButton("Replace")
        cBtn = QPushButton("Cancel")
        # sets cancel to default button (i.e. if user hits enter it clicks cancel)
        cBtn.setDefault(True)

        self.btnBox = QDialogButtonBox()
        self.btnBox.setCenterButtons(True)

        self.btnBox.addButton(rBtn, QDialogButtonBox.AcceptRole)
        self.btnBox.addButton(cBtn, QDialogButtonBox.RejectRole)

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.btnBox)
        self.setLayout(self.layout)

# A good portion of this is designer code
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(747, 601)

        MainWindow.setStyleSheet("""
            background: #171e24;
            color: white;
        """)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
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

        # Tree widget
        self.treeWidget = QtWidgets.QTreeWidget(self.Tags)
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 201, 481))
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
        
        #self.widget_2 = QtWidgets.QWidget(self.Tags)
        #self.widget_2.setMaximumSize(QtCore.QSize(16777215, 60))
        #self.widget_2.setObjectName("widget_2")
        #self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_2)
        #self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        #self.pushButton = QtWidgets.QPushButton(self.widget_2)
        #self.pushButton.setMaximumSize(QtCore.QSize(60, 16777215))
        #self.pushButton.setObjectName("pushButton")
        #self.horizontalLayout_4.addWidget(self.pushButton)
        #self.verticalLayout_2.addWidget(self.widget_2)

        self.Tags.setStyleSheet("""
            background-color: #282f39;
            color: white;
        """)

        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3.addWidget(self.Tags)
        self.Notes = QtWidgets.QFrame(self.Notes_Tags)
        self.Notes.setObjectName("Notes")

        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.Notes)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")

        # custom tab widget
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.Notes.setSizePolicy(sizePolicy)

        self.Notes.setStyleSheet("""
            background: #282f39;
            color: white;
            border: none;
        """)

        self.tabWidget = NotesTabWidget(self.Notes)

        self.horizontalLayout_6.addWidget(self.tabWidget)
        self.horizontalLayout_3.addWidget(self.Notes)

        self.Tools = QtWidgets.QFrame(self.Notes_Tags)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.Tools.sizePolicy().hasHeightForWidth())
        self.Tools.setSizePolicy(sizePolicy)
        self.Tools.setMaximumSize(QtCore.QSize(25, 120))
        self.Tools.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.Tools.setObjectName("Tools")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.Tools)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # toolbar bold, italic and underline buttons
        self.italicButton = QtWidgets.QToolButton(self.Tools)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("resources/italics.ico"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.italicButton.setIcon(icon)
        self.italicButton.setObjectName("italicButton")
        self.verticalLayout.addWidget(self.italicButton)
        self.italicButton.clicked.connect(self.tabWidget.setItalic)

        self.boldButton = QtWidgets.QToolButton(self.Tools)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("resources/bold.ico"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.boldButton.setIcon(icon1)
        self.boldButton.setObjectName("boldButton")
        self.verticalLayout.addWidget(self.boldButton)
        self.boldButton.clicked.connect(self.tabWidget.setBold)

        self.underlineButton = QtWidgets.QToolButton(self.Tools)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("resources/underline.ico"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        #self.addMenubar = self.menubar.addMenu('&Add')

        #Added this line to show menu bar in the app window
        self.menubar.setNativeMenuBar(False)     
        #addMenu.setNativeMenuBar(False) 

        # Initializing menu bar
        self.menubar.setGeometry(QtCore.QRect(0, 0, 747, 22))
        self.menubar.setObjectName("menubar")

        self.menubar.setStyleSheet("""
            background-color: #282f39;
            color: white;
        """)

        self.menu_Notisimplifi = QtWidgets.QMenu(self.menubar)
        self.menu_Notisimplifi.setObjectName("menu_Notisimplifi")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Add = QtWidgets.QMenu(self.menubar)
        self.menu_Add.setObjectName("menu_Add")
        #MainWindow.setMenuBar(self.menubar)

        #initalize section for add button
        #addMenu.setGeometry(QtCore.QRect(500, 0, 200, 50))
        '''self.addMenubar.setObjectName("addmenu")
        self.add_button = QtWidgets.QMenu(self.addMenubar)
        self.add_button.setObjectName("add_button")'''
        #MainWindow.setMenuBar(addMenu)

        #Initializing menubar 'Add' drop down actions
        self.addFolder = QtWidgets.QAction(MainWindow)
        self.addFolder.setObjectName("addFolder")
        self.addFile = QtWidgets.QAction(MainWindow)
        self.addFile.setObjectName("addFile")

        # Initialize add button functionality
        self.actionAdd = QtWidgets.QAction(MainWindow)
        self.actionAdd.setObjectName("actionAdd")
    
        # Initializing menu bar 'Notisimplifi' drop down actions
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")

        # Initializing menu bar 'File' drop down actions
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")

        # connecting action to current tab 
        self.actionSave.triggered.connect(self.tabWidget.saveTab)

        # Setting layout and separators of 'File' drop down actions
        self.menu_Notisimplifi.addAction(self.actionAbout)
        self.menu_Notisimplifi.addSeparator()
        self.menu_Notisimplifi.addAction(self.actionQuit)

        # Setting layout and seperators of 'File' drop down actions
        self.menu_File.addAction(self.actionOpen)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionSave)

        self.menu_Add.addAction(self.addFolder)
        self.menu_Add.addSeparator()
        self.menu_Add.addAction(self.addFile)

        #Adding actions to menu actions that can take place
        self.menubar.addAction(self.menu_Notisimplifi.menuAction())
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Add.menuAction())

        # self.statusbar = QtWidgets.QStatusBar(MainWindow)
        # self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_Notisimplifi.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #self.pushButton.setText(_translate("MainWindow", "Add"))

        # self.toolButton.setText(_translate("MainWindow", "..."))
        # self.toolButton_2.setText(_translate("MainWindow", "..."))
        # self.toolButton_3.setText(_translate("MainWindow", "..."))

        self.menu_Notisimplifi.setTitle(
            _translate("MainWindow", "&Notisimplifi"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Add.setTitle(_translate("MainWindow", "&Add"))
        self.addFolder.setText(_translate("MainWindow", "Folder"))
        self.addFile.setText(_translate("MainWindow", "Notes File"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionSave.setText(_translate("MainWindow", "Save"))

        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Senior Courses"))
        # __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("MainWindow", "Senior Design"))
        self.treeWidget.topLevelItem(0).child(0).setText(0, _translate("MainWindow", "Intro to Course"))
        self.treeWidget.topLevelItem(0).child(1).setText(0, _translate("MainWindow", "Resume/CV"))
        self.treeWidget.topLevelItem(0).child(2).setText(0, _translate("MainWindow", "Project Management"))
        self.treeWidget.topLevelItem(1).setText(0, _translate("MainWindow", "Software Engineering"))
        self.treeWidget.topLevelItem(1).child(0).setText(0, _translate("MainWindow", "Project Iterations"))
        self.treeWidget.topLevelItem(1).child(1).setText(0, _translate("MainWindow", "Process"))
        self.treeWidget.topLevelItem(1).child(2).setText(0, _translate("MainWindow", "Usability"))

# executes program
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
