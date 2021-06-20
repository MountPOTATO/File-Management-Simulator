import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QMainWindow, QMessageBox, QInputDialog, QLineEdit, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui, QtCore

class QSS_READER:
    def __init__(self):
        pass

    def read(style):
        """[读入qss文件并以str形式存储]
        Args:
            style ([str]): [qss文件的相对路径地址]
        Returns:
            [str]: [qss文件的str形式，以在setStyleSheet中调用]
        """        
        with open(style,'r') as f:
            return f.read()


