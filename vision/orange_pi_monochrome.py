# test ts using: pip install opencv-python numpy
# python orange_pi_monochrome.py


#Threshold: 60
#Area: 125000

import cv2
import socket
import time
from collections import deque
import numpy as np

# -------- TCP Setup to Raspberry Pi --------
RPI_IP = '192.168.1.100'
RPI_PORT = 5005
RECONNECT_DELAY = 5

def connect_to_pi():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((RPI_IP, RPI_PORT))
            print("Connected to Raspberry Pi")
            return s
        except Exception as e:
            print("Failed to connect, retrying in", RECONNECT_DELAY, "s")
            time.sleep(RECONNECT_DELAY)

# Uncomment to enable TCP
# s = connect_to_pi()

def send_command(cmd):
    global s
    try:
        s.sendall(f"{cmd}\n".encode())
    except Exception as e:
        print("Connection lost, reconnecting...")
        s.close()
        s = connect_to_pi()

# -------- Camera Setup --------
cap = cv2.VideoCapture(0)
SMOOTH_FRAMES = 3
frame_queue = deque(maxlen=SMOOTH_FRAMES)

# -------- Trackbars for live tuning --------
cv2.namedWindow("Camera Feed")
cv2.createTrackbar("Threshold", "Camera Feed", 60, 255, lambda x: None)
# Default tuned for ~3ft
cv2.createTrackbar("Area", "Camera Feed", 20000, 200000, lambda x: None)


# -------- Main Loop --------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected")
        break

    gray = frame if len(frame.shape) == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Contrast boost
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(blur)

    # Get live values from trackbars
    thresh_val = cv2.getTrackbarPos("Threshold", "Camera Feed")
    area_thresh = cv2.getTrackbarPos("Area", "Camera Feed")

    # Thresholding
    _, thresh = cv2.threshold(enhanced, thresh_val, 255, cv2.THRESH_BINARY_INV)

    # Morphology cleanup
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Contour detection
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacle_detected = False
    max_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        x, y, w, h_c = cv2.boundingRect(c)

        if area > area_thresh and h_c > 40:
            obstacle_detected = True
            cv2.rectangle(frame, (x, y), (x + w, y + h_c), (0,255,0), 2)

        if area > max_area:
            max_area = area

    # Smooth detection
    frame_queue.append(obstacle_detected)
    if frame_queue.count(True) >= (SMOOTH_FRAMES // 2 + 1):
        command = "STOP"
    else:
        command = "GO"

    # send_command(command)

    # Debug overlays
    cv2.putText(frame, f"{command} (MaxArea={int(max_area)})", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Threshold Mask", thresh)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
