import socket
import select
from CameraStream import CameraStream
from MotorControl import motor_control

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 20101  # Port to listen on (non-privileged ports are > 1023)

video = CameraStream()
turret = motor_control(27, 18, 17, 23, 22, 12, 6)

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
        command = int.from_bytes(data[3:5], "little", signed=False)
        turret.motionMotor1(command)
        command = int.from_bytes(data[5:7], "little", signed=False)
        turret.motionMotor2(command)
        command = int(data[7])
        turret.motionTrigger(command)
        return 1

    return 0




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
                else:
                    break