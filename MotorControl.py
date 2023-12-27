import time
from gpiozero import PWMOutputDevice, OutputDevice, LED
import threading


class motor_control():

    def __init__(self, Motor1, DirMotor1, Motor2, DirMotor2, Trigger, Magazine):
        # self.Motor1 = OutputDevice(Motor1)
        self.Motor1 = PWMOutputDevice(Motor1)
        self.DirMotor1 = OutputDevice(DirMotor1)
        # self.Motor2 = OutputDevice(Motor2)
        self.Motor2 = PWMOutputDevice(Motor2)
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
        if command < 0:
            self.rotate_counterclockwise(self.DirMotor1)
        elif command > 0:
            self.rotate_clockwise(self.DirMotor1)
            
        # print(f'Motor1 {command}')
        self.__motionMotor(command, self.Motor1)
        self.__flagLastControl()

    def motionMotor2(self, command):
        if command < 0:
            self.rotate_counterclockwise(self.DirMotor2)
        elif command > 0:
            self.rotate_clockwise(self.DirMotor2)
            
        # print(f'Motor2 {command}')
        self.__motionMotor(command, self.Motor2)
        self.__flagLastControl()

    def __motionMotor(self, command, motor):
        if command != 0:
            command = abs(command)
            if motor.frequency != command:
                motor.frequency = command
            if motor.value == 0:
                motor.value = 0.5
                # motor.on()
        else:
            if motor.value != 0:
                motor.value = 0
                # motor.off()
                
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


