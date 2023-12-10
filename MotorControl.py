import time
from gpiozero import OutputDevice, LED
import threading


class motor_control():

    def __init__(self, StepPin, Motor1, DirMotor1, Motor2, DirMotor2, Trigger, Magazine):
        self.StepPin = OutputDevice(StepPin)
        self.Motor1 = OutputDevice(Motor1)
        self.DirMotor1 = OutputDevice(DirMotor1)
        self.Motor2 = OutputDevice(Motor2)
        self.DirMotor2 = OutputDevice(DirMotor2)
        self.Trigger = OutputDevice(Trigger)
        self.Magazine = OutputDevice(Magazine)
        self.timeLastControl = time.time()

        self.watch_dog_thread = threading.Thread(target=self.__watch_dog)
        self.watch_dog_active = True
        self.watch_dog_thread.start()


    def __del__(self):
        self.watch_dog_active = False
        self.Motor1.off()
        self.DirMotor1.off()
        self.Motor2.off()
        self.DirMotor2.off()
        self.Trigger.off()
        self.watch_dog_thread.join()

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
        self.__motionMotor(command, self.Motor1)
        self.__flagLastControl()

    def motionMotor2(self, command):
        self.__motionMotor(command, self.Motor2)
        self.__flagLastControl()

    def __motionMotor(self, command, motor):
        if command < 0:
            self.rotate_counterclockwise(self.DirMotor1)
            if motor.value == 0:
                motor.on()
        elif command > 0:
            self.rotate_clockwise(self.DirMotor1)
            if motor.value == 0:
                motor.on()
        else:
            if motor.value == 1:
                motor.off()
                
        self.__StepPinControl()
    
    def __StepPinControl(self):
        if self.Motor1.value == 1 or self.Motor2.value == 1:
            if self.StepPin.value == 0:
                self.StepPin.on()
        elif self.StepPin.value == 1:
            self.StepPin.off()

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
        self.motionMotor1(0)
        self.motionMotor2(0)
        self.motionTrigger(0)

    def __watch_dog(self):
        while(self.watch_dog_active):
            if time.time() - self.timeLastControl > 0.25:
                self.motionAllOff()
            time.sleep(0.05)


