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
        except:
            print("Failed to connect, retrying in", RECONNECT_DELAY, "s")
            time.sleep(RECONNECT_DELAY)

# s = connect_to_pi()

def send_command(cmd):
    global s
    try:
        s.sendall(f"{cmd}\n".encode())
    except:
        print("Connection lost, reconnecting...")
        s.close()
        s = connect_to_pi()

# -------- Camera Setup --------
cap = cv2.VideoCapture(0)
ROI_RATIO = 0.35
OBSTACLE_THRESHOLD = 3000
SMOOTH_FRAMES = 3
frame_queue = deque(maxlen=SMOOTH_FRAMES)

# -------- Improved Threshold Function --------
def get_clean_mask(gray_roi):
    # Normalize lighting
    norm = cv2.normalize(gray_roi, None, 0, 255, cv2.NORM_MINMAX)

    # Blur to remove tiny noise
    blur = cv2.GaussianBlur(norm, (7,7), 0)

    # Adaptive Threshold (better than Otsu in real life)
    mask = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 31, 7
    )

    # Morphological cleanup
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # remove noise dots
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # remove holes

    return mask

# -------- Main Loop --------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Region of interest (bottom of frame)
    h = gray.shape[0]
    roi = gray[int(h*(1-ROI_RATIO)):, :]

    # Apply improved mask
    thresh = get_clean_mask(roi)

    # Find objects using contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacle_detected = False
    max_area = 0

    for c in contours:
        area = cv2.contourArea(c)
        x, y, w, h_c = cv2.boundingRect(c)
        aspect_ratio = w / (h_c + 1e-5)

        if area > OBSTACLE_THRESHOLD and 0.2 < aspect_ratio < 5.0:
            obstacle_detected = True
            cv2.rectangle(frame,
                (x, y + int(h*(1-ROI_RATIO))),
                (x+w, y+h_c + int(h*(1-ROI_RATIO))),
                (0,255,0), 2
            )
        max_area = max(max_area, area)

    frame_queue.append(obstacle_detected)
    command = "STOP" if frame_queue.count(True) >= 2 else "GO"

    # Debug text
    cv2.putText(frame, f"{command} (Area={int(max_area)})",
                (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Threshold Mask", thresh)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
# s.close()
