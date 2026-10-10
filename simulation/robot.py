class Robot:
    def __init__(self, start_position):
        self.position = start_position
        self.steps_taken = 0
        self.collision_count = 0

    def move_to(self, new_position, environment):
        if not environment.is_inside(new_position):
            self.collision_count += 1
            return False

        if environment.is_obstacle(new_position):
            self.collision_count += 1
            return False

        self.position = new_position
        self.steps_taken += 1

        return True
    