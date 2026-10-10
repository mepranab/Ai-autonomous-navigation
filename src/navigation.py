from simulation.robot import Robot
from simulation.environment import Environment
from path_planning import find_path


def run_navigation():
    environment = Environment()

    robot = Robot((1, 1))
    goal = (8, 6)

    print("Autonomous Navigation Started!")
    print("Starting position:", robot.position)
    print("Destination:", goal)

    path = find_path(environment, robot.position, goal)

    if path is None:
        print("No valid path found!")
        return

    print("\nPath found!")
    print("Path:", path)

    for next_position in path[1:]:
        moved = robot.move_to(next_position, environment)

        if not moved:
            print("Movement failed at:", next_position)
            return

        print("Robot moved to:", robot.position)

    print("\nDestination reached!")
    print("Total steps:", robot.steps_taken)
    print("Collision attempts:", robot.collision_count)


if __name__ == "__main__":
    run_navigation()