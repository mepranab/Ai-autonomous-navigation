import csv
from pathlib import Path


class NavigationMetrics:
    def __init__(self):
        self.steps_taken = 0
        self.collision_attempts = 0
        self.replanning_count = 0
        self.navigation_success = False
        self.path_length = 0
        self.obstacle_count = 0

    def record_step(self):
        self.steps_taken += 1

    def record_collision(self):
        self.collision_attempts += 1

    def record_replanning(self):
        self.replanning_count += 1

    def set_navigation_result(self, success):
        self.navigation_success = success

    def update_environment(self, path_length, obstacle_count):
        self.path_length = path_length
        self.obstacle_count = obstacle_count

    def display(self):
        print("\n===== NAVIGATION PERFORMANCE =====")
        print("Steps taken:", self.steps_taken)
        print("Path length:", self.path_length)
        print("Obstacle count:", self.obstacle_count)
        print("Collision attempts:", self.collision_attempts)
        print("Replanning count:", self.replanning_count)
        print("Navigation successful:", self.navigation_success)
        print("==================================")

    def save_to_csv(self, filename="outputs/metrics/navigation_metrics.csv"):
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = output_path.exists()

        with output_path.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            fieldnames = [
                "steps_taken",
                "collision_attempts",
                "replanning_count",
                "navigation_success",
                "path_length",
                "obstacle_count",
            ]

            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(
                {
                    "steps_taken": self.steps_taken,
                    "collision_attempts": self.collision_attempts,
                    "replanning_count": self.replanning_count,
                    "navigation_success": self.navigation_success,
                    "path_length": self.path_length,
                    "obstacle_count": self.obstacle_count,
                }
            )

        print("Metrics saved to:", output_path)
        