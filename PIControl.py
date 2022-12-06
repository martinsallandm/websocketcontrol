from ControlLib import *
from math import *
import numpy as np


class PI(Control): 

	def __init__(self, T, KP, KI):
		super().__init__(T, 3)
		self.KP = KP
		self.KI = KI

	def control(self):

		u0 = self.u(-1) + self.KI*self.e(-1) + self.T*self.KP*(self.e(0) - self.e(-1))

		return u0



T = 0.3

KP = 15.5
KI = 3.0


controller = PI(T, KP, KI)


rc = RemoteControl(controller)


rc.run()