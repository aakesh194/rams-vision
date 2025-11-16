import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Simple binary threshold for obstacle detection
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)

    # Find contours on thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    obstacle = False  # Initialize

    for c in contours:
        if cv2.contourArea(c) > 3000:   # Adjust if too sensitive
            obstacle = True
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 3)

    text = "OBSTACLE!" if obstacle else "CLEAR"
    cv2.putText(frame, text, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255,0,0), 3)

    cv2.imshow("Obstacle Detection", frame)
    cv2.imshow("Mask", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
