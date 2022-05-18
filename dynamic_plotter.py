import pyqtgraph as pg
from scipy import signal

import collections
import numpy as np


class DynamicPlotter:
    def __init__(
            self, widget, sampleinterval=0.01,
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
        self.ref_plot_func = "step"
        self.maxAmplitude = 10.0
        self.minAmplitude = 0.0
        self.maxPeriod = 2*np.pi
        self.minPeriod = 0.1
        self.offset = 0.0
        self.last_value = [0.0, 0.0, 0.0]
        self.count = 0
        self.loop = 0.0
        self.start = 0.0
        self.rand = 0.0

    def set_plot_func(self, value):
        self.plot_func = value

    def set_ref_plot_func(self, value):
        self.ref_plot_func = value

    def set_maxAmplitude(self, value):
        self.maxAmplitude = value

    def set_minAmplitude(self, value):
        self.minAmplitude = value

    def set_maxPeriod(self, value):
        self.maxPeriod = value
        self.rand_data = np.random.uniform(
            self.minPeriod, self.maxPeriod, (1, 10000))

    def set_minPeriod(self, value):
        self.minPeriod = value
        self.rand_data = np.random.uniform(
            self.minPeriod, self.maxPeriod, (1, 10000))

    def set_offset(self, value):
        self.offset = value

    def get_plot_widget(self):
        return self.plt

    def get_input(self, t):
        return getattr(self, self.plot_func)(t)

    def get_ref(self, t):
        return getattr(self, self.ref_plot_func)(t)

    def update_plot(self, refs, outs, t):
        input = self.get_input(t)
        ref = self.get_ref(t)
        refs = [float(r) for r in refs]
        outs = [float(o) for o in outs]
        if self.loop == 1.0:
            input = refs[0]-outs[1]
        else:
            input = input[0]
        self.databuffer_b.append(input)
        self.databuffer_r.append(outs[0])
        self.databuffer_g.append(outs[1])
        self.databuffer_p.append(refs[0])

        self.y_b[:] = self.databuffer_b
        self.y_r[:] = self.databuffer_r
        self.y_g[:] = self.databuffer_g
        self.y_p[:] = self.databuffer_p

        self.curve_b.setData(self.x, self.y_b)
        self.curve_r.setData(self.x, self.y_r)
        self.curve_g.setData(self.x, self.y_g)
        self.curve_p.setData(self.x, self.y_p)

        return input, ref

    def step(self, t):
        return [self.maxAmplitude]

    def sine(self, t):
        return [self.maxAmplitude * np.sin(
            (2*np.pi/self.maxPeriod)*t
        ) + self.offset*np.ones_like(t)]

    def square(self, t):
        return [self.maxAmplitude * signal.square(
            (2*np.pi/self.maxPeriod)*t
        ) + self.offset]

    def sawtooth(self, t):
        return [self.maxAmplitude * signal.sawtooth(
            (2*np.pi/self.maxPeriod)*t
        ) + self.offset]

    def random(self, t):
        if t-self.start >= self.maxPeriod:
            self.rand = np.random.uniform(self.minAmplitude, self.maxAmplitude)
            self.start = t
        elif t-self.start >= self.minPeriod:
            if np.random.randint(0, 1) == 1:
                self.rand = np.random.uniform(
                    self.minAmplitude,
                    self.maxAmplitude)
                self.start = t
        return[self.rand]
