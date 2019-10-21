# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from UI import Ui_MainWindow
import sys
from Sudoku import Sudoku


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Button
        self.ui.pushButton00.clicked.connect(lambda: self.buttonEvent(0, 0))
        self.ui.pushButton00.clicked.connect(lambda: self.buttonEvent(0, 0))
        self.ui.pushButton01.clicked.connect(lambda: self.buttonEvent(0, 1))
        self.ui.pushButton02.clicked.connect(lambda: self.buttonEvent(0, 2))
        self.ui.pushButton03.clicked.connect(lambda: self.buttonEvent(0, 3))
        self.ui.pushButton04.clicked.connect(lambda: self.buttonEvent(0, 4))
        self.ui.pushButton05.clicked.connect(lambda: self.buttonEvent(0, 5))
        self.ui.pushButton06.clicked.connect(lambda: self.buttonEvent(0, 6))
        self.ui.pushButton07.clicked.connect(lambda: self.buttonEvent(0, 7))
        self.ui.pushButton08.clicked.connect(lambda: self.buttonEvent(0, 8))
        self.ui.pushButton10.clicked.connect(lambda: self.buttonEvent(1, 0))
        self.ui.pushButton11.clicked.connect(lambda: self.buttonEvent(1, 1))
        self.ui.pushButton12.clicked.connect(lambda: self.buttonEvent(1, 2))
        self.ui.pushButton13.clicked.connect(lambda: self.buttonEvent(1, 3))
        self.ui.pushButton14.clicked.connect(lambda: self.buttonEvent(1, 4))
        self.ui.pushButton15.clicked.connect(lambda: self.buttonEvent(1, 5))
        self.ui.pushButton16.clicked.connect(lambda: self.buttonEvent(1, 6))
        self.ui.pushButton17.clicked.connect(lambda: self.buttonEvent(1, 7))
        self.ui.pushButton18.clicked.connect(lambda: self.buttonEvent(1, 8))
        self.ui.pushButton20.clicked.connect(lambda: self.buttonEvent(2, 0))
        self.ui.pushButton21.clicked.connect(lambda: self.buttonEvent(2, 1))
        self.ui.pushButton22.clicked.connect(lambda: self.buttonEvent(2, 2))
        self.ui.pushButton23.clicked.connect(lambda: self.buttonEvent(2, 3))
        self.ui.pushButton24.clicked.connect(lambda: self.buttonEvent(2, 4))
        self.ui.pushButton25.clicked.connect(lambda: self.buttonEvent(2, 5))
        self.ui.pushButton26.clicked.connect(lambda: self.buttonEvent(2, 6))
        self.ui.pushButton27.clicked.connect(lambda: self.buttonEvent(2, 7))
        self.ui.pushButton28.clicked.connect(lambda: self.buttonEvent(2, 8))
        self.ui.pushButton30.clicked.connect(lambda: self.buttonEvent(3, 0))
        self.ui.pushButton31.clicked.connect(lambda: self.buttonEvent(3, 1))
        self.ui.pushButton32.clicked.connect(lambda: self.buttonEvent(3, 2))
        self.ui.pushButton33.clicked.connect(lambda: self.buttonEvent(3, 3))
        self.ui.pushButton34.clicked.connect(lambda: self.buttonEvent(3, 4))
        self.ui.pushButton35.clicked.connect(lambda: self.buttonEvent(3, 5))
        self.ui.pushButton36.clicked.connect(lambda: self.buttonEvent(3, 6))
        self.ui.pushButton37.clicked.connect(lambda: self.buttonEvent(3, 7))
        self.ui.pushButton38.clicked.connect(lambda: self.buttonEvent(3, 8))
        self.ui.pushButton40.clicked.connect(lambda: self.buttonEvent(4, 0))
        self.ui.pushButton41.clicked.connect(lambda: self.buttonEvent(4, 1))
        self.ui.pushButton42.clicked.connect(lambda: self.buttonEvent(4, 2))
        self.ui.pushButton43.clicked.connect(lambda: self.buttonEvent(4, 3))
        self.ui.pushButton44.clicked.connect(lambda: self.buttonEvent(4, 4))
        self.ui.pushButton45.clicked.connect(lambda: self.buttonEvent(4, 5))
        self.ui.pushButton46.clicked.connect(lambda: self.buttonEvent(4, 6))
        self.ui.pushButton47.clicked.connect(lambda: self.buttonEvent(4, 7))
        self.ui.pushButton48.clicked.connect(lambda: self.buttonEvent(4, 8))
        self.ui.pushButton50.clicked.connect(lambda: self.buttonEvent(5, 0))
        self.ui.pushButton51.clicked.connect(lambda: self.buttonEvent(5, 1))
        self.ui.pushButton52.clicked.connect(lambda: self.buttonEvent(5, 2))
        self.ui.pushButton53.clicked.connect(lambda: self.buttonEvent(5, 3))
        self.ui.pushButton54.clicked.connect(lambda: self.buttonEvent(5, 4))
        self.ui.pushButton55.clicked.connect(lambda: self.buttonEvent(5, 5))
        self.ui.pushButton56.clicked.connect(lambda: self.buttonEvent(5, 6))
        self.ui.pushButton57.clicked.connect(lambda: self.buttonEvent(5, 7))
        self.ui.pushButton58.clicked.connect(lambda: self.buttonEvent(5, 8))
        self.ui.pushButton60.clicked.connect(lambda: self.buttonEvent(6, 0))
        self.ui.pushButton61.clicked.connect(lambda: self.buttonEvent(6, 1))
        self.ui.pushButton62.clicked.connect(lambda: self.buttonEvent(6, 2))
        self.ui.pushButton63.clicked.connect(lambda: self.buttonEvent(6, 3))
        self.ui.pushButton64.clicked.connect(lambda: self.buttonEvent(6, 4))
        self.ui.pushButton65.clicked.connect(lambda: self.buttonEvent(6, 5))
        self.ui.pushButton66.clicked.connect(lambda: self.buttonEvent(6, 6))
        self.ui.pushButton67.clicked.connect(lambda: self.buttonEvent(6, 7))
        self.ui.pushButton68.clicked.connect(lambda: self.buttonEvent(6, 8))
        self.ui.pushButton70.clicked.connect(lambda: self.buttonEvent(7, 0))
        self.ui.pushButton71.clicked.connect(lambda: self.buttonEvent(7, 1))
        self.ui.pushButton72.clicked.connect(lambda: self.buttonEvent(7, 2))
        self.ui.pushButton73.clicked.connect(lambda: self.buttonEvent(7, 3))
        self.ui.pushButton74.clicked.connect(lambda: self.buttonEvent(7, 4))
        self.ui.pushButton75.clicked.connect(lambda: self.buttonEvent(7, 5))
        self.ui.pushButton76.clicked.connect(lambda: self.buttonEvent(7, 6))
        self.ui.pushButton77.clicked.connect(lambda: self.buttonEvent(7, 7))
        self.ui.pushButton78.clicked.connect(lambda: self.buttonEvent(7, 8))
        self.ui.pushButton80.clicked.connect(lambda: self.buttonEvent(8, 0))
        self.ui.pushButton81.clicked.connect(lambda: self.buttonEvent(8, 1))
        self.ui.pushButton82.clicked.connect(lambda: self.buttonEvent(8, 2))
        self.ui.pushButton83.clicked.connect(lambda: self.buttonEvent(8, 3))
        self.ui.pushButton84.clicked.connect(lambda: self.buttonEvent(8, 4))
        self.ui.pushButton85.clicked.connect(lambda: self.buttonEvent(8, 5))
        self.ui.pushButton86.clicked.connect(lambda: self.buttonEvent(8, 6))
        self.ui.pushButton87.clicked.connect(lambda: self.buttonEvent(8, 7))
        self.ui.pushButton88.clicked.connect(lambda: self.buttonEvent(8, 8))

        # Button color
        self.colorPosition = (-1, -1)

        # Go button
        self.ui.GoButton.clicked.connect(self.GoButtonEvent)

    def buttonEvent(self, i, j):
        if self.colorPosition != (-1, -1):
            self.removeButtonColor(self.colorPosition[0], self.colorPosition[1])

        if (i, j) == (0, 0):
            self.ui.pushButton00.setStyleSheet('background-color: rgb(220, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 1):
            self.ui.pushButton01.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 2):
            self.ui.pushButton02.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 3):
            self.ui.pushButton03.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 4):
            self.ui.pushButton04.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 5):
            self.ui.pushButton05.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 6):
            self.ui.pushButton06.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 7):
            self.ui.pushButton07.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (0, 8):
            self.ui.pushButton08.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 0):
            self.ui.pushButton10.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 1):
            self.ui.pushButton11.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 2):
            self.ui.pushButton12.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 3):
            self.ui.pushButton13.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 4):
            self.ui.pushButton14.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 5):
            self.ui.pushButton15.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 6):
            self.ui.pushButton16.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 7):
            self.ui.pushButton17.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (1, 8):
            self.ui.pushButton18.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 0):
            self.ui.pushButton20.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 1):
            self.ui.pushButton21.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 2):
            self.ui.pushButton22.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 3):
            self.ui.pushButton23.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 4):
            self.ui.pushButton24.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 5):
            self.ui.pushButton25.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 6):
            self.ui.pushButton26.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 7):
            self.ui.pushButton27.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (2, 8):
            self.ui.pushButton28.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 0):
            self.ui.pushButton30.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 1):
            self.ui.pushButton31.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 2):
            self.ui.pushButton32.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 3):
            self.ui.pushButton33.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 4):
            self.ui.pushButton34.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 5):
            self.ui.pushButton35.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 6):
            self.ui.pushButton36.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 7):
            self.ui.pushButton37.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (3, 8):
            self.ui.pushButton38.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 0):
            self.ui.pushButton40.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 1):
            self.ui.pushButton41.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 2):
            self.ui.pushButton42.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 3):
            self.ui.pushButton43.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 4):
            self.ui.pushButton44.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 5):
            self.ui.pushButton45.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 6):
            self.ui.pushButton46.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 7):
            self.ui.pushButton47.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (4, 8):
            self.ui.pushButton48.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 0):
            self.ui.pushButton50.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 1):
            self.ui.pushButton51.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 2):
            self.ui.pushButton52.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 3):
            self.ui.pushButton53.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 4):
            self.ui.pushButton54.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 5):
            self.ui.pushButton55.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 6):
            self.ui.pushButton56.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 7):
            self.ui.pushButton57.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (5, 8):
            self.ui.pushButton58.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 0):
            self.ui.pushButton60.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 1):
            self.ui.pushButton61.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 2):
            self.ui.pushButton62.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 3):
            self.ui.pushButton63.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 4):
            self.ui.pushButton64.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 5):
            self.ui.pushButton65.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 6):
            self.ui.pushButton66.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 7):
            self.ui.pushButton67.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (6, 8):
            self.ui.pushButton68.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 0):
            self.ui.pushButton70.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 1):
            self.ui.pushButton71.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 2):
            self.ui.pushButton72.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 3):
            self.ui.pushButton73.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 4):
            self.ui.pushButton74.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 5):
            self.ui.pushButton75.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 6):
            self.ui.pushButton76.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 7):
            self.ui.pushButton77.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (7, 8):
            self.ui.pushButton78.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 0):
            self.ui.pushButton80.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 1):
            self.ui.pushButton81.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 2):
            self.ui.pushButton82.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 3):
            self.ui.pushButton83.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 4):
            self.ui.pushButton84.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 5):
            self.ui.pushButton85.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 6):
            self.ui.pushButton86.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 7):
            self.ui.pushButton87.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)
        elif (i, j) == (8, 8):
            self.ui.pushButton88.setStyleSheet('background-color: rgb(200, 0, 0);')
            self.colorPosition = (i, j)

    def removeButtonColor(self, i, j):
        if i == 0 and j == 0: self.ui.pushButton00.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 1: self.ui.pushButton01.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 2: self.ui.pushButton02.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 3: self.ui.pushButton03.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 4: self.ui.pushButton04.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 5: self.ui.pushButton05.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 6: self.ui.pushButton06.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 7: self.ui.pushButton07.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 0 and j == 8: self.ui.pushButton08.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 0: self.ui.pushButton10.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 1: self.ui.pushButton11.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 2: self.ui.pushButton12.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 3: self.ui.pushButton13.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 4: self.ui.pushButton14.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 5: self.ui.pushButton15.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 6: self.ui.pushButton16.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 7: self.ui.pushButton17.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 1 and j == 8: self.ui.pushButton18.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 0: self.ui.pushButton20.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 1: self.ui.pushButton21.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 2: self.ui.pushButton22.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 3: self.ui.pushButton23.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 4: self.ui.pushButton24.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 5: self.ui.pushButton25.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 6: self.ui.pushButton26.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 7: self.ui.pushButton27.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 2 and j == 8: self.ui.pushButton28.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 0: self.ui.pushButton30.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 1: self.ui.pushButton31.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 2: self.ui.pushButton32.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 3: self.ui.pushButton33.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 4: self.ui.pushButton34.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 5: self.ui.pushButton35.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 6: self.ui.pushButton36.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 7: self.ui.pushButton37.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 3 and j == 8: self.ui.pushButton38.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 0: self.ui.pushButton40.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 1: self.ui.pushButton41.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 2: self.ui.pushButton42.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 3: self.ui.pushButton43.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 4: self.ui.pushButton44.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 5: self.ui.pushButton45.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 6: self.ui.pushButton46.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 7: self.ui.pushButton47.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 4 and j == 8: self.ui.pushButton48.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 0: self.ui.pushButton50.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 1: self.ui.pushButton51.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 2: self.ui.pushButton52.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 3: self.ui.pushButton53.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 4: self.ui.pushButton54.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 5: self.ui.pushButton55.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 6: self.ui.pushButton56.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 7: self.ui.pushButton57.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 5 and j == 8: self.ui.pushButton58.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 0: self.ui.pushButton60.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 1: self.ui.pushButton61.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 2: self.ui.pushButton62.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 3: self.ui.pushButton63.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 4: self.ui.pushButton64.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 5: self.ui.pushButton65.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 6: self.ui.pushButton66.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 7: self.ui.pushButton67.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 6 and j == 8: self.ui.pushButton68.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 0: self.ui.pushButton70.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 1: self.ui.pushButton71.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 2: self.ui.pushButton72.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 3: self.ui.pushButton73.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 4: self.ui.pushButton74.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 5: self.ui.pushButton75.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 6: self.ui.pushButton76.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 7: self.ui.pushButton77.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 7 and j == 8: self.ui.pushButton78.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 0: self.ui.pushButton80.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 1: self.ui.pushButton81.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 2: self.ui.pushButton82.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 3: self.ui.pushButton83.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 4: self.ui.pushButton84.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 5: self.ui.pushButton85.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 6: self.ui.pushButton86.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 7: self.ui.pushButton87.setStyleSheet('background-color: rgb(200, 200, 200);')
        elif i == 8 and j == 8: self.ui.pushButton88.setStyleSheet('background-color: rgb(200, 200, 200);')

    def keyPressEvent(self, event):
        if self.colorPosition != (None, None):
            if event.key() == Qt.Key_1:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 1)
            elif event.key() == Qt.Key_2:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 2)
            elif event.key() == Qt.Key_3:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 3)
            elif event.key() == Qt.Key_4:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 4)
            elif event.key() == Qt.Key_5:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 5)
            elif event.key() == Qt.Key_6:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 6)
            elif event.key() == Qt.Key_7:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 7)
            elif event.key() == Qt.Key_8:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 8)
            elif event.key() == Qt.Key_9:
                self.filledNumberInButton(self.colorPosition[0], self.colorPosition[1], 9)

    def filledNumberInButton(self, x, y, num):
        num = str(num)
        if x == 0 and y == 0:
            self.ui.pushButton00.setText(num)
        if x == 0 and y == 1:
            self.ui.pushButton01.setText(num)
        if x == 0 and y == 2:
            self.ui.pushButton02.setText(num)
        if x == 0 and y == 3:
            self.ui.pushButton03.setText(num)
        if x == 0 and y == 4:
            self.ui.pushButton04.setText(num)
        if x == 0 and y == 5:
            self.ui.pushButton05.setText(num)
        if x == 0 and y == 6:
            self.ui.pushButton06.setText(num)
        if x == 0 and y == 7:
            self.ui.pushButton07.setText(num)
        if x == 0 and y == 8:
            self.ui.pushButton08.setText(num)
        if x == 1 and y == 0:
            self.ui.pushButton10.setText(num)
        if x == 1 and y == 1:
            self.ui.pushButton11.setText(num)
        if x == 1 and y == 2:
            self.ui.pushButton12.setText(num)
        if x == 1 and y == 3:
            self.ui.pushButton13.setText(num)
        if x == 1 and y == 4:
            self.ui.pushButton14.setText(num)
        if x == 1 and y == 5:
            self.ui.pushButton15.setText(num)
        if x == 1 and y == 6:
            self.ui.pushButton16.setText(num)
        if x == 1 and y == 7:
            self.ui.pushButton17.setText(num)
        if x == 1 and y == 8:
            self.ui.pushButton18.setText(num)
        if x == 2 and y == 0:
            self.ui.pushButton20.setText(num)
        if x == 2 and y == 1:
            self.ui.pushButton21.setText(num)
        if x == 2 and y == 2:
            self.ui.pushButton22.setText(num)
        if x == 2 and y == 3:
            self.ui.pushButton23.setText(num)
        if x == 2 and y == 4:
            self.ui.pushButton24.setText(num)
        if x == 2 and y == 5:
            self.ui.pushButton25.setText(num)
        if x == 2 and y == 6:
            self.ui.pushButton26.setText(num)
        if x == 2 and y == 7:
            self.ui.pushButton27.setText(num)
        if x == 2 and y == 8:
            self.ui.pushButton28.setText(num)
        if x == 3 and y == 0:
            self.ui.pushButton30.setText(num)
        if x == 3 and y == 1:
            self.ui.pushButton31.setText(num)
        if x == 3 and y == 2:
            self.ui.pushButton32.setText(num)
        if x == 3 and y == 3:
            self.ui.pushButton33.setText(num)
        if x == 3 and y == 4:
            self.ui.pushButton34.setText(num)
        if x == 3 and y == 5:
            self.ui.pushButton35.setText(num)
        if x == 3 and y == 6:
            self.ui.pushButton36.setText(num)
        if x == 3 and y == 7:
            self.ui.pushButton37.setText(num)
        if x == 3 and y == 8:
            self.ui.pushButton38.setText(num)
        if x == 4 and y == 0:
            self.ui.pushButton40.setText(num)
        if x == 4 and y == 1:
            self.ui.pushButton41.setText(num)
        if x == 4 and y == 2:
            self.ui.pushButton42.setText(num)
        if x == 4 and y == 3:
            self.ui.pushButton43.setText(num)
        if x == 4 and y == 4:
            self.ui.pushButton44.setText(num)
        if x == 4 and y == 5:
            self.ui.pushButton45.setText(num)
        if x == 4 and y == 6:
            self.ui.pushButton46.setText(num)
        if x == 4 and y == 7:
            self.ui.pushButton47.setText(num)
        if x == 4 and y == 8:
            self.ui.pushButton48.setText(num)
        if x == 5 and y == 0:
            self.ui.pushButton50.setText(num)
        if x == 5 and y == 1:
            self.ui.pushButton51.setText(num)
        if x == 5 and y == 2:
            self.ui.pushButton52.setText(num)
        if x == 5 and y == 3:
            self.ui.pushButton53.setText(num)
        if x == 5 and y == 4:
            self.ui.pushButton54.setText(num)
        if x == 5 and y == 5:
            self.ui.pushButton55.setText(num)
        if x == 5 and y == 6:
            self.ui.pushButton56.setText(num)
        if x == 5 and y == 7:
            self.ui.pushButton57.setText(num)
        if x == 5 and y == 8:
            self.ui.pushButton58.setText(num)
        if x == 6 and y == 0:
            self.ui.pushButton60.setText(num)
        if x == 6 and y == 1:
            self.ui.pushButton61.setText(num)
        if x == 6 and y == 2:
            self.ui.pushButton62.setText(num)
        if x == 6 and y == 3:
            self.ui.pushButton63.setText(num)
        if x == 6 and y == 4:
            self.ui.pushButton64.setText(num)
        if x == 6 and y == 5:
            self.ui.pushButton65.setText(num)
        if x == 6 and y == 6:
            self.ui.pushButton66.setText(num)
        if x == 6 and y == 7:
            self.ui.pushButton67.setText(num)
        if x == 6 and y == 8:
            self.ui.pushButton68.setText(num)
        if x == 7 and y == 0:
            self.ui.pushButton70.setText(num)
        if x == 7 and y == 1:
            self.ui.pushButton71.setText(num)
        if x == 7 and y == 2:
            self.ui.pushButton72.setText(num)
        if x == 7 and y == 3:
            self.ui.pushButton73.setText(num)
        if x == 7 and y == 4:
            self.ui.pushButton74.setText(num)
        if x == 7 and y == 5:
            self.ui.pushButton75.setText(num)
        if x == 7 and y == 6:
            self.ui.pushButton76.setText(num)
        if x == 7 and y == 7:
            self.ui.pushButton77.setText(num)
        if x == 7 and y == 8:
            self.ui.pushButton78.setText(num)
        if x == 8 and y == 0:
            self.ui.pushButton80.setText(num)
        if x == 8 and y == 1:
            self.ui.pushButton81.setText(num)
        if x == 8 and y == 2:
            self.ui.pushButton82.setText(num)
        if x == 8 and y == 3:
            self.ui.pushButton83.setText(num)
        if x == 8 and y == 4:
            self.ui.pushButton84.setText(num)
        if x == 8 and y == 5:
            self.ui.pushButton85.setText(num)
        if x == 8 and y == 6:
            self.ui.pushButton86.setText(num)
        if x == 8 and y == 7:
            self.ui.pushButton87.setText(num)
        if x == 8 and y == 8:
            self.ui.pushButton88.setText(num)

        self.removeButtonColor(x, y)

    def GoButtonEvent(self):
        question = [[0 for a in range(9)] for b in range(9)]
        if self.ui.pushButton00: question[0][0] = int(self.ui.pushButton00.text())
        if self.ui.pushButton01: question[0][1] = int(self.ui.pushButton01.text())
        if self.ui.pushButton02: question[0][2] = int(self.ui.pushButton02.text())
        if self.ui.pushButton03: question[0][3] = int(self.ui.pushButton03.text())
        if self.ui.pushButton04: question[0][4] = int(self.ui.pushButton04.text())
        if self.ui.pushButton05: question[0][5] = int(self.ui.pushButton05.text())
        if self.ui.pushButton06: question[0][6] = int(self.ui.pushButton06.text())
        if self.ui.pushButton07: question[0][7] = int(self.ui.pushButton07.text())
        if self.ui.pushButton08: question[0][8] = int(self.ui.pushButton08.text())
        if self.ui.pushButton10: question[1][0] = int(self.ui.pushButton10.text())
        if self.ui.pushButton11: question[1][1] = int(self.ui.pushButton11.text())
        if self.ui.pushButton12: question[1][2] = int(self.ui.pushButton12.text())
        if self.ui.pushButton13: question[1][3] = int(self.ui.pushButton13.text())
        if self.ui.pushButton14: question[1][4] = int(self.ui.pushButton14.text())
        if self.ui.pushButton15: question[1][5] = int(self.ui.pushButton15.text())
        if self.ui.pushButton16: question[1][6] = int(self.ui.pushButton16.text())
        if self.ui.pushButton17: question[1][7] = int(self.ui.pushButton17.text())
        if self.ui.pushButton18: question[1][8] = int(self.ui.pushButton18.text())
        if self.ui.pushButton20: question[2][0] = int(self.ui.pushButton20.text())
        if self.ui.pushButton21: question[2][1] = int(self.ui.pushButton21.text())
        if self.ui.pushButton22: question[2][2] = int(self.ui.pushButton22.text())
        if self.ui.pushButton23: question[2][3] = int(self.ui.pushButton23.text())
        if self.ui.pushButton24: question[2][4] = int(self.ui.pushButton24.text())
        if self.ui.pushButton25: question[2][5] = int(self.ui.pushButton25.text())
        if self.ui.pushButton26: question[2][6] = int(self.ui.pushButton26.text())
        if self.ui.pushButton27: question[2][7] = int(self.ui.pushButton27.text())
        if self.ui.pushButton28: question[2][8] = int(self.ui.pushButton28.text())
        if self.ui.pushButton30: question[3][0] = int(self.ui.pushButton30.text())
        if self.ui.pushButton31: question[3][1] = int(self.ui.pushButton31.text())
        if self.ui.pushButton32: question[3][2] = int(self.ui.pushButton32.text())
        if self.ui.pushButton33: question[3][3] = int(self.ui.pushButton33.text())
        if self.ui.pushButton34: question[3][4] = int(self.ui.pushButton34.text())
        if self.ui.pushButton35: question[3][5] = int(self.ui.pushButton35.text())
        if self.ui.pushButton36: question[3][6] = int(self.ui.pushButton36.text())
        if self.ui.pushButton37: question[3][7] = int(self.ui.pushButton37.text())
        if self.ui.pushButton38: question[3][8] = int(self.ui.pushButton38.text())
        if self.ui.pushButton40: question[4][0] = int(self.ui.pushButton40.text())
        if self.ui.pushButton41: question[4][1] = int(self.ui.pushButton41.text())
        if self.ui.pushButton42: question[4][2] = int(self.ui.pushButton42.text())
        if self.ui.pushButton43: question[4][3] = int(self.ui.pushButton43.text())
        if self.ui.pushButton44: question[4][4] = int(self.ui.pushButton44.text())
        if self.ui.pushButton45: question[4][5] = int(self.ui.pushButton45.text())
        if self.ui.pushButton46: question[4][6] = int(self.ui.pushButton46.text())
        if self.ui.pushButton47: question[4][7] = int(self.ui.pushButton47.text())
        if self.ui.pushButton48: question[4][8] = int(self.ui.pushButton48.text())
        if self.ui.pushButton50: question[5][0] = int(self.ui.pushButton50.text())
        if self.ui.pushButton51: question[5][1] = int(self.ui.pushButton51.text())
        if self.ui.pushButton52: question[5][2] = int(self.ui.pushButton52.text())
        if self.ui.pushButton53: question[5][3] = int(self.ui.pushButton53.text())
        if self.ui.pushButton54: question[5][4] = int(self.ui.pushButton54.text())
        if self.ui.pushButton55: question[5][5] = int(self.ui.pushButton55.text())
        if self.ui.pushButton56: question[5][6] = int(self.ui.pushButton56.text())
        if self.ui.pushButton57: question[5][7] = int(self.ui.pushButton57.text())
        if self.ui.pushButton58: question[5][8] = int(self.ui.pushButton58.text())
        if self.ui.pushButton60: question[6][0] = int(self.ui.pushButton60.text())
        if self.ui.pushButton61: question[6][1] = int(self.ui.pushButton61.text())
        if self.ui.pushButton62: question[6][2] = int(self.ui.pushButton62.text())
        if self.ui.pushButton63: question[6][3] = int(self.ui.pushButton63.text())
        if self.ui.pushButton64: question[6][4] = int(self.ui.pushButton64.text())
        if self.ui.pushButton65: question[6][5] = int(self.ui.pushButton65.text())
        if self.ui.pushButton66: question[6][6] = int(self.ui.pushButton66.text())
        if self.ui.pushButton67: question[6][7] = int(self.ui.pushButton67.text())
        if self.ui.pushButton68: question[6][8] = int(self.ui.pushButton68.text())
        if self.ui.pushButton70: question[7][0] = int(self.ui.pushButton70.text())
        if self.ui.pushButton71: question[7][1] = int(self.ui.pushButton71.text())
        if self.ui.pushButton72: question[7][2] = int(self.ui.pushButton72.text())
        if self.ui.pushButton73: question[7][3] = int(self.ui.pushButton73.text())
        if self.ui.pushButton74: question[7][4] = int(self.ui.pushButton74.text())
        if self.ui.pushButton75: question[7][5] = int(self.ui.pushButton75.text())
        if self.ui.pushButton76: question[7][6] = int(self.ui.pushButton76.text())
        if self.ui.pushButton77: question[7][7] = int(self.ui.pushButton77.text())
        if self.ui.pushButton78: question[7][8] = int(self.ui.pushButton78.text())
        if self.ui.pushButton80: question[8][0] = int(self.ui.pushButton80.text())
        if self.ui.pushButton81: question[8][1] = int(self.ui.pushButton81.text())
        if self.ui.pushButton82: question[8][2] = int(self.ui.pushButton82.text())
        if self.ui.pushButton83: question[8][3] = int(self.ui.pushButton83.text())
        if self.ui.pushButton84: question[8][4] = int(self.ui.pushButton84.text())
        if self.ui.pushButton85: question[8][5] = int(self.ui.pushButton85.text())
        if self.ui.pushButton86: question[8][6] = int(self.ui.pushButton86.text())
        if self.ui.pushButton87: question[8][7] = int(self.ui.pushButton87.text())
        if self.ui.pushButton88: question[8][8] = int(self.ui.pushButton88.text())

        sudoku = Sudoku(question)
        sudoku.run()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
