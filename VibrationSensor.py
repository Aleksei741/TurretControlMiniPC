import time
from gpiozero import DigitalInputDevice
import configparser
import os
import threading
from collections import deque

class hit_sensor():

	def __init__(self, Pin):
		self.DELAY = ord(b'\x44')
		self.HEALTH = ord(b'\x48')
		self.MINUTES = ord(b'\x4D')
		self.SECONDS = ord(b'\x53')
		self.RESET = ord(b'\x52')

		# Флаг сброс урона
		self.ResetDmg = False

		# Инициализируем параметры перемещения
		self.config = configparser.ConfigParser()
		if os.path.exists("Sensor.ini"):
			self.config.read("Sensor.ini")
		else:
			self.config["Sensor"] = {}
			self.config["Health"] = {}
			self.config["Sensor"]["Delay"] = '500'
			self.config["Health"]["Health"] = '20'
			self.config["Health"]["Minutes"] = '1'
			self.config["Health"]["Seconds"] = '30'

		self.delaySensor = float(int(self.config["Sensor"]["Delay"]))/1000.0
		self.NumHealth = int(self.config["Health"]["Health"])
		self.Health = self.NumHealth
		self.DamageLifeTimeMin = int(self.config["Health"]["Minutes"])
		self.DamageLifeTimeSec = int(self.config["Health"]["Seconds"])
		self.DamageLifeTime = self.DamageLifeTimeMin * 60 + self.DamageLifeTimeSec

		# Обработчик прерываний с ноги платы
		self.sensor = DigitalInputDevice(Pin, pull_up=True)
		self.timeLastActive = time.time()
		self.sensor.when_deactivated = self.SensorActive

		# Лист с повреждениями
		self.Damage = list()

		# Роцедура расчета HP
		self.DemageCalc_thread = threading.Thread(target=self.__DemageCalcProcedure)
		self.DemageCalc_thread.start()

		# Поток сохранения параметров
		self.SaveParameters_event = threading.Event()
		self.SaveParameters_thread = threading.Thread(target=self.__SaveParameters)
		self.SaveParameters_thread.start()

	def __del__(self):
		self.sensor.close()
		self.SaveParameters_thread.terminate()
		self.DemageCalc_thread.terminate()

	def __DemageCalcProcedure(self):
		while True:
			while self.Damage:
				if self.Damage[0] + self.DamageLifeTime < time.time():
					self.Damage.pop(0)
				else:
					break
			if self.ResetDmg:
				self.Damage.clear()
				self.ResetDmg = False
			self.Health = self.NumHealth - len(self.Damage)
			time.sleep(self.delaySensor / 4)

	# прерывание
	def SensorActive(self):
		if self.timeLastActive + self.delaySensor < time.time():
			self.timeLastActive = time.time()
			self.Damage.append(time.time())

	def GetHealth(self):
		return self.Health

	def GetParam(self, param):
		if param == self.DELAY:
			print(f"Request delay {int(self.delaySensor * 1000)}")
			return int(self.delaySensor * 1000)
		elif param == self.HEALTH:
			print(f"Request healt {self.NumHealth}")
			return self.NumHealth
		elif param == self.MINUTES:
			print(f"Request DamageLifeTimeMin {self.DamageLifeTimeMin}")
			return self.DamageLifeTimeMin
		elif param == self.SECONDS:
			print(f"Request DamageLifeTimeSec {self.DamageLifeTimeSec}")
			return self.DamageLifeTimeSec

		return None

	def SetParam(self, param, value):
		ret = 0
		if param == self.DELAY:
			self.config["Sensor"]["Delay"] = str(value)
			self.delaySensor = float(int(self.config["Sensor"]["Delay"]))/1000.0
			print(f"Sensor delay active {self.delaySensor}")
			ret = 1
		elif param == self.HEALTH:
			if value > 120:
				value = 120
			self.config["Health"]["Health"] = str(value)
			self.NumHealth = int(self.config["Health"]["Health"])
			print(f"Health Set {self.NumHealth}")
			ret = 1
		elif param == self.MINUTES:
			self.config["Health"]["Minutes"] = str(value)
			self.DamageLifeTimeMin = int(self.config["Health"]["Minutes"])
			self.DamageLifeTime = self.DamageLifeTimeMin * 60 + self.DamageLifeTimeSec
			print(f"Damage lifetime {self.DamageLifeTime}")
			ret = 1
		elif param == self.SECONDS:
			if value >= 60:
				value = 59
			self.config["Health"]["Seconds"] = str(value)
			self.DamageLifeTimeSec = int(self.config["Health"]["Seconds"])
			self.DamageLifeTime = self.DamageLifeTimeMin * 60 + self.DamageLifeTimeSec
			print(f"Damage lifetime {self.DamageLifeTime}")
			ret = 1

		if ret:
			self.SaveParameters_event.set()

		return ret

	def SetFlag(self, flag, value):
		ret = 0
		if flag == self.RESET:
			self.ResetDmg = True
			print(f"Reset damage")
			ret = 1

		return ret

	def __SaveParameters(self):
		while True:
			self.SaveParameters_event.wait()
			time.sleep(5)
			with open('Sensor.ini', 'w') as configfile:
				self.config.write(configfile)
			self.SaveParameters_event.clear()
