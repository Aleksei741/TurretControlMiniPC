import socket
import select
from CameraStream import CameraStream
from VibrationSensor import hit_sensor
from MotorControl import motor_control

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 20101  # Port to listen on (non-privileged ports are > 1023)

video = CameraStream()
turret = motor_control(18, 17, 23, 22, 12, 6)
sensor = hit_sensor(27)

def command_parse(data):
    if data[:2] != b'\x54\x43':
        return 0

    # video
    if data[2] == ord(b'\x56'):
        # param
        if data[3] == ord(b'\x50'):
            video.SetParam(data[4], int.from_bytes(data[5:9], "little", signed=False)) # "little"
            return 1

        # start/stop
        if data[3] == ord(b'\x53'):
            if data[4] == ord(b'\x01'):
                video.startTranslation()
                return 1
            elif data[4] == ord(b'\x00'):
                video.stopTranslation()
                return 1



    # control command
    if data[2] == ord(b'\x43'):
        command = int.from_bytes(data[3:5], "little", signed=True)
        # print(f'Motor1 {command}')
        turret.motionMotor1(command)
        command = int.from_bytes(data[5:7], "little", signed=True)
        # print(f'Motor2 {command}')
        turret.motionMotor2(command)
        command = int(data[7])
        turret.motionTrigger(command)
        return 1

    return 0

def ResponseFill():
    data = list()
    
    data.append(ord(b'\x54')) # ('T')
    data.append(ord(b'\x43')) # ('C')
    
    # Video status
    data.append(video.GetStatusVideo())
    
    # Sensor cnt
    data.append(sensor.GetCntSensor())
    
    # reserv
    data.append(0)
    data.append(0)
    data.append(0)
    data.append(0)
    data.append(0)
    data.append(0)
    
    data.append(ord(b'\xA5'))
    data.append(ord(b'\xA5'))
    
    return bytes(data)


while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)

        print(f"listen")
        conn, addr = s.accept()
        print(f"accept")

        video.SetParam(video.IP, addr[0])

        with conn:
            conn.setblocking(0)
            print(f"Connected by {addr}")
            while True:
                ready = select.select([conn], [], [], 1)

                if ready[0]:
                    data = conn.recv(12)
                    if not data:
                        break

                    if command_parse(data) == 0:
                        break
                        
                    ResponseData = ResponseFill()
                    conn.sendall(ResponseData)
                else:
                    break
