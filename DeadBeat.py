from ControlLib import *
from math import *
import numpy as np


class DeadBeat(Control): 

	def __init__(self, T, a1, a2, b0, b1, b2):
		super().__init__(T, 3)
		self.a1 = a1
		self.a2 = a2
		self.b0 = b0
		self.b1 = b1
		self.b2 = b2

	def control(self):

		
		# computed
		u0 = - self.a1*self.u(-1) - self.a2*self.u(-2) + self.b0*self.e(0) + self.b1*self.e(-1)  + self.b2*self.e(-2) 

		return u0



T = 0.7


# simple spring-mass (default parameters)
# b0 = 1.000000000000000;  b1 = -1.355665568462296; b2 = 0.579226885074133
# a0 = 0.459319438977445;  a1 = -0.695344584432624; a2 = 0.236025145455179


# G =
#        0.55 s + 0.4
#   ----------------------
#   0.6 s^2 + 0.55 s + 0.4


# H =
#    0.4285 z - 0.2967
#   --------------------
#   z^2 - 1.5 z + 0.6323


# C =
#     z^2 - 0.174 z + 0.1599
#   ---------------------------
#   1.178 z^2 - 1.37 z + 0.1918


b0 = 1.0;  b1 = -0.174; b2 = 0.1599
a0 = 1.178; a1 = -1.137; a2 = 0.1918


controller = DeadBeat(T, a1/a0, a2/a0, b0/a0, b1/a0, b2/a0)
rc = RemoteControl(controller)
rc.run()