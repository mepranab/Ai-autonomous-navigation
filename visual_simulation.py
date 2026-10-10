import random
import pygame
from ultralytics import YOLO

from simulation.environment import Environment
from path_planning import find_path
from src.metrics import NavigationMetrics


# ============================================================
# 1. INITIALIZE PYGAME
# ============================================================

pygame.init()

CELL_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 15

PANEL_WIDTH = 280

SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + PANEL_WIDTH
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Autonomous Navigation")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 18)
SMALL_FONT = pygame.font.SysFont("Arial", 15)
TITLE_FONT = pygame.font.SysFont("Arial", 23, bold=True)


# ============================================================
# 2. COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
BLUE = (40, 100, 240)
GREEN = (40, 200, 80)
YELLOW = (255, 220, 40)
RED = (230, 60, 60)
GRAY = (190, 190, 190)
LIGHT_GRAY = (235, 235, 235)
DARK_GRAY = (70, 70, 70)
ORANGE = (255, 150, 30)


# ============================================================
# 3. CREATE THE ENVIRONMENT
# ============================================================

environment = Environment()

start = (1, 1)
goal = (8, 6)

robot_position = start

path = find_path(environment, start, goal)

path_index = 0

steps_taken = 0
paused = False

status = "READY"
message = "Simulation started"

metrics = NavigationMetrics()

model = None

image_path = r"C:\Users\PRANAB\Downloads\image.png"

running = True

MOVE_DELAY = 500
last_move_time = 0


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def grid_to_pixel(position):
    """Convert a grid position to screen coordinates."""

    x, y = position

    return (
        x * CELL_SIZE,
        y * CELL_SIZE
    )


def draw_text(text, x, y, color=BLACK, font=FONT):
    """Draw text on the screen."""

    text_surface = font.render(str(text), True, color)

    screen.blit(text_surface, (x, y))


def recalculate_path():
    """Calculate a new route from the robot to the goal."""

    global path
    global path_index
    global status
    global message

    path = find_path(
        environment,
        robot_position,
        goal
    )

    path_index = 0

    metrics.record_replanning()

    metrics.update_environment(
    len(path) - 1 if path is not None else 0,
    len(environment.obstacles)
)

    if path is None:

        status = "NO PATH"

        message = "No route available!"

        print("No path found to the goal.")

    elif robot_position == goal:

        status = "DESTINATION REACHED"

        message = "Robot reached the goal!"

    else:

        status = "REPLANNING"

        message = "Route updated"

        print("New path calculated:", path)


def add_random_obstacles(number_to_add):
    """Add obstacles at randomly selected grid positions."""

    free_positions = []

    for y in range(GRID_HEIGHT):

        for x in range(GRID_WIDTH):

            position = (x, y)

            if position == robot_position:
                continue

            if position == goal:
                continue

            if position == start:
                continue

            if position in environment.obstacles:
                continue

            if not environment.is_inside(position):
                continue

            if not environment.is_walkable(position):
                continue

            distance_from_start = (
                abs(x - start[0]) +
                abs(y - start[1])
            )

            distance_from_goal = (
                abs(x - goal[0]) +
                abs(y - goal[1])
            )

            if distance_from_start < 3:
                continue

            if distance_from_goal < 3:
                continue

            free_positions.append(position)

    random.shuffle(free_positions)

    added = 0

    for position in free_positions:

        if added >= number_to_add:
            break

        environment.obstacles.add(position)

        added += 1

    return added


# ============================================================
# 5. MAIN SIMULATION LOOP
# ============================================================

