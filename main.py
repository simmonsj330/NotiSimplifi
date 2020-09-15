#!/usr/bin/env python3

'''
File: main.py
Description:
    Holds the main functions for the application
'''
import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFrame, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QColor

'''
Note:
    For some reason, the pylinter throws a false error when importing like this
        from PyQt5.QtWidgets import QApplication

    In order to get around this, one can simply imported qtwidgets as a whole then called specific functions like so
        self.QWidgets.QMainWindow.setwindowTitle()
    This seems tedious just to type functions, so I opted to just use the from-import method
    The false error doesnt stop anything from running, its just annoying to see an 'error' all the time

    This may be a James only error though
'''

'''
Description:
    This class inherits from QMainWindow and is used to initialize the application GUI
    Each respective feature can be compartamentalized into their own definition for better organization
'''
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #Initializing the main window name, geometry, and color
        self.setWindowTitle("Team-Ironman Note App")
        self.setGeometry(500, 200, 800, 800)
        self.setStyleSheet('background-color: #505050')


        #Each definition goes here...
        #self...()
        #self...()
        self.tagsframe()
        self.menuframe()

        self.show()

   
    #Create left hand frame to hold the tags menu 
    def tagsframe(self):
        top = QFrame(self)
        top.resize(200, 800)
        top.setStyleSheet('border: 5px solid black;')

    #Creates top frame to hold the add and home button as well as the logo
    def menuframe(self):
        menu_frame = QFrame(self)
        menu_frame.resize(500, 30)
        menu_frame.setStyleSheet('border: 5px solid black;')

        logo_label = QLabel('Logo', self)

        add_button = QPushButton("Add", self) 
        add_button.move(350,5)
        #add_button.clicked.connect(self.clicked)

        home_button = QPushButton("Home", self) 
        home_button.move(450,5)
        #home_button.clicked.connect(self.clicked)

    '''def clicked():
        print('pressed')'''

    '''def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox('')
        layout = QGridLayout()
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 3)
        layout.setColumnStretch(3, 3)
        layout.setColumnStretch(4, 8)

        self.horizontalGroupBox.setLayout(layout)'''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec_()


  