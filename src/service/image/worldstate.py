class WorldState:
    def __init__(self, world, robot, image_elements):
        self._world = world
        self._robot = robot
        self._image_elements = image_elements

    def robot_was_detected(self):
        return self._robot is not None

    def world_was_detected(self):
        return self._world is not None

    def get_image_elements(self):
        return self._image_elements

    def get_robot(self):
        return self._robot
