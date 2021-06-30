import asyncio
import websockets
from collections import deque
from math import *
import numpy as np
import time

class Control:
	def __init__(self, T=0.3, order=3):
		self.T = T
		self._e = deque([0]*order)
		self._u = deque([0]*order)
		self._y = deque([0]*order)
		self._r = deque([0]*order)
		self.currU = 0
		self.time = 0.0



	def reference(self, ref):
		self._r.rotate(-1)
		self._r[-1] = ref



	def measured(self, y):

		error = self._r[-1] - y

		self._e.rotate(-1)
		self._e[-1] = error

		self._y.rotate(-1)
		self._y[-1] = y


	def control(self):

		return 0


	def apply(self, controlSignal):

		self._u.rotate(-1)
		self._u[-1] = controlSignal


	def u(self, index = 0):
		return self._u[index]
	def e(self, index = 0):
		return self._e[index-1]
	def r(self, index = 0):
		return self._r[index-1]
	def y(self, index = 0):
		return self._y[index-1]



class RemoteControl:

	def __init__(self, controller, verbose = False):

		self.controller = controller
		self.verbose = verbose



	async def serverLoop(self, websocket, path):

		while True:
			startTime = time.time()

			await asyncio.sleep(self.controller.T)

			self.controller.time += self.controller.T

			try:

				print('get references') if self.verbose else None
				references = [];
				await websocket.send('get references')
				received = (await websocket.recv()).split(',')
				print(received) if self.verbose else None
				ref = float(received[1])

				if isnan(ref):
					ref = 0.0


				print('get outputs') if self.verbose else None
				outputs = [];
				await websocket.send('get outputs')
				received = (await websocket.recv()).split(',')
				print(received) if self.verbose else None
				out = float(received[1])




				self.controller.reference(ref)

				self.controller.measured(out)

				u = self.controller.control()

				self.controller.apply(u)




				
				print(f'u = {u}') if self.verbose else None
				await websocket.send('set input|'+f"{u}")


				ellapsedTime = 0.0

				while ellapsedTime < self.controller.T:
					time.sleep(0.0001)
					endTime = time.time()
					ellapsedTime = endTime - startTime


				print('%.4f %.4f %.4f %.4f %.4f, (%.4f)'%(self.controller.time, ref, out, u, self.controller.T, ellapsedTime))				


			except:
				print('System not active...') if self.verbose else None

	def run(self):

		server = websockets.serve(self.serverLoop, "localhost", 6660)

		asyncio.ensure_future(server)
		asyncio.get_event_loop().run_forever()













