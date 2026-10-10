"""Advanced CPU-friendly Pygame navigation demo.

Uses the project's existing Environment, find_path and NavigationMetrics APIs.
Controls: O add obstacle, D run YOLO on configured image, C toggle clearance
visualization, R reset, SPACE pause/resume, Q or window close to quit.
"""
import random
import time
import pygame
from ultralytics import YOLO

from simulation.environment import Environment
from path_planning import find_path
from src.metrics import NavigationMetrics

# ----------------------------- Configuration -----------------------------
CELL_SIZE = 36
GRID_WIDTH = 20
GRID_HEIGHT = 15
GRID_PIXEL_WIDTH = GRID_WIDTH * CELL_SIZE
GRID_PIXEL_HEIGHT = GRID_HEIGHT * CELL_SIZE
PANEL_WIDTH = 320
SCREEN_WIDTH = GRID_PIXEL_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = max(GRID_PIXEL_HEIGHT, 640)
MOVE_DELAY_MS = 420
CLEARANCE_RADIUS = 1
IMAGE_PATH = r"C:\Users\PRANAB\Downloads\image.png"

# Palette
BG = (19, 25, 38)
GRID_BG = (28, 36, 51)
GRID_LINE = (56, 67, 86)
PANEL_BG = (235, 240, 247)
TEXT = (32, 42, 58)
MUTED = (91, 105, 126)
BLUE = (50, 115, 235)
GREEN = (35, 165, 100)
YELLOW = (246, 194, 66)
RED = (213, 70, 78)
OBSTACLE = (39, 47, 62)
CLEARANCE = (246, 170, 64)
WHITE = (255, 255, 255)
CYAN = (42, 158, 184)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Autonomous Navigation | Advanced Simulation")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 17)
SMALL = pygame.font.SysFont("Arial", 14)
TINY = pygame.font.SysFont("Arial", 12)
TITLE = pygame.font.SysFont("Arial", 22, bold=True)

# ------------------------------- State -----------------------------------
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
running = True
show_clearance = True
replanning_count = 0
start_clock = time.monotonic()
last_move_time = pygame.time.get_ticks()


def grid_to_pixel(position):
    x, y = position
    return x * CELL_SIZE, y * CELL_SIZE


def draw_text(text, x, y, color=TEXT, font=FONT):
    surface = font.render(str(text), True, color)
    screen.blit(surface, (x, y))
    return surface.get_height()


def clearance_cells():
    """Return walkable cells within the configured Chebyshev radius of obstacles."""
    cells = set()
    for ox, oy in environment.obstacles:
        for dy in range(-CLEARANCE_RADIUS, CLEARANCE_RADIUS + 1):
            for dx in range(-CLEARANCE_RADIUS, CLEARANCE_RADIUS + 1):
                cell = (ox + dx, oy + dy)
                if cell in (robot_position, goal) or cell in environment.obstacles:
                    continue
                if environment.is_inside(cell) and environment.is_walkable(cell):
                    cells.add(cell)
    return cells


def recalculate_path(reason="Route recalculated"):
    global path, path_index, status, message, replanning_count
    path = find_path(environment, robot_position, goal)
    path_index = 0
    replanning_count += 1
    metrics.record_replanning()
    metrics.update_environment(len(path) - 1 if path else 0, len(environment.obstacles))
    if path is None:
        status = "NO PATH"
        message = "No route available"
    elif robot_position == goal:
        status = "DESTINATION REACHED"
        message = "Goal reached successfully"
    else:
        status = "REPLANNING"
        message = reason


def add_obstacle_near_robot():
    """Add one obstacle to a free adjacent cell, if possible."""
    candidates = [
        (robot_position[0] + 1, robot_position[1]),
        (robot_position[0] - 1, robot_position[1]),
        (robot_position[0], robot_position[1] + 1),
        (robot_position[0], robot_position[1] - 1),
    ]
    random.shuffle(candidates)
    for cell in candidates:
        if cell in (robot_position, goal) or not environment.is_inside(cell):
            continue
        if cell not in environment.obstacles and environment.is_walkable(cell):
            environment.obstacles.add(cell)
            recalculate_path("Manual obstacle added; route updated")
            return True
    return False


def add_random_obstacles(count):
    candidates = []
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell = (x, y)
            if cell in (robot_position, start, goal) or cell in environment.obstacles:
                continue
            if not environment.is_inside(cell) or not environment.is_walkable(cell):
                continue
            if abs(x - robot_position[0]) + abs(y - robot_position[1]) < 3:
                continue
            if abs(x - goal[0]) + abs(y - goal[1]) < 3:
                continue
            candidates.append(cell)
    random.shuffle(candidates)
    added = 0
    for cell in candidates[:max(0, count)]:
        environment.obstacles.add(cell)
        added += 1
    return added


