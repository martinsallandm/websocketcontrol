#!/usr/bin/env python

import asyncio
import threading
import websockets

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
            print("Outputs: " + received[1])
            queue.put(received)
        except Exception as e:
            print(e)
            return


async def foo():
    async with websockets.serve(echo, "localhost", 6660):
        await asyncio.Future()


def view():
    while True:
        try:
            #print("estou vivo")
            if not queue.empty():
                print("oi")
                view = queue.get()
                print(view)
        except Exception as e:
            print(e)
            return


server = websockets.serve(echo, "localhost", 6660)
asyncio.get_event_loop().run_until_complete(server)
y = threading.Thread(target=view)
y.start()
asyncio.get_event_loop().run_forever()
y.join()
