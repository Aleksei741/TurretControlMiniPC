import time
from gpiozero import PWMOutputDevice, OutputDevice, LED
import threading
import configparser
import os

class motor_control():

    def __init__(self, Motor1, DirMotor1, Motor2, DirMotor2, Trigger, Magazine):
        # Константы
        self.MAX_POSITION_STEPPERS_1 = ord(b'\x01')
        self.MAX_POSITION_STEPPERS_2 = ord(b'\x02')
        self.MIN_POSITION_STEPPERS_1 = ord(b'\x03')
        self.MIN_POSITION_STEPPERS_2 = ord(b'\x04')
        self.FREQ_MOTOR_1 = ord(b'\x11')
        self.FREQ_MOTOR_2 = ord(b'\x12')
        self.NO_LIMIT = ord(b'\x4C')
        self.ZERO_POSITION = ord(b'\x46')

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
            self.config["MotionOption"]["MaxPositionM1"] = '0'
            self.config["MotionOption"]["MaxPositionM2"] = '0'
            self.config["MotionOption"]["MinPositionM1"] = '0'
            self.config["MotionOption"]["MinPositionM2"] = '0'
            self.config["MotionOption"]["FreqM1"] = '200'
            self.config["MotionOption"]["FreqM2"] = '200'
        self.MaxPositionM1 = int(self.config["MotionOption"]["MaxPositionM1"])
        self.MaxPositionM2 = int(self.config["MotionOption"]["MaxPositionM2"])
        self.MinPositionM1 = int(self.config["MotionOption"]["MinPositionM1"])
        self.MinPositionM2 = int(self.config["MotionOption"]["MinPositionM2"])
        self.FreqM1 = int(self.config["MotionOption"]["FreqM1"])
        if self.FreqM1 == 0:
            self.FreqM1 = 1
        self.FreqM2 = int(self.config["MotionOption"]["FreqM2"])
        if self.FreqM2 == 0:
            self.FreqM2 = 1
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

        # Плавный старт/стоп
        self.IndexM1 = 0
        self.IndexM2 = 0
        self.__initDelayMas()

        # Иниализация основного потока работы
        self.ThreadMotionActive = True
        self.ImpulseM1_event = threading.Event()
        self.ImpulseM2_event = threading.Event()
        self.ImpulseM1_thread = threading.Thread(target=self.__ImpulseM1)
        self.ImpulseM2_thread = threading.Thread(target=self.__ImpulseM2)
        self.ImpulseM1_thread.start()
        self.ImpulseM2_thread.start()
        self.MotionProcessingM1_thread = threading.Thread(target=self.__MotionProcessingM1)
        self.MotionProcessingM1_thread.start()
        self.MotionProcessingM2_thread = threading.Thread(target=self.__MotionProcessingM2)
        self.MotionProcessingM2_thread.start()

        self.SaveParameters_event = threading.Event()
        self.SaveParameters_thread = threading.Thread(target=self.__SaveParameters)
        self.SaveParameters_thread.start()
        
        self.watch_dog_thread = threading.Thread(target=self.__watch_dog)
        self.watch_dog_active = True
        self.watch_dog_thread.start()

    def __initDelayMas(self):
        self.DelayMasM1 = [self.DelayM1 * 9, self.DelayM1 * 9,
                           self.DelayM1 * 8, self.DelayM1 * 7, self.DelayM1 * 6, self.DelayM1 * 5, self.DelayM1 * 4,
                           self.DelayM1 * 3, self.DelayM1 * 2, self.DelayM1]
        self.DelayMasM2 = [self.DelayM2 * 9, self.DelayM2 * 9,
                           self.DelayM2 * 8, self.DelayM2 * 7, self.DelayM2 * 6, self.DelayM2 * 5, self.DelayM2 * 4,
                           self.DelayM2 * 3, self.DelayM2 * 2, self.DelayM2]

    def __del__(self):
        self.ThreadMotionActive = False
        self.watch_dog_active = False
        self.MotionProcessingM1_thread.join()
        self.MotionProcessingM2_thread.join()
        self.ImpulseM1_thread.terminate()
        self.ImpulseM2_thread.terminate()
        self.SaveParameters_thread.terminate()
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
            if self.PositionMotor1 != self.NeedPositionMotor1 or self.IndexM1:
                
                # выбор направления движения
                if not self.IndexM1:
                    if self.PositionMotor1 > self.NeedPositionMotor1:
                        if self.DirMotor1.value == 1:
                            self.DirMotor1.off()
                    elif self.PositionMotor1 < self.NeedPositionMotor1:
                        if self.DirMotor1.value == 0:
                            self.DirMotor1.on()

                # делаем шаг
                self.ImpulseM1_event.set()

                # Считаем шаг
                if self.DirMotor1.value == 1:   # Направо
                    self.PositionMotor1 = self.PositionMotor1 + 1
                else:   # Налево
                    self.PositionMotor1 = self.PositionMotor1 - 1

                # делаем задержку
                time.sleep(self.DelayMasM1[self.IndexM1])

                # Считаем задержку
                len_mas = len(self.DelayMasM1)
                if self.DirMotor1.value == 1:   # Направо
                    if self.PositionMotor1 < self.NeedPositionMotor1:
                        Diff = self.NeedPositionMotor1 - self.PositionMotor1
                        if (Diff > len_mas) and (self.IndexM1 < len_mas-1):
                            self.IndexM1 = self.IndexM1 + 1
                        elif (Diff > len_mas / 2) and (self.IndexM1 < len_mas / 2):
                            self.IndexM1 = self.IndexM1 + 1
                        elif (Diff < len_mas) and (self.IndexM1 > 0):
                            self.IndexM1 = self.IndexM1 - 1
                    elif self.IndexM1:
                        self.IndexM1 = self.IndexM1 - 1
                else:   # Налево
                    if self.PositionMotor1 > self.NeedPositionMotor1:
                        Diff = self.PositionMotor1 - self.NeedPositionMotor1
                        if (Diff > len_mas) and (self.IndexM1 < len_mas-1):
                            self.IndexM1 = self.IndexM1 + 1
                        elif (Diff > len_mas / 2) and (self.IndexM1 < len_mas / 2):
                            self.IndexM1 = self.IndexM1 + 1
                        elif (Diff < len_mas) and (self.IndexM1 > 0):
                            self.IndexM1 = self.IndexM1 - 1
                    elif self.IndexM1:
                        self.IndexM1 = self.IndexM1 - 1
                        
            else:
                # self.ImpulseM1_thread.join()
                if self.DirMotor1.value == 1:
                    self.DirMotor1.off()
                time.sleep(0.05)

    def __MotionProcessingM2(self):
        while self.ThreadMotionActive:
            if self.PositionMotor2 != self.NeedPositionMotor2 or self.IndexM2:

                # выбор направления движения
                if not self.IndexM2:
                    if self.PositionMotor2 > self.NeedPositionMotor2:
                        if self.DirMotor2.value == 0:
                            self.DirMotor2.on()
                    elif self.PositionMotor2 < self.NeedPositionMotor2:
                        if self.DirMotor2.value == 1:
                            self.DirMotor2.off()
                
                # делаем шаг
                self.ImpulseM2_event.set()

                # Считаем шаг
                if self.DirMotor2.value == 0:
                    self.PositionMotor2 = self.PositionMotor2 + 1
                else:
                    self.PositionMotor2 = self.PositionMotor2 - 1

                # делаем задержку
                time.sleep(self.DelayMasM2[self.IndexM2])

                # Считаем задержку
                len_mas = len(self.DelayMasM2)
                if self.DirMotor2.value == 0:  
                    if self.PositionMotor2 < self.NeedPositionMotor2:
                        Diff = self.NeedPositionMotor2 - self.PositionMotor2
                        if (Diff > len_mas) and (self.IndexM2 < len_mas-1):
                            self.IndexM2 = self.IndexM2 + 1
                        elif (Diff > len_mas / 2) and (self.IndexM2 < len_mas / 2):
                            self.IndexM2 = self.IndexM2 + 1
                        elif (Diff < len(self.DelayMasM2)) and (self.IndexM2 > 0):
                            self.IndexM2 = self.IndexM2 - 1
                    elif self.IndexM2:
                        self.IndexM2 = self.IndexM2 - 1
                else:  
                    if self.PositionMotor2 > self.NeedPositionMotor2:
                        Diff = self.PositionMotor2 - self.NeedPositionMotor2
                        if (Diff > len_mas) and (self.IndexM2 < len_mas-1):
                            self.IndexM2 = self.IndexM2 + 1
                        elif (Diff > len_mas / 2) and (self.IndexM2 < len_mas / 2):
                            self.IndexM2 = self.IndexM2 + 1
                        elif (Diff < len_mas) and (self.IndexM2 > 0):
                            self.IndexM2 = self.IndexM2 - 1
                    elif self.IndexM2:
                        self.IndexM2 = self.IndexM2 - 1
            else:
                # self.ImpulseM2_thread.join()
                if self.DirMotor2.value == 1:
                    self.DirMotor2.off()
                time.sleep(0.05)

    def __ImpulseM1(self):
        while self.ThreadMotionActive:
            self.ImpulseM1_event.wait()
            # print('Impulse 1')
            self.Motor1.on()
            time.sleep(self.DelayM1 / 3)
            self.Motor1.off()
            time.sleep(self.DelayM1 * 0.1)
            self.ImpulseM1_event.clear()

    def __ImpulseM2(self):
        while self.ThreadMotionActive:
            self.ImpulseM2_event.wait()
            # print('Impulse 2')
            self.Motor2.on()
            time.sleep(self.DelayM2 / 3)
            self.Motor2.off()
            time.sleep(self.DelayM2 * 0.1)
            self.ImpulseM2_event.clear()

    def motionMotor1(self, command):
        if abs(command) == 32000:
            self.RotateM1 = True
            self.NeedPositionMotor1 = self.PositionMotor1 + command
        elif self.RotateM1:
            self.RotateM1 = False
            self.NeedPositionMotor1 = self.PositionMotor1
            print(f'command {command} Position {self.PositionMotor1} NeedPosition {self.NeedPositionMotor1}')
        else:
            self.NeedPositionMotor1 = self.NeedPositionMotor1 + command

        if self.NeedPositionMotor1 < self.MinPositionM1:
            if not self.NoLimit:
                self.NeedPositionMotor1 = self.MinPositionM1
        elif self.NeedPositionMotor1 > self.MaxPositionM1:
            if not self.NoLimit:
                self.NeedPositionMotor1 = self.MaxPositionM1
        if command:
            print(f'command {command} Position {self.PositionMotor1} NeedPosition {self.NeedPositionMotor1}')
        self.__flagLastControl()

    def motionMotor2(self, command):
        if abs(command) == 32000:
            self.RotateM2 = True
            self.NeedPositionMotor2 = self.PositionMotor2 + command
        elif self.RotateM2:
            self.RotateM2 = False
            self.NeedPositionMotor2 = self.PositionMotor2
        else:
            self.NeedPositionMotor2 = self.NeedPositionMotor2 + command

        if self.NeedPositionMotor2 < self.MinPositionM2:
            if not self.NoLimit:
                self.NeedPositionMotor2 = self.MinPositionM2
        elif self.NeedPositionMotor2 > self.MaxPositionM2:
            if not self.NoLimit:
                self.NeedPositionMotor2 = self.MaxPositionM2
        
        if command:
            print(f'command {command} Position {self.PositionMotor2} NeedPosition {self.NeedPositionMotor2}')
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
        if param == self.MAX_POSITION_STEPPERS_1:
            self.config["MotionOption"]["MaxPositionM1"] = str(value)
            self.MaxPositionM1 = int(self.config["MotionOption"]["MaxPositionM1"])
            print(f"Max position motor 1 {self.MaxPositionM1}")
            ret = 1
        elif param == self.MAX_POSITION_STEPPERS_2:
            self.config["MotionOption"]["MaxPositionM2"] = str(value)
            self.MaxPositionM2 = int(self.config["MotionOption"]["MaxPositionM2"])
            print(f"Max position motor 2 {self.MaxPositionM2}")
            ret = 1
        elif param == self.MIN_POSITION_STEPPERS_1:
            self.config["MotionOption"]["MinPositionM1"] = str(value * (-1))
            self.MinPositionM1 = int(self.config["MotionOption"]["MinPositionM1"])
            print(f"Min position motor 1 {self.MinPositionM1}")
            ret = 1
        elif param == self.MIN_POSITION_STEPPERS_2:
            self.config["MotionOption"]["MinPositionM2"] = str(value * (-1))
            self.MinPositionM2 = int(self.config["MotionOption"]["MinPositionM2"])
            print(f"Min position motor 2 {self.MinPositionM2}")
            ret = 1
        elif param == self.FREQ_MOTOR_1:
            self.config["MotionOption"]["FreqM1"] = str(value)
            self.FreqM1 = int(self.config["MotionOption"]["FreqM1"])
            print(f"Freq motor 1 {self.FreqM1}")
            if self.FreqM1 == 0:
                self.FreqM1 = 1
            self.DelayM1 = 1.0 / float(self.FreqM1)
            if self.DelayM1 < 0.001:
                self.DelayM1 = 0.001
            self.__initDelayMas()
            print(f"Delay motor 1 {self.DelayM1}")
            ret = 1
        elif param == self.FREQ_MOTOR_2:
            self.config["MotionOption"]["FreqM2"] = str(value)
            self.FreqM2 = int(self.config["MotionOption"]["FreqM2"])
            print(f"Freq motor 2 {self.FreqM2}")
            if self.FreqM2 == 0:
                self.FreqM2 = 1
            self.DelayM2 = 1.0 / float(self.FreqM2)
            if self.DelayM2 < 0.001:
                self.DelayM2 = 0.001
            self.__initDelayMas()
            print(f"Delay motor 1 {self.DelayM2}")
            ret = 1

        if ret:
            self.SaveParameters_event.set()

        return ret

    def GetParam(self, param):
        if param == self.MAX_POSITION_STEPPERS_1:
            return self.MaxPositionM1
        elif param == self.MAX_POSITION_STEPPERS_2:
            return self.MaxPositionM2
        elif param == self.MIN_POSITION_STEPPERS_1:
            return self.MinPositionM1 * (-1)
        elif param == self.MIN_POSITION_STEPPERS_2:
            return self.MinPositionM2 * (-1)
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

    def __SaveParameters(self):
        while self.ThreadMotionActive:
            self.SaveParameters_event.wait()
            time.sleep(5)
            with open('MotorControl.ini', 'w') as configfile:
                self.config.write(configfile)
            self.SaveParameters_event.clear()

