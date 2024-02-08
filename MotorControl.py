import time
from gpiozero import PWMOutputDevice, OutputDevice, LED
import threading
import configparser
import os

class motor_control():

    def __init__(self, Motor1, DirMotor1, Motor2, DirMotor2, Trigger, Magazine):
        # Константы
        self.STEPPERS_1 = ord(b'\x01')
        self.STEPPERS_2 = ord(b'\x02')
        self.FREQ_MOTOR_1 = ord(b'\x11')
        self.FREQ_MOTOR_2 = ord(b'\x12')
        self.NO_LIMIT = ord(b'\x4C')
        self.ZERO_POSITION = ord(b'\x5A')

        # Инициализаци портов
        self.Motor1 = OutputDevice(Motor1)
        # self.Motor1 = PWMOutputDevice(Motor1)
        self.DirMotor1 = OutputDevice(DirMotor1)
        self.Motor2 = OutputDevice(Motor2)
        # self.Motor2 = PWMOutputDevice(Motor2)
        self.DirMotor2 = OutputDevice(DirMotor2)
        self.Trigger = OutputDevice(Trigger)
        self.Magazine = OutputDevice(Magazine)
        self.timeLastControl = time.time()

        # Инициализируем параметры перемещения
        self.config = configparser.ConfigParser()
        if os.path.exists("MotorControl.ini"):
            self.config.read("MotorControl.ini")
        else:
            self.config["MotionOption"] = {}
            self.config["MotionOption"]["MaxSteppersM1"] = 0
            self.config["MotionOption"]["MaxSteppersM2"] = 0
            self.config["MotionOption"]["FreqM1"] = 200
            self.config["MotionOption"]["FreqM2"] = 200
        self.MaxSteppersM1 = self.config["MotionOption"]["MaxSteppersM1"]
        self.MaxSteppersM2 = self.config["MotionOption"]["MaxSteppersM2"]
        self.FreqM1 = self.config["MotionOption"]["FreqM1"]
        self.FreqM2 = self.config["MotionOption"]["FreqM2"]
        self.DelayM1 = 1.0/float(self.FreqM1)
        if self.DelayM1 < 0.001:
            self.DelayM1 = 0.001
        self.DelayM2 = 1.0/float(self.FreqM2)
        if self.DelayM2 < 0.001:
            self.DelayM2 = 0.001
        self.PositionMotor1 = 0
        self.PositionMotor2 = 0
        self.NeedPositionMotor1 = 0
        self.NeedPositionMotor2 = 0

        # Иниализация основного потока работы
        self.MotionProcessingM1_thread = threading.Thread(target=self.__MotionProcessingM1)
        self.MotionProcessingM1_thread.start()
        self.MotionProcessingM2_thread = threading.Thread(target=self.__MotionProcessingM2)
        self.MotionProcessingM2_thread.start()

        self.watch_dog_thread = threading.Thread(target=self.__watch_dog)
        self.watch_dog_active = True
        self.watch_dog_thread.start()

    def __del__(self):
        self.MotionProcessingM1_thread.join()
        self.MotionProcessingM2_thread.join()
        self.watch_dog_active = False
        self.Motor1.off()
        self.Motor1.close()
        self.DirMotor1.off()
        self.DirMotor1.close()
        self.Motor2.off()
        self.Motor2.close()
        self.DirMotor2.off()
        self.DirMotor2.close()
        self.Trigger.off()
        self.Trigger.close()
        self.watch_dog_thread.join()

    def __MotionProcessingM1(self):
        time.sleep(1)

    def __MotionProcessingM2(self):
        time.sleep(1)

    @staticmethod
    def rotate_clockwise(driver_pin):
        if driver_pin.value == 0:
            driver_pin.on()

    @staticmethod
    def rotate_counterclockwise(driver_pin):
        if driver_pin.value == 1:
            driver_pin.off()

    def __flagLastControl(self):
        self.timeLastControl = time.time()

    def motionMotor1(self, command):
        if command == 65535:
            pass
        else:
            self.NeedPositionMotor1 = self.NeedPositionMotor1 + command
            if self.NeedPositionMotor1 < 0:
                self.NeedPositionMotor1 = 0
            elif self.NeedPositionMotor1 > self.MaxSteppersM1:
                self.NeedPositionMotor1 = self.MaxSteppersM1
        self.__flagLastControl()

    def motionMotor2(self, command):
        if command == 65535:
            pass
        else:
            self.NeedPositionMotor2 = self.NeedPositionMotor2 + command
            if self.NeedPositionMotor2 < 0:
                self.NeedPositionMotor2 = 0
            elif self.NeedPositionMotor2 > self.MaxSteppersM2:
                self.NeedPositionMotor2 = self.MaxSteppersM2
        self.__flagLastControl()

    def motionTrigger(self, command):
        if command > 0:
            if self.Trigger.value == 0:
                self.Trigger.on()
                self.Magazine.on()
        else:
            if self.Trigger.value == 1:
                self.Trigger.off()
                self.Magazine.off()
        self.__flagLastControl()

    def motionAllOff(self):
        self.NeedPositionMotor2 = self.PositionMotor1
        self.NeedPositionMotor2 = self.PositionMotor2
        self.motionTrigger(0)

    def __watch_dog(self):
        while(self.watch_dog_active):
            if time.time() - self.timeLastControl > 0.25:
                self.motionAllOff()
            time.sleep(0.05)


