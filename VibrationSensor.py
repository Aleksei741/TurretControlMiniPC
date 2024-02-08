import time
from gpiozero import DigitalInputDevice


class hit_sensor():
	def __init__(self, Pin):
		self.DELAY = ord(b'\x44')
    
		self.delayActive = 0.5
    
		self.sensor = DigitalInputDevice(Pin, pull_up=True)
		self.timeLastActive = time.time()
		self.cnt = 0
		self.sensor.when_deactivated = self.SensorActive

	def __del__(self):
		self.sensor.close()

	def SensorActive(self):
		if self.timeLastActive + self.delayActive < time.time():
			self.timeLastActive = time.time()
			self.cnt = self.cnt + 1
      # print(f'SensorActive {self.cnt}')

	def GetCntSensor(self):
		cnt = self.cnt
		self.cnt = 0
		return cnt

	def SetParam(self, param, value):
		ret = 0
		if param == self.DELAY:
			self.delayActive = value / 1000
			print(f"Sensor delay active {self.delayActive}")          
			ret = 1
					
		return ret
