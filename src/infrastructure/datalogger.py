import math


class DataLogger:
    def __init__(self, verbose=False):
        self._robot_positions = []
        self._verbose = verbose

    def log_robot_position(self, robot):
        image_x, image_y = robot._image_position
        world_x, world_y = robot._world_position

        self._robot_positions.append((
            int(math.floor(image_x)), int(math.floor(image_y))
        ))

        if self._verbose:
            print("Robot at --> ({}, {})".format(
                int(math.floor(world_x)),
                int(math.floor(world_y))
            ))

    def reset_robot_positions(self):
        self._robot_positions.clear()

    def get_robot_positions(self):
        return self._robot_positions