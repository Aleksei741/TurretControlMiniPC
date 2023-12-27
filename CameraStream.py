import time
import threading
import subprocess
import os, signal

class CameraStream():

    def __init__(self):
        self.HEIGHT = ord(b'\x48')
        self.WEIGHT = ord(b'\x57')
        self.BITRATE = ord(b'\x42')
        self.FRAMERATE = ord(b'\x46')
        self.IP = ord(b'\x49')
        self.PORT = ord(b'\x50')

        self.height = 1080
        self.weight = 720
        self.bitrate = 5000
        self.framerate = 25
        self.ip = "localhost"
        self.port = 20100
        self.proc = None


    def startTranslation(self):
        if(self.proc):
            p = self.proc.poll()
            if p is None:
                os.kill(self.proc.pid, signal.SIGINT)
                self.proc.wait()
    
        self.proc = subprocess.Popen(["ffmpeg", "-re",
                                      "-f", "v4l2",
                                      "-i", "/dev/video0",
                                      "-preset", "ultrafast",
                                      "-framerate", f"{self.framerate}",
                                      "-vcodec", "libx264",
                                      "-s:v", f"{self.height}x{self.weight}",
                                      "-b:v", f"{self.bitrate}K",
                                      "-tune", "zerolatency",
                                      "-f", "rtp",
                                      f"rtp://{self.ip}:{self.port}"])

    def stopTranslation(self):
        if(self.proc):
            p = self.proc.poll()
            if p is None:
                os.kill(self.proc.pid, signal.SIGINT)
                self.proc.wait()

    def SetParam(self, param, value):
        ret = 0
        if param == self.HEIGHT:
            print(f"height {value}")
            self.height = value
            ret = 1
        elif param == self.WEIGHT:
            print(f"weight {value}")
            self.weight = value
            ret = 1
        elif param == self.BITRATE:
            print(f"bitrate {value}")
            self.bitrate = value
            ret = 1
        elif param == self.FRAMERATE:
            print(f"framerate {value}")
            self.framerate = value
            ret = 1
        elif param == self.IP:
            # print(f"ip {value}")
            self.ip = value
            ret = 1
        elif param == self.PORT:
            print(f"port {value}")
            self.port = value
            ret = 1
        return ret

    def GetParam(self, param):
        if param == self.HEIGHT:
            return self.height
        elif param == self.WEIGHT:
            return self.weight
        elif param == self.BITRATE:
            return self.bitrate
        elif param == self.FRAMERATE:
            return self.framerate
        elif param == self.IP:
            return self.ip
        elif param == self.PORT:
            return self.port
            
    def GetStatusVideo(self):
        if(self.proc):
            p = self.proc.poll()
            if p is None:
                return True
        return False
