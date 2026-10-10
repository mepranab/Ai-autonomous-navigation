from simulation.environment import Environment
from path_planning import find_path


def test_astar_finds_path_with_additional_obstacles():
    environment = Environment()

    # Add demonstration obstacles from the AI integration test.
    environment.add_obstacle((7, 6))
    environment.add_obstacle((8, 6))
    environment.add_obstacle((9, 6))
    environment.add_obstacle((7, 7))

    start = (0, 0)
    goal = (19, 14)

    path = find_path(environment, start, goal)

    assert path is not None
    assert path[0] == start
    assert path[-1] == goal

    # The planned route must not pass through obstacles.
    for position in path:
        assert not environment.is_obstacle(position)


def test_astar_returns_no_path_when_goal_is_blocked():
    environment = Environment()
    goal = (19, 14)

    environment.add_obstacle(goal)

    path = find_path(environment, (0, 0), goal)

    assert path is None
    