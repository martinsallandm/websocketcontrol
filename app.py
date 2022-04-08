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

        self.maxAmplitude = 0.0
        self.minAmplitude = 0.0
        self.period = 2*np.pi
        self.offset = 0.0

        self.plot_func = self.step

        self.n_points = 100
        self.x = np.linspace(0, 5.0, self.n_points)
        self.y = self.plot_func(self.maxAmplitude, self.period, self.offset)

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen, )
        self.graphWidget.setLimits(yMin=-1.0, yMax=1.0)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000//24)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        self.comboBoxLoop.currentIndexChanged.connect(
            self.change_loop
        )

        self.comboBoxWaveForm.currentIndexChanged.connect(
            self.change_wave_form
        )

        self.doubleBoxMaxAmplitude.valueChanged.connect(
            self.change_max_amplitude
        )
        self.doubleBoxMinAmplitude.valueChanged.connect(
            self.change_min_amplitude
        )
        self.doubleBoxPeriod.valueChanged.connect(
            self.change_period
        )
        self.doubleBoxOffset.valueChanged.connect(
            self.change_offset
        )

    def change_loop(self, i):
        if self.comboBoxLoop.itemText(i) == "Closed":
            self.doubleBoxSetPoint.setEnabled(True)
        else:
            self.doubleBoxSetPoint.setEnabled(False)

    def change_wave_form(self, i):
        wave_form = self.comboBoxWaveForm.itemText(i)
        self.plot_func = getattr(self, wave_form)
        if wave_form == "random":
            self.labelMaxAmplitude.setText("Max Amplitude")
            self.doubleBoxMinAmplitude.setEnabled(True)
        else:
            self.labelMaxAmplitude.setText("Amplitude")
            self.doubleBoxMinAmplitude.setEnabled(False)

    def change_max_amplitude(self, value):
        self.maxAmplitude = value

    def change_min_amplitude(self, value):
        self.mminAmplitude = value

    def change_period(self, value):
        self.period = value

    def change_offset(self, value):
        self.offset = value

    def update_plot_data(self):

        self.x = np.roll(self.x, -1)  # Remove the first y element.
        self.x[-1] = (self.x[-2] - self.x[-3]) + self.x[-2]
        self.y = self.plot_func(self.maxAmplitude, self.period, self.offset)
        self.data_line.setData(self.x, self.y)  # Update the data.

    def step(self, amp=0.0, per=None, offset=None, min_amp=None):
        return amp * np.ones_like(self.x) + self.offset * np.ones_like(self.x)

    def sine(self, amp=0.0, per=2*np.pi, offset=0.0, min_amp=None):
        return amp*np.sin((2*np.pi/per)*self.x) + offset*np.ones_like(self.x)

    def square(self, amp=0.0, per=2*np.pi, offset=0.0, min_amp=None):
        off = offset*np.ones_like(self.x)
        return amp*signal.square((2*np.pi/per)*self.x) + off

    def sawtooth(self, amp=0.0, per=2*np.pi, offset=0.0, min_amp=None):
        off = offset*np.ones_like(self.x)
        return amp*signal.sawtooth((2*np.pi/per)*self.x) + off

    def random(self, amp=0.0, per=2*np.pi, offset=0.0, min_amp=None):
        return amp * np.ones_like(self.x)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
