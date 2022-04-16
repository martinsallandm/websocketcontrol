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
            self, widget, queue, sampleinterval=0.05, timewindow=10.0,
            size=(600, 350)):
        # Data stuff
        self._interval = int(sampleinterval * 1000)
        self._bufsize = int(timewindow / sampleinterval)
        self.databuffer_r = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.databuffer_g = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.databuffer_b = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(0.0, timewindow, self._bufsize)
        self.y_r = np.zeros(self._bufsize, dtype=np.float)
        self.y_g = np.zeros(self._bufsize, dtype=np.float)
        self.y_b = np.zeros(self._bufsize, dtype=np.float)
        self.plt = pg.PlotWidget(widget)
        self.plt.setYRange(-100.0, 100.0)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel("left", "amplitude", "V")
        self.plt.setLabel("bottom", "time", "s")
        self.curve_r = self.plt.plot(self.x, self.y_r, pen="r")
        self.curve_g = self.plt.plot(self.x, self.y_g, pen="g")
        self.curve_b = self.plt.plot(self.x, self.y_b, pen="b")

        self.plot_func = "step"
        self.maxAmplitude = 0.0
        self.minAmplitude = 0.0
        self.period = 2*np.pi
        self.offset = 0.0
        self.queue = queue
        self.last_value = [0.0, 0.0, 0.0]
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
        data = self.get_data()

        self.databuffer_b.append(data[0])
        self.databuffer_r.append(data[-1])
        self.databuffer_g.append(data[-2])

        self.y_b[:] = self.databuffer_b
        self.y_r[:] = self.databuffer_r
        self.y_g[:] = self.databuffer_g

        self.curve_b.setData(self.x, self.y_b)
        self.curve_r.setData(self.x, self.y_r)
        self.curve_g.setData(self.x, self.y_g)

    def step(self, t, queue):
        return [self.maxAmplitude, 0, 0]

    def sine(self, t, queue):
        return [self.maxAmplitude * np.sin(
            (2*np.pi/self.period)*t
        ) + self.offset*np.ones_like(t), 0, 0]

    def square(self, t, queue):
        return [self.maxAmplitude * signal.square(
            (2*np.pi/self.period)*t
        ) + self.offset, 0, 0]

    def sawtooth(self, t, queue):
        return [self.maxAmplitude * signal.sawtooth(
            (2*np.pi/self.period)*t
        ) + self.offset, 0, 0]

    def random(self, t, queue):
        return [self.maxAmplitude, 0, 0]

    def input(self, t, queue):
        if not queue.empty():
            self.last_value = queue.get()
        return self.last_value
