import cv2
from ultralytics import YOLO


def main():
    print("Loading YOLO model...")
    model = YOLO("yolo11s.pt")

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not open webcam.")
        return

    print("Live obstacle detection started.")
    print("Press Q to quit.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Unable to read camera frame.")
                break

            height, width = frame.shape[:2]

            # Define the center region of the camera image.
            center_left = width // 3
            center_right = 2 * width // 3

            results = model.predict(
                source=frame,
                conf=0.40,
                verbose=False
            )

            result = results[0]
            annotated_frame = frame.copy()

            # Draw left, center, and right region boundaries.
            cv2.line(
                annotated_frame,
                (center_left, 0),
                (center_left, height),
                (255, 255, 0),
                2
            )

            cv2.line(
                annotated_frame,
                (center_right, 0),
                (center_right, height),
                (255, 255, 0),
                2
            )

            center_obstacles = 0
            total_detections = 0

            if result.boxes is not None:
                for box in result.boxes:
                    confidence = float(box.conf[0])

                    if confidence < 0.40:
                        continue

                    class_id = int(box.cls[0])
                    object_name = model.names[class_id]

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0].tolist()
                    )

                    object_center_x = (x1 + x2) // 2

                    total_detections += 1

                    # Check whether the object center is in the middle third.
                    is_center = (
                        center_left <= object_center_x <= center_right
                    )

                    if is_center:
                        center_obstacles += 1
                        color = (0, 0, 255)
                        label = f"AHEAD: {object_name} {confidence:.2f}"
                    else:
                        color = (0, 255, 0)
                        label = f"{object_name} {confidence:.2f}"

                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        color,
                        2
                    )

                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        color,
                        2
                    )

            if center_obstacles > 0:
                status = f"WARNING: {center_obstacles} object(s) ahead"
                status_color = (0, 0, 255)
            else:
                status = "No detected objects in center region"
                status_color = (0, 255, 0)

            cv2.putText(
                annotated_frame,
                status,
                (15, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                status_color,
                2
            )

            cv2.putText(
                annotated_frame,
                f"Total detections: {total_detections}",
                (15, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "AI Navigation - Camera Obstacle Detection",
                annotated_frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Camera released.")


if __name__ == "__main__":
    main()