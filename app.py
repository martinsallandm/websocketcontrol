from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np
from scipy import signal

from main_window import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.graphWidget = pg.PlotWidget(self.centralWidget)
        self.graphWidget.setObjectName("graphWidget")
        self.graphWidgetLayout.addWidget(self.graphWidget)

        self.plot_func = self.sin

        self.n_points = 100
        self.x = np.linspace(0, 5.0, self.n_points)
        self.y = self.plot_func()

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000//60)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):

        self.x = np.roll(self.x, -1)  # Remove the first y element.
        self.x[-1] = (self.x[-2] - self.x[-3]) + self.x[-2]
        self.y = self.plot_func()
        self.data_line.setData(self.x, self.y)  # Update the data.

    def step(self, amp=1.0):
        return amp * np.ones_like(self.x)

    def sin(self, amp=1.0, per=2*np.pi, offset=0.0):
        return amp*np.sin((2*np.pi/per)*self.x) + offset*np.ones_like(self.x)

    def pulse(self, amp=1.0, per=2*np.pi, offset=0.0):
        off = offset*np.ones_like(self.x)
        return signal.square((2*np.pi/per)*self.x) + off

    def sawtooth(self, amp=1.0, per=2*np.pi, offset=0.0):
        off = offset*np.ones_like(self.x)
        return signal.sawtooth((2*np.pi/per)*self.x) + off


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
