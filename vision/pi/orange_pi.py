# Orange Pi side: send frame
import cv2
import socket
import pickle
import struct

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('RPI_IP', 8000))

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    data = pickle.dumps(frame)
    client_socket.sendall(struct.pack(">L", len(data)) + data)
