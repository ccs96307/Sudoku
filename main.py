# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from UI import Ui_MainWindow
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Widget
        # palette = QtGui.QPalette()
        # palette.setColor(self.ui.textBrowser.backgroundRole(), QColor(0, 0, 0))
        # self.ui.textBrowser.setPalette(palette)
        # self.ui.widget.setStyleSheet("background-color: Black;")

        # self.ui.openGLWidget.resize


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())