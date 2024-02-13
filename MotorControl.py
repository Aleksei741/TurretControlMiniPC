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
        self.RotateM1 = False
        self.RotateM2 = False

        # инициализация флагов
        self.NoLimit = False
        self.ZeroPositionSet = False

        # Иниализация основного потока работы
        self.ThreadMotionActive = True
        self.MotionProcessingM1_thread = threading.Thread(target=self.__MotionProcessingM1)
        self.MotionProcessingM1_thread.start()
        self.MotionProcessingM2_thread = threading.Thread(target=self.__MotionProcessingM2)
        self.MotionProcessingM2_thread.start()
        self.ImpulseM1_thread = threading.Thread(target=self.__ImpulseM1)
        self.ImpulseM2_thread = threading.Thread(target=self.__ImpulseM2)

        self.watch_dog_thread = threading.Thread(target=self.__watch_dog)
        self.watch_dog_active = True
        self.watch_dog_thread.start()

    def __del__(self):
        self.ThreadMotionActive = False
        self.watch_dog_active = False
        self.MotionProcessingM1_thread.join()
        self.MotionProcessingM2_thread.join()
        self.watch_dog_thread.join()
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

    def __MotionProcessingM1(self):
        while self.ThreadMotionActive:
            if self.PositionMotor1 != self.NeedPositionMotor1:
                # выбор направления движения
                if self.PositionMotor1 > self.NeedPositionMotor1:
                    if self.DirMotor1.value == 0:
                        self.DirMotor1.on()
                elif self.PositionMotor1 < self.NeedPositionMotor1:
                    if self.DirMotor1.value == 1:
                        self.DirMotor1.off()

                # делаем шаг
                self.ImpulseM1_thread.join()
                self.ImpulseM1_thread.start()

                # Считаем шаг
                if self.DirMotor1.value == 1:
                    self.PositionMotor1 = self.PositionMotor1 + 1
                else:
                    self.PositionMotor1 = self.PositionMotor1 - 1

                # делаем задержку
                time.delay(self.DelayM1)
            else:
                self.ImpulseM1_thread.join()
                if self.DirMotor1.value == 1:
                    self.DirMotor1.off()
                time.sleep(0.1)

    def __MotionProcessingM2(self):
        while self.ThreadMotionActive:
            if self.PositionMotor2 != self.NeedPositionMotor2:
                # выбор направления движения
                if self.PositionMotor2 > self.NeedPositionMotor2:
                    if self.DirMotor2.value == 0:
                        self.DirMotor2.on()
                elif self.PositionMotor2 < self.NeedPositionMotor2:
                    if self.DirMotor2.value == 1:
                        self.DirMotor2.off()

                # делаем шаг
                self.ImpulseM2_thread.join()
                self.ImpulseM2_thread.start()

                # Считаем шаг
                if self.DirMotor2.value == 1:
                    self.PositionMotor2 = self.PositionMotor2 + 1
                else:
                    self.PositionMotor2 = self.PositionMotor2 - 1

                # делаем задержку
                time.delay(self.DelayM2)
            else:
                self.ImpulseM2_thread.join()
                if self.DirMotor2.value == 1:
                    self.DirMotor2.off()
                time.sleep(0.05)

    def __ImpulseM1(self):
        self.Motor1.on()
        time.nanosleep(self.DelayM1 / 3 * 1000000000)
        self.Motor1.off()
        time.nanosleep(self.DelayM1 * 0.1 * 1000000000)

    def __ImpulseM2(self):
        self.Motor2.on()
        time.nanosleep(self.DelayM2 / 3 * 1000000000)
        self.Motor2.off()
        time.nanosleep(self.DelayM2 * 0.1 * 1000000000)

    def motionMotor1(self, command):
        if abs(command) == 32000:
            self.RotateM1 = True
            self.NeedPositionMotor1 = self.PositionMotor1 + command
        elif self.RotateM1:
            self.RotateM1 = False
            self.NeedPositionMotor1 = self.PositionMotor1
        else:
            self.NeedPositionMotor1 = self.NeedPositionMotor1 + command

        if self.NeedPositionMotor1 < 0:
            if not self.NoLimit:
                self.NeedPositionMotor1 = 0
        elif self.NeedPositionMotor1 > self.MaxSteppersM1:
            if not self.NoLimit:
                self.NeedPositionMotor1 = self.MaxSteppersM1

        self.__flagLastControl()

    def motionMotor2(self, command):
        if abs(command) == 32000:
            self.RotateM2 = True
            self.NeedPositionMotor2 = self.PositionMotor1 + command
        elif self.RotateM2:
            self.RotateM2 = False
            self.NeedPositionMotor1 = self.PositionMotor1
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
        self.NeedPositionMotor1 = self.PositionMotor1
        self.NeedPositionMotor2 = self.PositionMotor2
        self.motionTrigger(0)

    def SetParam(self, param, value):
        ret = 0
        if param == self.STEPPERS_1:
            self.config["MotionOption"]["MaxSteppersM1"] = value
            self.MaxSteppersM1 = self.config["MotionOption"]["MaxSteppersM1"]
            print(f"Max steppers step motor 1 {self.MaxSteppersM1}")
            ret = 1
        elif param == self.STEPPERS_2:
            self.config["MotionOption"]["MaxSteppersM2"] = value
            self.MaxSteppersM2 = self.config["MotionOption"]["MaxSteppersM2"]
            print(f"Max steppers step motor 2 {self.MaxSteppersM2}")
            ret = 1
        elif param == self.FREQ_MOTOR_1:
            self.config["MotionOption"]["FreqM1"] = value
            self.FreqM1 = self.config["MotionOption"]["FreqM1"]
            print(f"Freq motor 1 {self.FreqM1}")
            self.DelayM1 = 1.0 / float(self.FreqM1)
            if self.DelayM1 < 0.001:
                self.DelayM1 = 0.001
            print(f"Delay motor 1 {self.DelayM1}")
            ret = 1
        elif param == self.FREQ_MOTOR_2:
            self.config["MotionOption"]["FreqM2"] = value
            self.FreqM2 = self.config["MotionOption"]["FreqM2"]
            print(f"Freq motor 2 {self.FreqM2}")
            self.DelayM2 = 1.0 / float(self.FreqM2)
            if self.DelayM2 < 0.001:
                self.DelayM2 = 0.001
            print(f"Delay motor 1 {self.DelayM2}")
            ret = 1

        if ret:
            with open('MotorControl.ini', 'w') as configfile:
                self.write(configfile)

        return ret

    def GetParam(self, param):
        if param == self.STEPPERS_1:
            return self.MaxSteppersM1
        elif param == self.STEPPERS_2:
            return self.MaxSteppersM2
        elif param == self.FREQ_MOTOR_1:
            return self.FreqM1
        elif param == self.FREQ_MOTOR_2:
            return self.FreqM2

        return None

    def SetFlag(self, flag, value):
        ret = 0
        if flag == self.NO_LIMIT:
            self.NoLimit = value
            print(f"NoLimit {self.NoLimit}")
            ret = 1
        elif flag == self.ZERO_POSITION:
            if value == 1:
                self.PositionMotor1 = 0
                self.PositionMotor2 = 0
                self.NeedPositionMotor1 = 0
                self.NeedPositionMotor2 = 0
                print(f"ZeroPosition {self.ZERO_POSITION}")
            ret = 1

        return ret

    def GetPositionM1(self):
        return self.PositionMotor1

    def GetPositionM2(self):
        return self.PositionMotor2

    def GetNeedPositionM1(self):
        return self.NeedPositionMotor1

    def GetNeedPositionM2(self):
        return self.NeedPositionMotor2

    def __flagLastControl(self):
        self.timeLastControl = time.time()

    def __watch_dog(self):
        while(self.watch_dog_active):
            if time.time() - self.timeLastControl > 0.25:
                self.motionAllOff()
            time.sleep(0.05)


