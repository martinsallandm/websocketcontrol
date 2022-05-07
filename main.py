#!/usr/bin/env python

import ctypes
import sys  # We need sys so that we can pass argv to QApplication
from PyQt6 import QtWidgets, QtGui
import app

if __name__ == "__main__":
    myappid = "ecom102-idynamic-controler-0.0.1"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    gui = QtWidgets.QApplication(sys.argv)

    window = app.MainWindow()
    window.setWindowIcon(QtGui.QIcon("qtui/feedback.png"))
    window.show()
    gui.exec()
