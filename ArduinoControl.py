from math import *
from serial import Serial
from ControlLib import *


# for china arduino nano:
# - Install CH34x driver
# - restart in recovery mode (Commnand-R)  (do not use USB-C monitor!!!)
# -- use terminal and do #> csrutil disable (in recovery mode)
# - on normal mode #> sudo nvram boot-args="kext-dev-mode=1"
# - exchange the cable (looks silly but I had to do twice)

class HardwareControl(Control):

	def __init__(self, serialPort, T = 0.1, scale = 100.0, verbose = False):
		super().__init__(T, 3)

		self.verbose = verbose
		self.serial = Serial('/dev/'+serialPort, 115200)
		self.scale = scale


	def control(self):

		controlSignal = 0.0

		try:
			self.serial.flushInput()
			self.serial.read_until().decode("utf-8") 
			controlSignal = self.scale*(float(self.serial.read_until().decode("utf-8"))-450.0)/450.0
			print(f'u = {controlSignal}') if self.verbose else None

		except:
			print('Problem with serial or socket...') if self.verbose else None

		return controlSignal



if __name__=='__main__':
	controller = HardwareControl('tty.wchusbserial146140', 0.01, 100.0, True)
	rc = RemoteControl(controller, True)
	rc.run()