while running:

    clock.tick(60)

    current_time = pygame.time.get_ticks()

    # --------------------------------------------------------
    # HANDLE KEYBOARD EVENTS
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # D KEY: DETECT OBJECTS USING YOLO
            # ------------------------------------------------

            if event.key == pygame.K_d:

                print("\nStarting YOLO object detection...")

                try:

                    # Load YOLO only when first needed.
                    if model is None:

                        print("Loading YOLO model...")

                        model = YOLO("yolo11n.pt")

                    # Run detection on the image.
                    results = model(image_path)

                    detected_classes = set()

                    obstacle_classes = {
                        "person",
                        "car",
                        "bicycle",
                        "motorcycle",
                        "bus",
                        "truck",
                        "dog",
                        "chair"
                    }

                    for result in results:

                        for box in result.boxes:

                            class_id = int(
                                box.cls[0].item()
                            )

                            class_name = result.names[class_id]

                            print(
                                "Detected object:",
                                class_name
                            )

                            if class_name in obstacle_classes:

                                detected_classes.add(class_name)

                    print(
                        "\nUnique obstacle-related classes:",
                        detected_classes
                    )

                    # Restart the robot if it already reached
                    # the destination.
                    if robot_position == goal:

                        robot_position = start

                        path_index = 0

                        steps_taken = 0

                    # Add demonstration obstacles.
                    number_to_add = len(detected_classes)

                    added = add_random_obstacles(
                        number_to_add
                    )

                    print(
                        "New demonstration obstacles added:",
                        added
                    )

                    # Calculate a new route.
                    recalculate_path()

                    if path is not None and robot_position != goal:

                        status = "REPLANNING"

                        message = "YOLO obstacles added"

                    print(
                        "Total obstacles:",
                        len(environment.obstacles)
                    )

                    print("Current route:", path)

                except Exception as error:

                    print(
                        "Object detection failed:",
                        error
                    )

                    status = "DETECTION ERROR"

                    message = "Check image path and model"

            # ------------------------------------------------
            # O KEY: ADD ONE MANUAL OBSTACLE
            # ------------------------------------------------

            elif event.key == pygame.K_o:

                candidates = [
                    (robot_position[0] + 1, robot_position[1]),
                    (robot_position[0] - 1, robot_position[1]),
                    (robot_position[0], robot_position[1] + 1),
                    (robot_position[0], robot_position[1] - 1)
                ]

                added_obstacle = False

                for position in candidates:

                    if not environment.is_inside(position):
                        continue

                    if position == robot_position:
                        continue

                    if position == goal:
                        continue

                    if position in environment.obstacles:
                        continue

                    environment.obstacles.add(position)

                    added_obstacle = True

                    print(
                        "Manual obstacle added at:",
                        position
                    )

                    break

                if added_obstacle:

                    recalculate_path()

                else:

                    message = "No suitable obstacle position"

            # ------------------------------------------------
            # R KEY: RESET THE SIMULATION
            # ------------------------------------------------

            elif event.key == pygame.K_r:

                environment = Environment()

                robot_position = start

                path = find_path(
                    environment,
                    start,
                    goal
                )

                path_index = 0

                steps_taken = 0

                paused = False

                status = "READY"

                message = "Simulation reset"

                metrics = NavigationMetrics()

                last_move_time = pygame.time.get_ticks()

                print("Simulation reset.")

            # ------------------------------------------------
            # SPACE KEY: PAUSE OR RESUME
            # ------------------------------------------------

            elif event.key == pygame.K_SPACE:

                paused = not paused

                if paused:

                    message = "Simulation paused"

                    print("Simulation paused.")

                else:

                    message = "Simulation resumed"

                    print("Simulation resumed.")


    # ========================================================
    # 6. MOVE THE ROBOT ALONG THE PATH
    # ========================================================

    if (
        not paused
        and path is not None
        and robot_position != goal
        and current_time - last_move_time >= MOVE_DELAY
    ):

        if path_index + 1 < len(path):

            next_position = path[path_index + 1]

            if (
                environment.is_inside(next_position)
                and environment.is_walkable(next_position)
            ):

                robot_position = next_position

                path_index += 1

                steps_taken += 1

                metrics.record_step()

                metrics.update_environment(
    len(path) - 1 if path is not None else 0,
    len(environment.obstacles)
)

                last_move_time = current_time

                print(
                    "Robot moved to:",
                    robot_position
                )

                if robot_position == goal:

                    status = "DESTINATION REACHED"

                    message = "Robot reached the goal!"

                    print(
                        "\nDestination reached successfully!"
                    )

            else:

                print(
                    "Next position blocked. Recalculating route..."
                )

                recalculate_path()

                last_move_time = current_time

        else:

            status = "NO PATH"

            message = "Route ended before goal"


    # ========================================================
    # 7. DRAW THE BACKGROUND
    # ========================================================

    screen.fill(WHITE)

    grid_pixel_width = GRID_WIDTH * CELL_SIZE

    grid_pixel_height = GRID_HEIGHT * CELL_SIZE


    # ========================================================
    # 8. DRAW THE GRID
    # ========================================================

    for x in range(GRID_WIDTH + 1):

        pygame.draw.line(
            screen,
            GRAY,
            (x * CELL_SIZE, 0),
            (x * CELL_SIZE, grid_pixel_height),
            1
        )

    for y in range(GRID_HEIGHT + 1):

        pygame.draw.line(
            screen,
            GRAY,
            (0, y * CELL_SIZE),
            (grid_pixel_width, y * CELL_SIZE),
            1
        )


    # ========================================================
    # 9. DRAW THE PLANNED PATH
    # ========================================================

    if path is not None and len(path) > 1:

        for i in range(len(path) - 1):

            current_cell = path[i]

            next_cell = path[i + 1]

            current_center = (
                current_cell[0] * CELL_SIZE + CELL_SIZE // 2,
                current_cell[1] * CELL_SIZE + CELL_SIZE // 2
            )

            next_center = (
                next_cell[0] * CELL_SIZE + CELL_SIZE // 2,
                next_cell[1] * CELL_SIZE + CELL_SIZE // 2
            )

            pygame.draw.line(
                screen,
                YELLOW,
                current_center,
                next_center,
                5
            )


    # ========================================================
    # 10. DRAW OBSTACLES
    # ========================================================

    for obstacle in environment.obstacles:

        x, y = grid_to_pixel(obstacle)

        pygame.draw.rect(
            screen,
            BLACK,
            (
                x + 3,
                y + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            )
        )


    # ========================================================
    # 11. DRAW THE GOAL
    # ========================================================

    goal_x, goal_y = grid_to_pixel(goal)

    pygame.draw.rect(
        screen,
        GREEN,
        (
            goal_x + 3,
            goal_y + 3,
            CELL_SIZE - 6,
            CELL_SIZE - 6
        )
    )

    goal_label = FONT.render(
        "G",
        True,
        WHITE
    )

    screen.blit(
        goal_label,
        (
            goal_x + CELL_SIZE // 2 - goal_label.get_width() // 2,
            goal_y + CELL_SIZE // 2 - goal_label.get_height() // 2
        )
    )


    # ========================================================
    # 12. DRAW THE ROBOT
    # ========================================================

    robot_x, robot_y = grid_to_pixel(robot_position)

    pygame.draw.circle(
        screen,
        BLUE,
        (
            robot_x + CELL_SIZE // 2,
            robot_y + CELL_SIZE // 2
        ),
        CELL_SIZE // 2 - 5
    )

    robot_label = FONT.render(
        "R",
        True,
        WHITE
    )

    screen.blit(
        robot_label,
        (
            robot_x + CELL_SIZE // 2 - robot_label.get_width() // 2,
            robot_y + CELL_SIZE // 2 - robot_label.get_height() // 2
        )
    )


    # ========================================================
    # 13. DRAW THE INFORMATION PANEL
    # ========================================================

    panel_x = grid_pixel_width

    pygame.draw.rect(
        screen,
        LIGHT_GRAY,
        (
            panel_x,
            0,
            PANEL_WIDTH,
            SCREEN_HEIGHT
        )
    )

    pygame.draw.line(
        screen,
        DARK_GRAY,
        (panel_x, 0),
        (panel_x, SCREEN_HEIGHT),
        2
    )

    text_x = panel_x + 15

    y = 15

    draw_text(
        "AI NAVIGATION",
        text_x,
        y,
        BLUE,
        TITLE_FONT
    )

    y += 45

    pygame.draw.line(
        screen,
        GRAY,
        (text_x, y),
        (SCREEN_WIDTH - 15, y),
        1
    )

    y += 15

    draw_text("Robot Position:", text_x, y, BLACK, SMALL_FONT)

    y += 23

    draw_text(
        str(robot_position),
        text_x,
        y,
        BLUE,
        FONT
    )

    y += 35

    draw_text("Goal Position:", text_x, y, BLACK, SMALL_FONT)

    y += 23

    draw_text(
        str(goal),
        text_x,
        y,
        GREEN,
        FONT
    )

    y += 35

    draw_text("Steps Taken:", text_x, y, BLACK, SMALL_FONT)

    y += 23

    draw_text(
        steps_taken,
        text_x,
        y,
        BLACK,
        FONT
    )

    y += 35

    draw_text("Total Obstacles:", text_x, y, BLACK, SMALL_FONT)

    y += 23

    draw_text(
        len(environment.obstacles),
        text_x,
        y,
        RED,
        FONT
    )

    y += 35

    draw_text("Route Length:", text_x, y, BLACK, SMALL_FONT)

    y += 23

    if path is not None:

        remaining_steps = max(
            0,
            len(path) - 1 - path_index
        )

        draw_text(
            remaining_steps,
            text_x,
            y,
            BLACK,
            FONT
        )

    else:

        draw_text(
            "Unavailable",
            text_x,
            y,
            RED,
            SMALL_FONT
        )

    y += 35

    draw_text("Status:", text_x, y, BLACK, SMALL_FONT)

    y += 23

    status_color = BLUE

    if status == "NO PATH":

        status_color = RED

    elif status == "DESTINATION REACHED":

        status_color = GREEN

    draw_text(
        status,
        text_x,
        y,
        status_color,
        SMALL_FONT
    )

    y += 30

    draw_text(
        message,
        text_x,
        y,
        DARK_GRAY,
        SMALL_FONT
    )

    y += 40

    pygame.draw.line(
        screen,
        GRAY,
        (text_x, y),
        (SCREEN_WIDTH - 15, y),
        1
    )

    y += 15

    draw_text(
        "CONTROLS",
        text_x,
        y,
        BLACK,
        FONT
    )

    y += 30

    draw_text("D - Detect objects", text_x, y, BLACK, SMALL_FONT)

    y += 25

    draw_text("O - Add obstacle", text_x, y, BLACK, SMALL_FONT)

    y += 25

    draw_text("R - Reset simulation", text_x, y, BLACK, SMALL_FONT)

    y += 25

    draw_text("SPACE - Pause/Resume", text_x, y, BLACK, SMALL_FONT)

    y += 35

    if paused:

        draw_text(
            "PAUSED",
            text_x,
            y,
            RED,
            FONT
        )


    # ========================================================
    # 14. UPDATE THE DISPLAY
    # ========================================================

    pygame.display.flip()


# ============================================================
# 15. CLOSE PYGAME
# ============================================================

pygame.quit()

print("Simulation closed.")
