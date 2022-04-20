#!/usr/bin/env python

import ctypes
import sys  # We need sys so that we can pass argv to QApplication
from PyQt6 import QtWidgets, QtGui
import app
import asyncio
import threading
import websockets
import time

from queue import Queue

queue_out = Queue(maxsize=100)
queue_in = Queue(maxsize=100)
queue_ref = Queue(maxsize=100)
queue_ref_in = Queue(maxsize=100)
loop = False


async def echo(websocket):
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

                await websocket.send("set references|"+str(queue_ref_in.get()))'''
            ellapsedTime = 0.0
            while ellapsedTime < 0.01:
                time.sleep(0.0001)
                endTime = time.time()
                ellapsedTime = endTime - startTime
        except Exception as e:
            print(e)
            return


def view():

    gui = QtWidgets.QApplication(sys.argv)

    window = app.MainWindow(queue_out, queue_in, queue_ref, queue_ref_in, loop)
    window.setWindowIcon(QtGui.QIcon("qtui/feedback.png"))
    window.show()
    gui.exec()


myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

server = websockets.serve(echo, "localhost", 6660)
asyncio.get_event_loop().run_until_complete(server)
y = threading.Thread(target=view)
y.start()

asyncio.get_event_loop().run_forever()
y.join()
