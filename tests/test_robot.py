from simulation.environment import Environment
from simulation.robot import Robot


def test_robot_moves_to_free_cell():
    environment = Environment()
    robot = Robot((1, 1))

    result = robot.move_to((2, 1), environment)

    assert result is True
    assert robot.position == (2, 1)


def test_robot_cannot_enter_obstacle():
    environment = Environment()
    robot = Robot((4, 3))

    result = robot.move_to((5, 3), environment)

    assert result is False
    assert robot.position == (4, 3)
    assert robot.collision_count == 1
    