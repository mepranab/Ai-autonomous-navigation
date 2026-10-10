import heapq


def heuristic(a, b):
    """Estimate the distance between two positions."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def find_path(environment, start, goal):
    """Find a path from start to goal using the A* algorithm."""

    if not environment.is_walkable(start):
        return None

    if not environment.is_walkable(goal):
        return None

    frontier = []
    heapq.heappush(frontier, (0, start))

    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        x, y = current

        neighbors = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        for neighbor in neighbors:
            if not environment.is_walkable(neighbor):
                continue

            new_cost = cost_so_far[current] + 1

            if (
                neighbor not in cost_so_far
                or new_cost < cost_so_far[neighbor]
            ):
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)

                heapq.heappush(
                    frontier,
                    (priority, neighbor),
                )

                came_from[neighbor] = current

    if goal not in came_from:
        return None

    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path
