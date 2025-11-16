# robot_client.py (Raspberry Pi)
import socket

HOST = ''   # Listen on all interfaces
PORT = 5005

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

print("Waiting for Orange Pi...")
conn, addr = s.accept()
print("Connected by", addr)

while True:
    data = conn.recv(1024)
    if not data:
        break
    command = data.decode().strip()
    if command == 'STOP':
        print("Robot stopping!")
        # TODO: integrate motor stop
    elif command == 'GO':
        print("Robot moving forward!")
        # TODO: integrate waypoint navigation

conn.close()
