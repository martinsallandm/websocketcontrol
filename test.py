#!/usr/bin/env python

import asyncio
import websockets

queue = asyncio.Queue()

async def echo(websocket):
	while True:
		await websocket.send("get references")
		received = (await websocket.recv()).split(',')
		#print(received)
		await websocket.send("get outputs")
		received = (await websocket.recv()).split(',')
		#print(received)
		await queue.put(received)

async def view():
	while True:
		if not queue.empty():
			print("oi")
			view = await queue.get()
			print(view)

async def main():
	async with websockets.serve(echo, "localhost", 6660):
		await asyncio.Future()  # run forever
	'''server = websockets.serve(echo, "localhost", 6660)
	asyncio.ensure_future(server)
	viewer = view()
	asyncio.ensure_future(viewer)
	asyncio.get_event_loop().run_forever()'''
asyncio.run(main())