def reset_simulation():
    global environment, robot_position, path, path_index, steps_taken
    global paused, status, message, metrics, last_move_time, start_clock
    global replanning_count
    environment = Environment()
    robot_position = start
    path = find_path(environment, start, goal)
    path_index = 0
    steps_taken = 0
    paused = False
    status = "READY"
    message = "Simulation reset"
    metrics = NavigationMetrics()
    replanning_count = 0
    start_clock = time.monotonic()
    last_move_time = pygame.time.get_ticks()


def handle_yolo_image():
    global model, status, message, robot_position, path_index, steps_taken
    try:
        if model is None:
            message = "Loading YOLO model (CPU if no GPU)..."
            if not pygame.display.get_init():
                return
            model = YOLO("yolo11n.pt")
        results = model(IMAGE_PATH, verbose=False, device="cpu")
        obstacle_classes = {"person", "car", "bicycle", "motorcycle", "bus", "truck", "dog", "chair"}
        detected = set()
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                class_name = result.names[class_id]
                if class_name in obstacle_classes:
                    detected.add(class_name)
        added = add_random_obstacles(len(detected))
        if robot_position == goal:
            robot_position = start
            path_index = 0
            steps_taken = 0
        recalculate_path(f"YOLO demo: {len(detected)} class(es), {added} grid obstacle(s) added")
        if path is not None and robot_position != goal:
            status = "REPLANNING"
        print("YOLO classes:", sorted(detected), "| demonstration obstacles added:", added)
    except Exception as exc:
        status = "DETECTION ERROR"
        message = "Check image path/model; see terminal"
        print("Object detection failed:", exc)


