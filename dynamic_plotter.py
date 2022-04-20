from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
from scipy import signal

import collections
import time
import numpy as np

# Original script at
# https://github.com/ap--/python-live-plotting/blob/master/plot_pyqtgraph.py


class DynamicPlotter:
    def __init__(
            self, widget, queue_out, queue_in, queue_ref, sampleinterval=0.05,
            timewindow=10.0, size=(600, 350)):
        # Data stuff
        self._interval = int(sampleinterval * 1000)
        self._bufsize = int(timewindow / sampleinterval)
        self.databuffer_r = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.databuffer_g = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.databuffer_b = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.databuffer_p = collections.deque(
            [0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(0.0, timewindow, self._bufsize)
        self.y_r = np.zeros(self._bufsize, dtype=np.float)
        self.y_g = np.zeros(self._bufsize, dtype=np.float)
        self.y_b = np.zeros(self._bufsize, dtype=np.float)
        self.y_p = np.zeros(self._bufsize, dtype=np.float)
        self.plt = pg.PlotWidget(widget)
        self.plt.setYRange(-100.0, 100.0)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel("left", "amplitude", "V")
        self.plt.setLabel("bottom", "time", "s")
        self.curve_r = self.plt.plot(self.x, self.y_r, pen="r")
        self.curve_g = self.plt.plot(self.x, self.y_g, pen="g")
        self.curve_b = self.plt.plot(self.x, self.y_b, pen="b")
        self.curve_p = self.plt.plot(self.x, self.y_b, pen="c")

        self.plot_func = "step"
        self.maxAmplitude = 0.0
        self.minAmplitude = 0.0
        self.maxPeriod = 2*np.pi
        self.minPeriod = 0.1
        self.offset = 0.0
        self.queue_out = queue_out
        self.queue_in = queue_in
        self.queue_ref = queue_ref
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

    def set_maxPeriod(self, value):
        self.maxPeriod = value

    def set_minPeriod(self, value):
        self.minPeriod = value

    def set_offset(self, value):
        self.offset = value

    def get_plot_widget(self):
        return self.plt

    def get_data(self):
        data = getattr(self, self.plot_func)(time.time(), self.queue_out)
        self.queue_in.put(data[0])
        ref = self.queue_ref.get()
        return data, ref

    def updateplot(self):
        data, ref = self.get_data()

        self.databuffer_b.append(data[0])
        self.databuffer_r.append(data[-1])
        self.databuffer_g.append(data[-2])
        self.databuffer_p.append(ref[1])

        self.y_b[:] = self.databuffer_b
        self.y_r[:] = self.databuffer_r
        self.y_g[:] = self.databuffer_g
        self.y_p[:] = self.databuffer_p

        self.curve_b.setData(self.x, self.y_b)
        self.curve_r.setData(self.x, self.y_r)
        self.curve_g.setData(self.x, self.y_g)
        self.curve_p.setData(self.x, self.y_p)

    def simulator(self, queue_out):
        if not queue_out.empty():
            self.last_value = queue_out.get()
        return self.last_value

    def step(self, t, queue_out):
        return [self.maxAmplitude] + self.simulator(queue_out)

    def sine(self, t, queue_out):
        return [self.maxAmplitude * np.sin(
                (2*np.pi/self.maxPeriod)*t
                ) + self.offset*np.ones_like(t)] + self.simulator(queue_out)

    def square(self, t, queue_out):
        return [self.maxAmplitude * signal.square(
                (2*np.pi/self.maxPeriod)*t
                ) + self.offset] + self.simulator(queue_out)

    def sawtooth(self, t, queue_out):
        return [self.maxAmplitude * signal.sawtooth(
                (2*np.pi/self.maxPeriod)*t
                ) + self.offset] + self.simulator(queue_out)

    def random(self, t, queue_out):
        return [self.maxAmplitude] + self.simulator(queue_out)
