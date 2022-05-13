import os

from PyQt6 import QtWidgets
from main_window import Ui_MainWindow
from dynamic_plotter import DynamicPlotter


from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool
import asyncio
import websockets
import time

from websockets.exceptions import ConnectionClosedError


class ThreadedServer(QRunnable):

    def __init__(self, sampling_time, plotter):
        super().__init__()
        self.sampling_time = sampling_time
        self.plotter = plotter

    async def server_loop(self, websocket):
        while True:
            try:
                startTime = time.time()

                await websocket.send("get references")
                received = await websocket.recv()
                n_refs, refs = self.parse_message(received)

                await websocket.send("get outputs")
                received = await websocket.recv()
                n_outs, outs = self.parse_message(received)
                input = self.plotter.update_plot(refs, outs, time.time())

                if input is not None:
                    await websocket.send("set input|"+str(input))

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
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setFixedWidth(800)
        self.setFixedHeight(600)
        self.dynamic_plotter = DynamicPlotter(
            self.centralWidget, 0.01, timewindow=10)

        self.threadpool = QThreadPool()

        self.server = ThreadedServer(0.01, self.dynamic_plotter)

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

        self.pushButtonRefreshGraphics.clicked.connect(
            self.refresh_graph
        )

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

    def init_server(self):
        self.pushButtonConnectServer.setEnabled(False)
        print("started server")
        self.threadpool.start(self.server)

    def refresh_graph(self):
        pass

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