def draw_map():
    screen.fill(BG)
    pygame.draw.rect(screen, GRID_BG, (0, 0, GRID_PIXEL_WIDTH, GRID_PIXEL_HEIGHT))

    # Inflated costmap/clearance overlay (visual aid, not a weighted A* costmap).
    if show_clearance:
        for x, y in clearance_cells():
            px, py = grid_to_pixel((x, y))
            pygame.draw.rect(screen, CLEARANCE, (px + 3, py + 3, CELL_SIZE - 6, CELL_SIZE - 6), border_radius=4)

    # Planned route.
    if path and len(path) > 1:
        points = [(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2) for x, y in path]
        pygame.draw.lines(screen, CYAN, False, points, 4)
        for px, py in points[1:-1]:
            pygame.draw.circle(screen, WHITE, (px, py), 3)

    # Obstacles and grid.
    for ox, oy in environment.obstacles:
        px, py = grid_to_pixel((ox, oy))
        pygame.draw.rect(screen, OBSTACLE, (px + 3, py + 3, CELL_SIZE - 6, CELL_SIZE - 6), border_radius=4)
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, GRID_LINE, (x * CELL_SIZE, 0), (x * CELL_SIZE, GRID_PIXEL_HEIGHT), 1)
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, GRID_LINE, (0, y * CELL_SIZE), (GRID_PIXEL_WIDTH, y * CELL_SIZE), 1)

    # Start and goal markers.
    sx, sy = grid_to_pixel(start)
    pygame.draw.rect(screen, GREEN, (sx + 5, sy + 5, CELL_SIZE - 10, CELL_SIZE - 10), border_radius=7)
    draw_centered("S", sx, sy, WHITE)
    gx, gy = grid_to_pixel(goal)
    pygame.draw.rect(screen, GREEN, (gx + 5, gy + 5, CELL_SIZE - 10, CELL_SIZE - 10), border_radius=7)
    draw_centered("G", gx, gy, WHITE)

    # Robot marker.
    rx, ry = grid_to_pixel(robot_position)
    pygame.draw.circle(screen, BLUE, (rx + CELL_SIZE // 2, ry + CELL_SIZE // 2), CELL_SIZE // 2 - 5)
    draw_centered("R", rx, ry, WHITE)


def draw_centered(label, px, py, color):
    surface = FONT.render(label, True, color)
    screen.blit(surface, (px + (CELL_SIZE - surface.get_width()) // 2, py + (CELL_SIZE - surface.get_height()) // 2))


def draw_panel():
    panel_x = GRID_PIXEL_WIDTH
    pygame.draw.rect(screen, PANEL_BG, (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))
    x = panel_x + 18
    y = 16
    draw_text("AUTONOMOUS NAVIGATION", x, y, BLUE, TITLE)
    y += 34
    draw_text("CPU-friendly simulation dashboard", x, y, MUTED, SMALL)
    y += 28
    pygame.draw.line(screen, (200, 210, 222), (x, y), (SCREEN_WIDTH - 16, y), 1)
    y += 14

    elapsed = max(0, int(time.monotonic() - start_clock))
    mins, secs = divmod(elapsed, 60)
    remaining = max(0, len(path) - 1 - path_index) if path else None
    rows = [
        ("ROBOT POSITION", str(robot_position), BLUE),
        ("GOAL POSITION", str(goal), GREEN),
        ("NAVIGATION STATUS", status, GREEN if status == "DESTINATION REACHED" else RED if status == "NO PATH" else BLUE),
        ("STEPS TAKEN", steps_taken, TEXT),
        ("REMAINING PATH", remaining if remaining is not None else "Unavailable", TEXT),
        ("OBSTACLES", len(environment.obstacles), RED),
        ("ROUTE UPDATES", replanning_count, CYAN),
        ("ELAPSED TIME", f"{mins:02d}:{secs:02d}", TEXT),
    ]
    for label, value, color in rows:
        draw_text(label, x, y, MUTED, TINY)
        y += 16
        draw_text(value, x, y, color, FONT)
        y += 27

    pygame.draw.line(screen, (200, 210, 222), (x, y), (SCREEN_WIDTH - 16, y), 1)
    y += 12
    draw_text("MAP LEGEND", x, y, TEXT, FONT)
    y += 24
    legend = [(BLUE, "Robot"), (GREEN, "Start / goal"), (CYAN, "Planned route"), (OBSTACLE, "Obstacle"), (CLEARANCE, "Clearance zone")]
    for color, label in legend:
        pygame.draw.rect(screen, color, (x, y + 2, 13, 13), border_radius=3)
        draw_text(label, x + 22, y, TEXT, SMALL)
        y += 21

    y += 5
    pygame.draw.line(screen, (200, 210, 222), (x, y), (SCREEN_WIDTH - 16, y), 1)
    y += 10
    draw_text("CONTROLS", x, y, TEXT, FONT)
    y += 22
    for line in ["O  Add adjacent obstacle", "C  Toggle clearance overlay", "D  YOLO image demo", "R  Reset simulation", "SPACE  Pause / resume", "Q  Quit"]:
        draw_text(line, x, y, TEXT, SMALL)
        y += 19
    if paused:
        draw_text("PAUSED", x, min(y + 2, SCREEN_HEIGHT - 28), RED, FONT)
    # Message bar along bottom of panel.
    msg_y = SCREEN_HEIGHT - 46
    pygame.draw.rect(screen, (220, 229, 239), (panel_x + 10, msg_y - 7, PANEL_WIDTH - 20, 39), border_radius=6)
    draw_text(message[:38], panel_x + 18, msg_y, TEXT, SMALL)


# ------------------------------- Main loop -------------------------------
try:
    while running:
        clock.tick(60)
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key == pygame.K_o:
                    if not add_obstacle_near_robot():
                        message = "No free adjacent cell for obstacle"
                elif event.key == pygame.K_c:
                    show_clearance = not show_clearance
                    message = "Clearance overlay " + ("enabled" if show_clearance else "disabled")
                elif event.key == pygame.K_d:
                    handle_yolo_image()
                elif event.key == pygame.K_r:
                    reset_simulation()
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    message = "Simulation paused" if paused else "Simulation resumed"

        if not paused and path is not None and robot_position != goal and now - last_move_time >= MOVE_DELAY_MS:
            if path_index + 1 < len(path):
                next_position = path[path_index + 1]
                if environment.is_inside(next_position) and environment.is_walkable(next_position):
                    robot_position = next_position
                    path_index += 1
                    steps_taken += 1
                    metrics.record_step()
                    metrics.update_environment(len(path) - 1, len(environment.obstacles))
                    last_move_time = now
                    if robot_position == goal:
                        status = "DESTINATION REACHED"
                        message = "Robot reached the goal!"
                else:
                    recalculate_path("Path blocked; recalculating")
                    last_move_time = now
            else:
                status = "NO PATH"
                message = "Route ended before goal"
        draw_map()
        draw_panel()
        pygame.display.flip()
finally:
    pygame.quit()
    print("Advanced simulation closed.")
