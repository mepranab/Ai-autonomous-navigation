import cv2

print("Starting camera test...")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open the camera.")
    print("Check that your webcam is connected and not being used by another app.")
    raise SystemExit(1)

print("Camera opened successfully.")
print("Press Q to close the camera window.")

while True:
    success, frame = camera.read()

    if not success:
        print("ERROR: Could not read a camera frame.")
        break

    cv2.imshow("Live Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("Camera test finished.")