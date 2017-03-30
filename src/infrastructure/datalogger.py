import math
from collections import deque


class DataLogger:
    def __init__(self, verbose=False):
        self._robot_positions = deque()
        self._verbose = verbose
        self._current_destination = None
        self._path = []
        self._figure_drawing = None

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

    def reset_path(self):
        self._path.clear()

    def get_robot_positions(self):
        return self._robot_positions

    def set_current_destination(self, destination):
        self._current_destination = destination

    def get_current_state(self):
        return self._current_destination

    def set_path(self, path):
        self._path = path

    def get_path(self):
        return self._path

    def set_figure_drawing(self, segments):
        self._figure_drawing = segments