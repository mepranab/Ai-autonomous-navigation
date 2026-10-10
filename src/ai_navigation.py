from ultralytics import YOLO
from simulation.environment import Environment


def detect_obstacles(image_path):
    """Detect objects and demonstrate adding obstacles to the grid."""

    # Create the simulation environment
    environment = Environment()

    # Load the pretrained YOLO model
    model = YOLO("yolo11n.pt")

    # Detect objects in the image
    results = model(image_path)

    detected_objects = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            object_name = model.names[class_id]
            detected_objects.append(object_name)

    print("\n===== AI NAVIGATION REPORT =====")
    print("Image:", image_path)
    print("Detected objects:", detected_objects)

    # Objects that may need attention during navigation
    potential_obstacles = {
        "person",
        "car",
        "bicycle",
        "motorcycle",
        "bus",
        "truck",
        "dog",
        "chair",
    }

    obstacles_found = [
        obj for obj in detected_objects
        if obj in potential_obstacles
    ]

    print("\nPotential obstacles:", obstacles_found)

    # Demonstration only: assign grid positions to detected objects.
    # These positions are NOT calculated from the image.
    demonstration_positions = [
        (7, 6),
        (8, 6),
        (9, 6),
        (7, 7),
        (8, 7),
    ]

    added_count = 0

    if obstacles_found:
        for index, object_name in enumerate(obstacles_found):
            position = demonstration_positions[
                index % len(demonstration_positions)
            ]

            if environment.add_obstacle(position):
                added_count += 1
                print(
                    f"Added demonstration obstacle for "
                    f"{object_name} at grid position {position}"
                )

        print("\nNavigation decision: Recheck the route.")
    else:
        print("No listed obstacles detected.")
        print("Navigation decision: Continue checking the path.")

    print("Original obstacles:", 5)
    print("Total obstacles in environment:", len(environment.obstacles))
    print("New obstacles added:", added_count)
    print("================================")


if __name__ == "__main__":
    image_path = input(
        "Enter the full path of an image: "
    ).strip().strip('"')

    detect_obstacles(image_path)
    