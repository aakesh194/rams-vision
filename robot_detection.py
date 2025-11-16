import cv2

cap = cv2.VideoCapture(0)
obstacle_area_threshold = 3000

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)

    # Region of interest: bottom half only
    height = thresh.shape[0]
    roi = thresh[height//2: , :]

    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacle_detected = False
    for c in contours:
        if cv2.contourArea(c) > obstacle_area_threshold:
            obstacle_detected = True
            x, y, w, h = cv2.boundingRect(c)
            # Offset y by roi start
            cv2.rectangle(frame, (x, y + height//2), (x+w, y+h + height//2), (0,255,0), 3)

    # Output commands for robot
    if obstacle_detected:
        print("STOP")
    else:
        print("GO")

    cv2.imshow("Robot Camera Feed", frame)
    cv2.imshow("Mask", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
