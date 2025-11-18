import cv2
import numpy as np
from collections import deque

cap = cv2.VideoCapture(2)

ROI_TOP_RATIO = 0.45      # previously 0.65 bottom-only view
OBSTACLE_MIN_AREA = 800   # detect smaller objects
OBSTACLE_MAX_AREA = 90000 # allow very large close objects
SMOOTH_FRAMES = 4
frame_queue = deque(maxlen=SMOOTH_FRAMES)

def adaptive_binary(frame):
    frame = cv2.equalizeHist(frame)
    thr = cv2.adaptiveThreshold(frame, 255,
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV,
                                31, 7)
    # morphology
    kernel = np.ones((7,7), np.uint8)
    thr = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel, iterations=2)
    return thr

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected")
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    
    h = blur.shape[0]
    roi = blur[int(h * ROI_TOP_RATIO):, :]      # lower half instead of last 35%
    
    thresh = adaptive_binary(roi)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    obstacle = False
    max_area = 0

    offset_y = int(h * ROI_TOP_RATIO)

    for c in contours:
        area = cv2.contourArea(c)
        if OBSTACLE_MIN_AREA < area < OBSTACLE_MAX_AREA:
            obstacle = True
            
            x,y,w,hc = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y + offset_y), (x+w, y+hc + offset_y), (0,255,0), 2)

        if area > max_area:
            max_area = area

    frame_queue.append(obstacle)
    cmd = "STOP" if frame_queue.count(True) >= (SMOOTH_FRAMES // 2 + 1) else "GO"

    cv2.putText(frame, f"{cmd}  Area={max_area}", (20,40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0,0,255), 3)

    cv2.imshow("Feed", frame)
    cv2.imshow("Mask", thresh)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
