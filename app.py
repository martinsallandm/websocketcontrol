from PyQt6 import QtWidgets, QtGui
import sys  # We need sys so that we can pass argv to QApplication
import os

from main_window import Ui_MainWindow

from dynamic_plotter import DynamicPlotter
from queue import Queue


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, queue, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.dynamic_plotter = DynamicPlotter(self.centralWidget, queue, 0.01)

        self.graphWidget = self.dynamic_plotter.get_plot_widget()
        self.graphWidget.setObjectName("graphWidget")
        self.graphWidgetLayout.addWidget(self.graphWidget)

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
        if wave_form == "random":
            self.labelMaxAmplitude.setText("Max Amplitude")
            self.doubleBoxMinAmplitude.setEnabled(True)
        else:
            self.labelMaxAmplitude.setText("Amplitude")
            self.doubleBoxMinAmplitude.setEnabled(False)
        self.dynamic_plotter.set_plot_func(wave_form)

    def change_max_amplitude(self, value):
        self.dynamic_plotter.set_maxAmplitude(value)

    def change_min_amplitude(self, value):
        self.dynamic_plotter.set_minAmplitude(value)

    def change_period(self, value):
        self.dynamic_plotter.set_period(value)

    def change_offset(self, value):
        self.dynamic_plotter.set_offset(value)

    def closeEvent(self, event):
        os._exit(1)
