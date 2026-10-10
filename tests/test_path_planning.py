from simulation.environment import Environment
from path_planning import find_path


def test_astar_finds_path():
    environment = Environment()

    start = (1, 1)
    goal = (8, 6)

    path = find_path(environment, start, goal)

    assert path is not None
    assert path[0] == start
    assert path[-1] == goal


def test_astar_avoids_obstacles():
    environment = Environment()

    path = find_path(environment, (1, 1), (8, 6))

    assert path is not None

    for position in path:
        assert environment.is_walkable(position)


def test_astar_rejects_obstacle_goal():
    environment = Environment()

    path = find_path(environment, (1, 1), (5, 3))

    assert path is None