#!/usr/bin/env python

from dynamic_plotter import DynamicPlotter
from main_window import Ui_MainWindow
import sys  # We need sys so that we can pass argv to QApplication
from PyQt6 import QtWidgets, QtGui, QtCore
import app
import asyncio
import threading
import websockets
import time

from queue import Queue

queue = Queue(maxsize=100)


async def echo(websocket):
    while True:
        try:
            await websocket.send("get references")
            received = (await websocket.recv()).split(",")
            # print("Reference: " + received[1])
            await websocket.send("get outputs")
            received = (await websocket.recv()).split(",")
            #print("Outputs: " + received[1])
            queue.put(received[1])
            time.sleep(0.05)
        except Exception as e:
            print(e)
            return


async def foo():
    async with websockets.serve(echo, "localhost", 6660):
        await asyncio.Future()


def view():
    '''while True:
        try:
            if not queue.empty():
                print("oi")
                view = queue.get()
                print(view)
        except Exception as e:
            print(e)
            return'''

    gui = QtWidgets.QApplication(sys.argv)

    window = app.MainWindow(queue)
    window.setWindowIcon(QtGui.QIcon("qtui/feedback.png"))
    window.show()
    gui.exec()

import ctypes
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

server = websockets.serve(echo, "localhost", 6660)
asyncio.get_event_loop().run_until_complete(server)
y = threading.Thread(target=view)
y.start()

asyncio.get_event_loop().run_forever()
y.join()
