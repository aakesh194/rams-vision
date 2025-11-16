# orange_pi_test_debug.py
import cv2

cap = cv2.VideoCapture(0)
OBSTACLE_THRESHOLD = 3000  # adjust for your setup
ROI_RATIO = 0.5            # bottom half

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected")
        break

    gray = frame if len(frame.shape) == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    h = blur.shape[0]
    roi = blur[int(h*ROI_RATIO):, :]

    # Threshold
    _, thresh = cv2.threshold(roi, 100, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacle_detected = False
    for c in contours:
        area = cv2.contourArea(c)
        print("Contour area:", area)  # debug output
        if area > OBSTACLE_THRESHOLD:
            obstacle_detected = True
            x, y, w, h_c = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y + int(h*ROI_RATIO)), (x+w, y+h_c + int(h*ROI_RATIO)), (0,255,0), 2)

    command = "STOP" if obstacle_detected else "GO"
    print("Command:", command)

    cv2.putText(frame, command, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
    cv2.imshow("Camera Feed", frame)
    cv2.imshow("Threshold Mask", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
