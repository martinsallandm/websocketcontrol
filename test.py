#!/usr/bin/env python

import asyncio
import threading
import websockets

from queue import Queue

queue = Queue(maxsize=100)


async def echo(websocket):
    while True:
        await websocket.send("get references")
        received = (await websocket.recv()).split(",")
        # print("Reference: " + received[1])
        await websocket.send("get outputs")
        received = (await websocket.recv()).split(",")
        print("Outputs: " + received[1])
        queue.put(received)


def view():
    while True:
        print("estou vivo")
        if not queue.empty():
            print("oi")
            view = queue.get()
            print(view)


async def main():
    async with websockets.serve(echo, "localhost", 6660):
        await asyncio.Future()  # run forever

    # server = websockets.serve(echo, "localhost", 6660)
    # asyncio.ensure_future(server)
    # asyncio.get_event_loop().run_forever()


x = threading.Thread(target=view)
x.start()

y = threading.Thread(target=main)
y.start()
