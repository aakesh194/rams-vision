import cv2
import socket
import time
from collections import deque
import numpy as np

# -------- TCP Setup to Raspberry Pi --------
RPI_IP = '192.168.1.100'  # Raspberry Pi IP
RPI_PORT = 5005
RECONNECT_DELAY = 5        # seconds

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

#s = connect_to_pi()

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
ROI_RATIO = 0.35
OBSTACLE_THRESHOLD = 3000
SMOOTH_FRAMES = 3
frame_queue = deque(maxlen=SMOOTH_FRAMES)

# -------- Threshold Helper --------
def auto_threshold(frame):
    # Use Otsu; fallback to fixed threshold if needed
    try:
        _, thresh = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return thresh
    except:
        return cv2.threshold(frame, 80, 255, cv2.THRESH_BINARY_INV)[1]

# -------- Main Loop --------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected")
        break

    gray = frame if len(frame.shape) == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    h = blur.shape[0]
    roi = blur[int(h*(1-ROI_RATIO)):, :]

    thresh = auto_threshold(roi)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacle_detected = False
    max_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        x, y, w, h_c = cv2.boundingRect(c)
        aspect_ratio = w / (h_c + 1e-5)

        if area > OBSTACLE_THRESHOLD and 0.2 < aspect_ratio < 5.0:
            obstacle_detected = True
            # Draw rectangle at correct position
            cv2.rectangle(frame, (x, y + int(h*(1-ROI_RATIO))),
                                 (x + w, y + h_c + int(h*(1-ROI_RATIO))), (0,255,0), 2)
        if area > max_area:
            max_area = area

    # Smooth detection over multiple frames
    frame_queue.append(obstacle_detected)
    if frame_queue.count(True) >= (SMOOTH_FRAMES // 2 + 1):
        command = "STOP"
    else:
        command = "GO"

    #send_command(command)

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
s.close()
