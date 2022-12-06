from ControlLib import *
from math import *
import numpy as np


class PID(Control): 

	def __init__(self, T, KP, KI, KD):
		super().__init__(T, 3)
		self.KP = KP
		self.KI = KI
		self.KD = KD

	def control(self):

		u0 = self.u(-1) + self.KI*self.e(-1) + self.T*self.KP*(self.e(0) - self.e(-1)) + self.KD*(self.e(0) - 2*self.e(-1) + self.e(-2))/self.T

		return u0



T = 0.2


# simple spring-mass (default parameters)
KP = 16.0
KI = 1.0
KD = 0.009


controller = PID(T, KP, KI, KD)


rc = RemoteControl(controller)


rc.run()