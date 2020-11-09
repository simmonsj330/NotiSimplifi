#!/usr/bin/env python3

# Source code for NotiSimplifi
# Authors: Team Ironman -- James, Terryl, and Ryan

import glob
import os
import sys
import xml.etree.ElementTree as et

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEventLoop, QTimer, Qt, QSize, QDir
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog


class TabBar(QTabBar):
    def __init__(self, parent):
        super(TabBar, self).__init__()
        self.parent = parent
        self.setAutoFillBackground(True)
        self.setStyleSheet("""
            QTabBar::close-button {
                image: url(./resources/delete_tab.png);
                subcontrol-position: left;
            }
            QTabBar::tab {
                color: black;
                background: #77dd77;
                border-left: 1px solid black;
                text-align: center;
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
                font: bold;
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
        max_width = int(self.parent.width()) - \
                    int(self.parent.addTabButton.width())
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
        # self.currentChanged.connect(self.setToolBar)
        self.add_new_tab()

    # this prevents duplicate file names so that way we don't overwrite
    # any existing note files
    def get_valid_name(self, label):
        # remove leading and trailing whitespace
        label = label.strip()

        # create list of all current file names
        current_tab_names = [self.tabBar().tabText(i)
                             for i in range(self.count())]
        saved_file_names = [os.path.basename(
            name) for name in glob.glob("saved_notes/*.txt")]
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

    def setStrikethrough(self):
        textEdit = self.currentWidget().plainTextEdit
        format = textEdit.currentCharFormat()
        format.setFontStrikeOut(not format.fontStrikeOut())
        textEdit.setCurrentCharFormat(format)

    def printNote(self):
        printer = QPrinter(QPrinter.HighResolution)
        printerDialog = QPrintDialog(printer, self)
        if printerDialog.exec_() == QPrintDialog.Accepted:
            self.currentWidget().plainTextEdit.print_(printer)

    def printPreview(self):
        printer = QPrinter(QPrinter.HighResolution)
        printPreview = QPrintPreviewDialog(printer, self)
        printPreview.paintRequested.connect(self.printPreviewText)
        printPreview.exec_()

    def printPreviewText(self, printer):
        self.currentWidget().plainTextEdit.print_(printer)

    def undoText(self):
        self.currentWidget().plainTextEdit.undo()

    def redoText(self):
        self.currentWidget().plainTextEdit.undo()

    def setLeftAlign(self):
        self.currentWidget().plainTextEdit.setAlignment(Qt.AlignLeft)

    def setRightAlign(self):
        self.currentWidget().plainTextEdit.setAlignment(Qt.AlignRight)

    def setCenterAlign(self):
        self.currentWidget().plainTextEdit.setAlignment(Qt.AlignCenter)

    def setJustify(self):
        self.currentWidget().plainTextEdit.setAlignment(Qt.AlignJustify)

    def indentRight(self):
        text = self.currentWidget().plainTextEdit

        cursor = text.textCursor()
        cursor.clearSelection()

        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        cursor.movePosition(QtGui.QTextCursor.NextWord, QtGui.QTextCursor.KeepAnchor)
        newText = '    ' + cursor.selectedText()
        cursor.insertText(newText)

    def indentLeft(self):
        text = self.currentWidget().plainTextEdit

        cursor = text.textCursor()
        cursor.clearSelection()

        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        cursor.movePosition(QtGui.QTextCursor.NextWord, QtGui.QTextCursor.KeepAnchor)
        tmpText = cursor.selectedText()

        if tmpText.startswith('    '):
            newText = tmpText.replace('    ', '', 1)
            cursor.insertText(newText)

    def setSuperscript(self):
        textEdit = self.currentWidget().plainTextEdit
        curCharFormat = textEdit.currentCharFormat()

        if curCharFormat.verticalAlignment() == QtGui.QTextCharFormat.AlignSuperScript:
            curCharFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)
        else:
            curCharFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)

        textEdit.setCurrentCharFormat(curCharFormat)

    def setSubscript(self):
        textEdit = self.currentWidget().plainTextEdit
        curCharFormat = textEdit.currentCharFormat()

        if curCharFormat.verticalAlignment() == QtGui.QTextCharFormat.AlignSubScript:
            curCharFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)
        else:
            curCharFormat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)

        textEdit.setCurrentCharFormat(curCharFormat)

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

            # added the checks for false or true to handle when signal fills the name argument
            if name == "" or name == False or name == True:
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

    # code from https://pythonprogramming.net/open-files-pyqt-tutorial/
    def openTab(self):
        name, _filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        
        if name != "":
            file = open(name, 'r')

            # strip path and file extension from file name
            name = os.path.splitext(os.path.basename(name))[0]

            # check to see if file is already open
            current_tab_names = [self.tabBar().tabText(i) for i in range(self.count())]

            inUse = True
            try:
                temp = current_tab_names.index(name)
            except ValueError:
                # if exception is hit, the file is not in use
                inUse = False

            if inUse:
                # self.setCurrentWidget(self, temp)
                self.setCurrentIndex(temp)
                return
            
            # create new tab for file
            # TODO: add check here to see if any tabs are open, if none are, use the initial tab
            self.add_new_tab()

            # write the files text to the new tab's textedit and setting
            # the tab name to the file's name
            with file:
                text = file.read()
                self.tabBar().setTabText(self.currentIndex(), name)
                self.currentWidget().plainTextEdit.setText(text)

            # since it is already a saved note, we are setting it's
            # saveState to True to turn on "auto save"
            self.currentWidget().saveState = True

    #Mostly same as 'openTab' except we dont manipulate save states and make the file non-editable
    def openAbout(self):
        
        #This is a temporary place holder for the file until we fix constant paths issue
        #it will not work on other machines
        name = "/Users/james/Desktop/Fall2020/340/team-ironman/resources/About.txt"
        if name != "":
            file = open(name, 'r')

            # strip path and file extension from file name
            name = os.path.splitext(os.path.basename(name))[0]

            # check to see if file is already open
            current_tab_names = [self.tabBar().tabText(i) for i in range(self.count())]

            inUse = True
            try:
                temp = current_tab_names.index(name)
            except ValueError:
                # if exception is hit, the file is not in use
                inUse = False

            if inUse:
                self.setCurrentIndex(temp)
                return
            
            # create new tab for file
            self.add_new_tab()

            # write the files text to the new tab's textedit and setting
            with file:
                text = file.read()
                self.tabBar().setTabText(self.currentIndex(), name)
                self.currentWidget().plainTextEdit.setText(text)
            
            #Setting file to non-editable
            self.currentWidget().plainTextEdit.setReadOnly(True)

    def folderTab(self):
        self.text_name = QLineEdit(self)
        self.text_name.move(100,22)
        self.text_name.setPlaceholderText("Enter folder name:")

        text, result = QInputDialog.getText(self, 'Add Folder', 'Folder Name:')
        if result == True:
            self.text_name.setText(str(text))
            path = QDir.currentPath()
            os.mkdir(path + '/' + text)

    def fileTab(self):
        self.text_name = QLineEdit(self)
        self.text_name.move(100,22)
        self.text_name.setPlaceholderText("Enter file name:")

        text, result = QInputDialog.getText(self, 'Add File', 'File Name:')
        if result == True:
            self.text_name.setText(str(text))
            self.add_new_tab()
            path = QDir.currentPath()
            os.system('touch ' + path + '/' + text + '.txt')
            
            index = self.currentIndex()
            nameChange = self.savedTabNameChange(text)
            if nameChange:
                self.setTabText(index, text) 

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

    def menubar_newtab(self):
        self.add_new_tab()


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

        self.centralwidget.setAutoFillBackground(True)

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
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        # self.horizontalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.Tags = QtWidgets.QFrame(self.Notes_Tags)
        self.Tags.setMaximumSize(QtCore.QSize(200, 16777215))
        # self.Tags.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Tags.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Tags.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Tags.setObjectName("Tags")

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Tags)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setSpacing(0)

        # Tree widget
        '''self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)'''

        # path = '/saved_notes'
        self.model = QFileSystemModel()
        # print(QDir.setPath(path))
        self.model.setRootPath(QDir.currentPath())
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.currentPath()))
        self.tree.setGeometry(QtCore.QRect(0, 0, 201, 481))

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        self.tree.setWindowTitle("Dir View")

        # https://stackoverflow.com/questions/58937754/hide-size-type-and-date-modified-columns-in-qfilesystemmodel
        for i in range(1, self.tree.model().columnCount()):
            self.tree.header().hideSection(i)

        self.verticalLayout_3.addWidget(self.tree)

        self.Tags.setStyleSheet("""
            background-color: #282f39;
            color: white;
        """)

        self.horizontalLayout_3.addWidget(self.Tags)
        self.Notes = QtWidgets.QFrame(self.Notes_Tags)
        self.Notes.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Notes.setFrameShadow(QtWidgets.QFrame.Plain)
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

        # self.horizontalLayout_6.addLayout(self.tabWidgetHorizontalLayout)
        self.horizontalLayout_6.addWidget(self.tabWidget)
        self.horizontalLayout_3.addWidget(self.Notes)

        # self.horizontalLayout_9.addLayout(self.verticalLayout)
        # self.horizontalLayout_3.addWidget(self.Tools, 0, QtCore.Qt.AlignTop)
        self.Menu_Notes_Tags.addWidget(self.Notes_Tags)
        self.horizontalLayout_2.addLayout(self.Menu_Notes_Tags)
        self.horizontalLayout.addWidget(self.Box)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.addMenubar = self.menubar.addMenu('&Add')

        # Added this line to show menu bar in the app window
        self.menubar.setNativeMenuBar(False)
        
        # addMenu.setNativeMenuBar(False)

        # Initializing menu bar
        self.menubar.setGeometry(QtCore.QRect(0, 0, 747, 22))
        self.menubar.setObjectName("menubar")

        self.menubar.setStyleSheet("""
            background-color: #2b3844;
            color: white;
        """)

        # Initializing menu objects
        # Notisimplifi
        self.menu_Notisimplifi = QtWidgets.QMenu(self.menubar)
        self.menu_Notisimplifi.setObjectName("menu_Notisimplifi")
        # File
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        # Edit
        self.menu_Edit = QtWidgets.QMenu(self.menubar)
        self.menu_Edit.setObjectName("menu_Edit")
        # Add
        self.menu_Add = QtWidgets.QMenu(self.menubar)
        self.menu_Add.setObjectName("menu_Add")
        MainWindow.setMenuBar(self.menubar)

        # initalize section for add button
        # addMenu.setGeometry(QtCore.QRect(500, 0, 200, 50))
        '''self.addMenubar.setObjectName("addmenu")
        self.add_button = QtWidgets.QMenu(self.addMenubar)
        self.add_button.setObjectName("add_button")'''
        # MainWindow.setMenuBar(addMenu)

        '''
        Initializing menubar action objects
        They are grouped together by what menubar section they are under
        '''
        # Add Folder and Add File
        self.addFolder = QtWidgets.QAction(MainWindow)
        self.addFolder.setObjectName("addFolder")
        self.addFile = QtWidgets.QAction(MainWindow)
        self.addFile.setObjectName("addFile")

        # TODO wtf is this section here for?
        # Initialize add button functionality
        self.actionAdd = QtWidgets.QAction(MainWindow)
        self.actionAdd.setObjectName("actionAdd")

        # About and Quit
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout.setToolTip('This is action 1')
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")

        # Open and Save
        self.actionNewtab = QtWidgets.QAction(MainWindow)
        self.actionNewtab.setObjectName("actionOpen")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveas = QtWidgets.QAction(MainWindow)
        self.actionSaveas.setObjectName("actionSaveas")

        # Undo and Copy
        self.actionUndo = QtWidgets.QAction(MainWindow)
        self.actionUndo.setObjectName("actionUndo")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionPaste = QtWidgets.QAction(MainWindow)
        self.actionPaste.setObjectName("actionPaste")

        # connecting action to current tab
        self.actionAbout.triggered.connect(self.tabWidget.openAbout)
        self.actionSave.triggered.connect(self.tabWidget.saveTab)
        self.actionOpen.triggered.connect(self.tabWidget.openTab)
        self.actionNewtab.triggered.connect(self.tabWidget.menubar_newtab)
        self.addFolder.triggered.connect(self.tabWidget.folderTab)
        self.addFile.triggered.connect(self.tabWidget.fileTab)

        # Setting layout and separators of 'File' drop down actions
        self.menu_Notisimplifi.addAction(self.actionAbout)
        self.menu_Notisimplifi.addSeparator()
        self.menu_Notisimplifi.addAction(self.actionQuit)

        # Setting layout and seperators of 'File' drop down actions
        self.menu_File.addAction(self.actionNewtab)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionOpen)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionSave)
        self.menu_File.addAction(self.actionSaveas)
        # self.menu_File.addSeparator()
        # self.menu_File.addAction()

        # Setting layout and separators of 'Edit' drop down actions
        self.menu_Edit.addAction(self.actionUndo)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.actionCopy)
        self.menu_Edit.addAction(self.actionPaste)

        # Setting layout and seperators of 'Add' drop down actions
        self.menu_Add.addAction(self.addFolder)
        self.menu_Add.addSeparator()
        self.menu_Add.addAction(self.addFile)

        # Adding actions to menu actions that can take place
        self.menubar.addAction(self.menu_Notisimplifi.menuAction())
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_Add.menuAction())

        ###################################################################
        #                     TOOLBAR and TOOL BUTTONS                    #
        ###################################################################
        self.tb2 = QtWidgets.QToolBar(MainWindow)
        self.tb2.setFloatable(False)
        self.tb2.setMovable(False)
        self.tb2.setIconSize(QSize(20, 20))

        # prevents users from right clicking and hiding the toolbar
        self.tb2.setContextMenuPolicy(Qt.PreventContextMenu)

        MainWindow.addToolBar(self.tb2)
        # self.tb.setOrientation(Qt.Vertical)
        # self.tb.setGeometry(QtCore.QRect(0, 0, 747, 22))

        # self.tb2.addSeparator()

        # undo button
        self.undo_icon = QtGui.QIcon()
        self.undo_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/undo-new.png"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
        self.undoButton = QAction(self.undo_icon, '', self.tb2)
        self.undoButton.setToolTip('Undo')
        self.undoButton.triggered.connect(self.tabWidget.undoText)
        self.tb2.addAction(self.undoButton)

        # redo button
        self.redo_icon = QtGui.QIcon()
        self.redo_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/redo-new.png"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
        self.redoButton = QAction(self.redo_icon, '', self.tb2)
        self.redoButton.setToolTip('Redo')
        self.redoButton.triggered.connect(self.tabWidget.redoText)
        self.tb2.addAction(self.redoButton)

        # save button
        self.save_icon = QtGui.QIcon()
        self.save_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/save.png"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
        self.saveButton = QAction(self.save_icon, '', self.tb2)
        self.saveButton.setToolTip('Save')
        self.saveButton.triggered.connect(self.tabWidget.saveTab)
        self.tb2.addAction(self.saveButton)
        # self.tb2.addSeparator()

        # newFile button
        self.newFile_icon = QtGui.QIcon()
        self.newFile_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/document-1.png"),
                                    QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.newFileButton = QAction(self.newFile_icon, '', self.tb2)
        self.newFileButton.setToolTip('New Note')
        self.newFileButton.triggered.connect(self.tabWidget.menubar_newtab)
        self.tb2.addAction(self.newFileButton)
        # self.tb2.addSeparator()

        # print button
        self.print_icon = QtGui.QIcon()
        self.print_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/printer.png"), QtGui.QIcon.Normal,
                                  QtGui.QIcon.Off)
        self.printButton = QAction(self.print_icon, '', self.tb2)
        self.printButton.setToolTip('Print')
        self.printButton.triggered.connect(self.tabWidget.printNote)
        self.tb2.addAction(self.printButton)
        # self.tb2.addSeparator()

        # print preview button
        self.printPreview_icon = QtGui.QIcon()
        self.printPreview_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/preview.png"),
                                         QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.printPreviewButton = QAction(self.printPreview_icon, '', self.tb2)
        self.printPreviewButton.setToolTip('Print Preview')
        self.printPreviewButton.triggered.connect(self.tabWidget.printPreview)
        self.tb2.addAction(self.printPreviewButton)
        # self.tb2.addSeparator()

        self.tb2.addSeparator()

        # bold button
        self.bold_icon = QtGui.QIcon()
        self.bold_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/bold.png"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
        self.boldButton = QAction(self.bold_icon, '', self.tb2)
        self.boldButton.setCheckable(True)
        self.boldButton.setToolTip('Bold')
        self.boldButton.triggered.connect(self.tabWidget.setBold)  # pass in bold button
        self.tb2.addAction(self.boldButton)
        # self.tb2.addSeparator()

        # underline button
        self.underline_icon = QtGui.QIcon()
        self.underline_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/underline.png"),
                                      QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.underlineButton = QAction(self.underline_icon, '', self.tb2)
        self.underlineButton.setCheckable(True)
        self.underlineButton.setToolTip('Underline')
        self.underlineButton.triggered.connect(self.tabWidget.setUnderline)
        self.tb2.addAction(self.underlineButton)
        # self.tb2.addSeparator()

        # italic button
        self.italic_icon = QtGui.QIcon()
        self.italic_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/italic.png"), QtGui.QIcon.Normal,
                                   QtGui.QIcon.Off)
        self.italicButton = QAction(self.italic_icon, '', self.tb2)
        self.italicButton.setCheckable(True)
        self.italicButton.setToolTip('Italic')
        self.italicButton.triggered.connect(self.tabWidget.setItalic)
        self.tb2.addAction(self.italicButton)
        # self.tb2.addSeparator()

        # strikethrough button
        self.strikethrough_icon = QtGui.QIcon()
        self.strikethrough_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/strikethrough.png"),
                                          QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.strikethroughButton = QAction(self.strikethrough_icon, '', self.tb2)
        self.strikethroughButton.setCheckable(True)
        self.strikethroughButton.setToolTip('Strikethrough')
        self.strikethroughButton.triggered.connect(self.tabWidget.setStrikethrough)
        self.tb2.addAction(self.strikethroughButton)
        # self.tb2.addSeparator()

        # superscript button
        self.superscript_icon = QtGui.QIcon()
        self.superscript_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/superscript.png"),
                                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.superscriptButton = QAction(self.superscript_icon, '', self.tb2)
        self.superscriptButton.setCheckable(True)
        self.superscriptButton.setToolTip('Superscript')
        self.superscriptButton.triggered.connect(self.tabWidget.setSuperscript)
        self.tb2.addAction(self.superscriptButton)
        # self.tb2.addSeparator()

        # subscript button
        self.subscript_icon = QtGui.QIcon()
        self.subscript_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/subscript.png"),
                                      QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.subscriptButton = QAction(self.subscript_icon, '', self.tb2)
        self.subscriptButton.setCheckable(True)
        self.subscriptButton.setToolTip('Subscript')
        self.subscriptButton.triggered.connect(self.tabWidget.setSubscript)
        self.tb2.addAction(self.subscriptButton)
        # self.tb2.addSeparator()

        self.tb2.addSeparator()

        # left align
        self.leftAlign_icon = QtGui.QIcon()
        self.leftAlign_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/left-alignment.png"),
                                      QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.leftAlignButton = QAction(self.leftAlign_icon, '', self.tb2)
        # self.leftAlignButton.setCheckable(True)
        self.leftAlignButton.setToolTip('Align Left')
        self.leftAlignButton.triggered.connect(self.tabWidget.setLeftAlign)
        self.tb2.addAction(self.leftAlignButton)
        # self.tb2.addSeparator()

        # center align
        self.centerAlign_icon = QtGui.QIcon()
        self.centerAlign_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/center-alignment.png"),
                                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.centerAlignButton = QAction(self.centerAlign_icon, '', self.tb2)
        # self.centerAlignButton.setCheckable(True)
        self.centerAlignButton.setToolTip('Center Text')
        self.centerAlignButton.triggered.connect(self.tabWidget.setCenterAlign)
        self.tb2.addAction(self.centerAlignButton)
        # self.tb2.addSeparator()

        # right align
        self.rightAlign_icon = QtGui.QIcon()
        self.rightAlign_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/right-alignment.png"),
                                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rightAlignButton = QAction(self.rightAlign_icon, '', self.tb2)
        # self.rightAlignButton.setCheckable(True)
        self.rightAlignButton.setToolTip('Align Right')
        self.rightAlignButton.triggered.connect(self.tabWidget.setRightAlign)
        self.tb2.addAction(self.rightAlignButton)
        # self.tb2.addSeparator()

        # justify
        self.justify_icon = QtGui.QIcon()
        self.justify_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/justify-align.png"),
                                    QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.justifyButton = QAction(self.justify_icon, '', self.tb2)
        self.justifyButton.setToolTip('Align Right')
        self.justifyButton.triggered.connect(self.tabWidget.setJustify)
        self.tb2.addAction(self.justifyButton)
        # self.tb2.addSeparator()

        # right indent
        self.rightIdent_icon = QtGui.QIcon()
        self.rightIdent_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/indent.png"),
                                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rightIdentButton = QAction(self.rightIdent_icon, '', self.tb2)
        self.rightIdentButton.setToolTip('Justify')
        self.rightIdentButton.triggered.connect(self.tabWidget.indentRight)
        self.tb2.addAction(self.rightIdentButton)
        # self.tb2.addSeparator()

        # left indent
        self.leftIdent_icon = QtGui.QIcon()
        self.leftIdent_icon.addPixmap(QtGui.QPixmap("resources/potential_icons/icons5/png/outdent.png"),
                                      QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.leftIdentButton = QAction(self.leftIdent_icon, '', self.tb2)
        self.leftIdentButton.setToolTip('Indent Left')
        self.leftIdentButton.triggered.connect(self.tabWidget.indentLeft)
        self.tb2.addAction(self.leftIdentButton)
        # self.tb2.addSeparator()

        # QToolBar::separator:horizontal {
        #   image: url("./resources/potential_icons/icons5/png/separator-gray.png");
        # }

        self.tb2.setStyleSheet("""
            QToolBar {
              background-color: #212b34;
              border-bottom: 1px solid #212b34;
            }

            QToolBar::separator:horizontal {
              background-color: #212b34;
              width: 1px;
              margin-left: 10px;
              margin-right: 10px;
            }

            QToolBar QToolButton {
              background-color: #212b34;
              border: 1px solid #212b34;
              border-radius: 2px;
            }

            QToolBar QToolButton QToolTip {
              color: white;
              border: 1px solid gray;
              border-radius: 3px;
            }

            QToolBar QToolButton:hover {
              border: 1px solid #77dd77;
            }

            QToolBar QToolButton:checked {
              border: 1px solid #b4ecb4;
              background-color: #5d7992;
            }

            QToolBar QToolButton:checked:hover {
              border: 1px solid #77dd77;
            }
        """)
        # background - color:  # 19232D;
        # border: 1px solid #b4ecb4;

        ###################################################################
        #                     TOOLBAR and TOOL BUTTONS                    #
        ###################################################################

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", ""))
        # self.pushButton.setText(_translate("MainWindow", "Add"))

        # self.toolButton.setText(_translate("MainWindow", "..."))
        # self.toolButton_2.setText(_translate("MainWindow", "..."))
        # self.toolButton_3.setText(_translate("MainWindow", "..."))

        self.menu_Notisimplifi.setTitle(_translate("MainWindow", "&Notisimplifi"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.menu_Edit.setTitle(_translate("MainWindow", "&Edit"))
        self.menu_Add.setTitle(_translate("MainWindow", "&Add"))

        self.addFolder.setText(_translate("MainWindow", "Folder"))
        self.addFolder.setShortcut(_translate("MainWindow", "Ctrl+F"))

        self.addFile.setText(_translate("MainWindow", "Notes File"))
        self.addFile.setShortcut(_translate("MainWindow", "Ctrl+N"))

        self.actionAbout.setText(_translate("MainWindow", "About"))

        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q"))

        self.actionNewtab.setText(_translate("MainWindow", "New Tab"))
        self.actionNewtab.setShortcut(_translate("MainWindow", "Ctrl+T"))

        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))

        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))


        self.actionSaveas.setText(_translate("MainWindow", "Save As..."))
        self.actionSaveas.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))

        self.actionUndo.setText(_translate("MainWindow", "Undo"))
        self.actionUndo.setShortcut(_translate("MainWindow", "Ctrl+Z"))

        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionCopy.setShortcut(_translate("MainWindow", "Ctrl+C"))

        self.actionPaste.setText(_translate("MainWindow", "Paste"))
        self.actionPaste.setShortcut(_translate("MainWindow", "Ctrl+V"))

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
