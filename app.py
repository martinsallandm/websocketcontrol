import os

from PyQt6 import QtWidgets
from main_window import Ui_MainWindow
from dynamic_plotter import DynamicPlotter


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(
            self, queue_out, queue_in, queue_ref, queue_ref_in, loop, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.dynamic_plotter = DynamicPlotter(
            self.centralWidget, queue_out, queue_in,
            queue_ref, queue_ref_in, loop, 0.01, timewindow=10)

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
        self.doubleBoxMaxPeriod.valueChanged.connect(
            self.change_max_period
        )
        self.doubleBoxMinPeriod.valueChanged.connect(
            self.change_min_period
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
            self.labelMaxPeriod.setText("Max Period")
            self.doubleBoxMinPeriod.setEnabled(True)
        else:
            self.labelMaxAmplitude.setText("Amplitude")
            self.doubleBoxMinAmplitude.setEnabled(False)
            self.labelMaxPeriod.setText("Period")
            self.doubleBoxMinPeriod.setEnabled(False)
        self.dynamic_plotter.set_plot_func(wave_form)

    def change_max_amplitude(self, value):
        self.dynamic_plotter.set_maxAmplitude(value)

    def change_min_amplitude(self, value):
        self.dynamic_plotter.set_minAmplitude(value)

    def change_max_period(self, value):
        self.dynamic_plotter.set_maxPeriod(value)

    def change_min_period(self, value):
        self.dynamic_plotter.set_minPeriod(value)

    def change_offset(self, value):
        self.dynamic_plotter.set_offset(value)

    def closeEvent(self, event):
        os._exit(1)
