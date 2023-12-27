import time
from gpiozero import DigitalInputDevice


class hit_sensor():
	def __init__(self, Pin):
		self.sensor = DigitalInputDevice(Pin, pull_up=True)
		self.timeLastActive = time.time()
		self.cnt = 0
		self.sensor.when_deactivated = self.SensorActive

	def SensorActive(self):
		if self.timeLastActive + 0.1 < time.time():
			self.timeLastActive = time.time()
			self.cnt = self.cnt + 1
      # print(f'SensorActive {self.cnt}')

	def GetCntSensor(self):
		cnt = self.cnt
		self.cnt = 0
		return cnt
			
