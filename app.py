import os

from PyQt6 import QtWidgets
from main_window import Ui_MainWindow
from dynamic_plotter import DynamicPlotter


from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool
import asyncio
import websockets
import time

from queue import Queue

queue_out = Queue(maxsize=100)
queue_in = Queue(maxsize=100)
queue_ref = Queue(maxsize=100)
queue_ref_in = Queue(maxsize=100)
loop = False


class ThreadedServer(QRunnable):

    async def server_loop(self, websocket):
        while True:
            try:
                startTime = time.time()
                await websocket.send("get references")
                received = (await websocket.recv()).split(",")
                queue_ref.put(received)
                # print(received)
                await websocket.send("get outputs")
                received = (await websocket.recv()).split(",")
                # print("Outputs: " + received[1])
                queue_out.put(received)
                while queue_in.empty():
                    time.sleep(0.0001)

                await websocket.send("set input|"+str(queue_in.get()))
                # Aqui mestre hugo
                '''if loop:
                    while queue_ref_in.empty():
                        time.sleep(0.0001)

                    await websocket.send(
                        "set references|"+str(queue_ref_in.get()))'''
                ellapsedTime = 0.0
                while ellapsedTime < 0.01:
                    time.sleep(0.0001)
                    endTime = time.time()
                    ellapsedTime = endTime - startTime
            except Exception as e:
                print(e)
                return

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

        self.server = ThreadedServer()
        self.threadpool = QThreadPool()

        print(
            "Multithreading with maximum %d threads"
            % self.threadpool.maxThreadCount()
        )

        self.dynamic_plotter = DynamicPlotter(
            self.centralWidget, queue_out, queue_in,
            queue_ref, queue_ref_in, loop, 0.01, timewindow=10)

        self.graphWidget = self.dynamic_plotter.get_plot_widget()
        self.graphWidget.setObjectName("graphWidget")
        self.graphWidgetLayout.addWidget(self.graphWidget)

        self.pushButtonConnectServer.pressed.connect(
            self.init_server
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
        print("started server")
        self.threadpool.start(self.server)
        # self.dynamic_plotter.trigger_timer()

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
