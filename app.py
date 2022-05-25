import os
import math

import numpy as np
from PyQt6 import QtWidgets
from main_window import Ui_MainWindow
from dynamic_plotter import DynamicPlotter


from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool
import asyncio
import websockets
import time

from websockets.exceptions import ConnectionClosedError

from PIDController import PIDController, PI_DController, I_PDController


class ThreadedServer(QRunnable):

    def __init__(self, sampling_time, plotter):
        super().__init__()
        self.sampling_time = sampling_time
        self.plotter = plotter
        self.controller = None

        self.output_index = 0

    def set_output_index(self, i):
        self.output_index = i

    def set_controller(self, controller, app):
        self.controller = controller
        self.lcdNumberIAE = app.lcdNumberIAE
        self.lcdNumberISE = app.lcdNumberISE
        self.lcdNumberITAE = app.lcdNumberITAE
        self.lcdNumberGoodHeart = app.lcdNumberGoodHeart

    async def server_loop(self, websocket):
        while True:
            try:
                startTime = time.time()

                await asyncio.sleep(self.sampling_time)

                if self.controller is not None:
                    self.controller.time += self.controller.T

                await websocket.send("get references")
                received = await websocket.recv()
                n_refs, refs = self.parse_message(received)

                ref = float(refs[0])

                if math.isnan(ref):
                    ref = 0.0

                await websocket.send("get outputs")
                received = await websocket.recv()
                n_outs, outs = self.parse_message(received)
                input, refs = self.plotter.update_plot(refs, outs, time.time())

                out = float(outs[self.output_index])

                if self.controller is not None:
                    self.controller.reference(ref)
                    self.controller.measured(out)
                    u = self.controller.control()
                    self.controller.apply(u)
                    await websocket.send("set input|" + f"{u}")
                    metrics = self.controller.error_metrics()
                    self.lcdNumberIAE.display(metrics["IAE"])
                    self.lcdNumberISE.display(metrics["ISE"])
                    self.lcdNumberITAE.display(metrics["ITAE"])
                    self.lcdNumberGoodHeart.display(metrics["GoodHeart"])
                else:
                    if input is not None:
                        await websocket.send("set input|" + str(input))

                if refs is not None:
                    await websocket.send("set references|" + str(refs[0]))

                ellapsedTime = 0.0
                while ellapsedTime < self.sampling_time:
                    time.sleep(0.0001)
                    endTime = time.time()
                    ellapsedTime = endTime - startTime
            except ConnectionClosedError:
                print("iDynamic connection was closed!")
                break

    @staticmethod
    def parse_message(msg):
        msg = msg.split(",")
        return msg[0], msg[1:]

    @pyqtSlot()
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server = websockets.serve(self.server_loop, "localhost", 6660)
        asyncio.ensure_future(server)
        asyncio.get_event_loop().run_forever()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    controller_label = "PID"
    Kp = 0.01
    Ki = 0.01
    Kd = 0.01
    Td = Kd/Kp
    Ti = Kp/Ki

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setFixedWidth(800)
        self.setFixedHeight(600)
        self.dynamic_plotter = DynamicPlotter(
            self.centralWidget, 0.01, timewindow=10)

        self.threadpool = QThreadPool()

        self.server = ThreadedServer(0.01, self.dynamic_plotter)

        self.is_controlling = False

        print(
            "Multithreading with maximum %d threads"
            % self.threadpool.maxThreadCount()
        )

        self.graphWidget = self.dynamic_plotter.get_plot_widget()
        self.graphWidget.setObjectName("graphWidget")
        self.graphWidgetLayout.addWidget(self.graphWidget)

        self.pushButtonConnectServer.clicked.connect(
            self.init_server
        )

        self.comboBoxLoop.currentIndexChanged.connect(
            self.change_loop
        )

        self.comboBoxWaveForm.currentIndexChanged.connect(
            self.change_wave_form
        )
        self.comboBoxReferenceWaveForm.currentIndexChanged.connect(
            self.change_ref_wave_form
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

        self.pushButtonControl.clicked.connect(
            self.init_controller
        )

        self.comboBoxController.currentIndexChanged.connect(
            self.change_controller
        )
        self.doubleBoxKp.valueChanged.connect(
            self.change_Kp
        )
        self.doubleBoxKp.setValue(self.Kp)
        self.doubleBoxKd.valueChanged.connect(
            self.change_Kd
        )
        self.doubleBoxKi.valueChanged.connect(
            self.change_Ki
        )
        self.doubleBoxTd.valueChanged.connect(
            self.change_Td
        )
        self.doubleBoxTd.setValue(self.Td)
        self.doubleBoxTi.valueChanged.connect(
            self.change_Ti
        )
        self.doubleBoxTi.setValue(self.Ti)

        self.comboBoxOutput.currentIndexChanged.connect(
            self.change_output
        )

    def init_server(self):
        self.pushButtonConnectServer.setEnabled(False)
        print("started server")
        self.threadpool.start(self.server)

    def change_loop(self, i):
        if self.comboBoxLoop.itemText(i) == "Closed":
            self.server.plotter.loop = 1.0
            self.doubleBoxSetPoint.setEnabled(True)
        else:
            self.server.plotter.loop = 0.0
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

    def change_ref_wave_form(self, i):
        wave_form = self.comboBoxWaveForm.itemText(i)
        self.dynamic_plotter.set_ref_plot_func(wave_form)

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

    def change_controller(self, i):
        self.controller_label = self.comboBoxController.itemText(i)

    def change_output(self, i):
        print(f"Output updated to {self.comboBoxOutput.itemText(i)}")
        self.server.set_output_index(i)

    def change_Kp(self, value):
        self.Kp = value

    def change_Kd(self, value):
        self.Kd = value

    def change_Ki(self, value):
        self.Ki = value

    def change_Td(self, value):
        self.Td = value
        self.Kd = self.Kp * self.Td
        self.doubleBoxKd.setValue(self.Kd)

    def change_Ti(self, value):
        self.Ti = value
        self.Ki = self.Kp / self.Ti
        self.doubleBoxKi.setValue(self.Ki)

    def init_controller(self):
        if self.is_controlling:
            self.server.set_controller(None, self)
            self.pushButtonControl.setStyleSheet(
                "background-color : lightgrey"
            )
            print("shutdown controller")
        else:
            print(self.controller_label)
            print(self.Kp, self.Kd, self.Ki)
            if self.controller_label == "PID":
                controller = PIDController(
                    Kp=self.Kp, Ki=self.Ki, Kd=self.Kd, T=0.01, order=3
                )
            elif self.controller_label == "PI-D":
                controller = PI_DController(
                    Kp=self.Kp, Ki=self.Ki, Kd=self.Kd, T=0.01, order=3
                )
            else:
                controller = I_PDController(
                    Kp=self.Kp, Ki=self.Ki, Kd=self.Kd, T=0.01, order=3
                )
            self.server.set_controller(controller, self)
            self.pushButtonControl.setStyleSheet(
                "background-color : lightblue"
            )
            print("start controller")
        self.is_controlling = not self.is_controlling

    def closeEvent(self, event):
        os._exit(1)
