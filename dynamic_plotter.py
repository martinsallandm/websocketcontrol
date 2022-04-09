from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
from scipy import signal
from queue import Queue

import collections
import time
import numpy as np

# Original script at
# https://github.com/ap--/python-live-plotting/blob/master/plot_pyqtgraph.py


class DynamicPlotter:
    def __init__(
            self, widget, queue, sampleinterval=0.1, timewindow=10.0,
            size=(600, 350)):
        # Data stuff
        self._interval = int(sampleinterval * 1000)
        self._bufsize = int(timewindow / sampleinterval)
        self.databuffer = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(0.0, timewindow, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        self.plt = pg.PlotWidget(widget)
        self.plt.setYRange(-1.0, 1.0)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel("left", "amplitude", "V")
        self.plt.setLabel("bottom", "time", "s")
        self.curve = self.plt.plot(self.x, self.y, pen=(255, 0, 0))

        self.plot_func = "step"
        self.maxAmplitude = 0.0
        self.minAmplitude = 0.0
        self.period = 2*np.pi
        self.offset = 0.0
        self.queue = queue
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def set_plot_func(self, value):
        self.plot_func = value

    def set_maxAmplitude(self, value):
        self.maxAmplitude = value

    def set_minAmplitude(self, value):
        self.minAmplitude = value

    def set_period(self, value):
        self.period = value

    def set_offset(self, value):
        self.offset = value

    def get_plot_widget(self):
        return self.plt

    def get_data(self):
        return getattr(self, self.plot_func)(time.time(), self.queue)

    def updateplot(self):
        self.databuffer.append(self.get_data())
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)

    def step(self, t, queue):
        return self.maxAmplitude

    def sine(self, t, queue):
        return self.maxAmplitude * np.sin(
            (2*np.pi/self.period)*t
        ) + self.offset*np.ones_like(t)

    def square(self, t, queue):
        return self.maxAmplitude * signal.square(
            (2*np.pi/self.period)*t
        ) + self.offset

    def sawtooth(self, t, queue):
        return self.maxAmplitude * signal.sawtooth(
            (2*np.pi/self.period)*t
        ) + self.offset

    def random(self, t, queue):
        return self.maxAmplitude

    def input(self, t, queue):
        if not queue.empty():
            return queue.get()
        return 0
