import cv2

cap = cv2.VideoCapture(0)
bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Background subtraction
    mask = bg.apply(gray)

    # Reduce noise
    mask = cv2.medianBlur(mask, 5)

    # Find contours (areas of movement)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_detected = False

    for c in contours:
        if cv2.contourArea(c) > 2000:  # Threshold size
            motion_detected = True
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    status = "MOTION" if motion_detected else "CLEAR"
    cv2.putText(frame, status, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0,0,255), 3)

    # Display windows
    cv2.imshow("Camera", frame)
    cv2.imshow("Mask", mask)

    # ← THIS IS THE KEY PART
    key = cv2.waitKey(1) & 0xFF  # 1ms delay, allows GUI to refresh
    if key == ord('q'):          # Press 'q' to quit
        break

# Release resources cleanly
cap.release()
cv2.destroyAllWindows()
