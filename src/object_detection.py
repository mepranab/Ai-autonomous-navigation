from ultralytics import YOLO
import cv2
from pathlib import Path


def detect_objects(image_path):
    """Detect objects in an image using a pretrained YOLO model."""

    if not Path(image_path).exists():
        print(f"Error: Image not found: {image_path}")
        return

    # Load a pretrained YOLO model
    model = YOLO("yolo11n.pt")

    # Detect objects in the image
    results = model(image_path)

    # Display the detection results
    for result in results:
        annotated_image = result.plot()

        cv2.imshow("AI Object Detection", annotated_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    print("AI Object Detection System")
    image_path = input("Enter the full path of an image: ")
    detect_objects(image_path)