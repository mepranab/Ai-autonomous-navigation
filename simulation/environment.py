class Environment:
    def __init__(self):
        self.width = 20
        self.height = 15

        self.obstacles = {
            (5, 3),
            (5, 4),
            (5, 5),
            (10, 8),
            (11, 8),
        }

    def is_obstacle(self, position):
        return position in self.obstacles

    def is_inside(self, position):
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, position):
        return self.is_inside(position) and not self.is_obstacle(position)

    def add_obstacle(self, position):
        """Add an obstacle if its position is inside the grid."""
        if self.is_inside(position):
            self.obstacles.add(position)
            return True

        return False
    