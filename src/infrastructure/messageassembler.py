import base64

import cv2
import numpy as np

from domain.world.drawingarea import DrawingArea

IMAGE_DIMINUTION_RATIO = 2


class MessageAssembler:
    def create_world_state_dto(self, image, world_state):
        world_elements = world_state._image_elements
        robot = world_state._robot
        world = world_state._world

        drawing_area = self.extract_drawing_area(world_elements)
        obstacles = self.extract_obstacles(world_elements)
        return {
            "headers": "push_vision_data",
            "data": {
                "image": {
                    "ratio": "0.378",
                    "origin": self.get_world_origin(world),

                    "data": self.prepare_image(image),
                    "original_dimension": {
                        "width": "1280",
                        "height": "800"
                    },
                    "sent_dimension": {
                        "width": "1280",
                        "height": "800"
                    }
                },
                "world": {
                    "unit": "mm",
                    "base_table": {
                        "dimension": self.get_world_dimension(world)
                    },
                    "robot": {
                        "position": self.get_robot_position(robot),
                        "orientation": self.get_robot_orientation(robot)
                    },
                    "obstacles": self.get_obstacles(obstacles),
                    "drawing_area": self.get_drawing_area(drawing_area)
                },

            }
        }

    def get_world_dimension(self, world):
        if world is not None:
            return {
                "width": str(world._width * 10),
                "height": str(world._length * 10)
            }
        else:
            return {
                "width": "",
                "height": ""
            }

    def get_world_origin(self, world):
        if world is not None:
            return {
                "x": str(world._image_origin._x / IMAGE_DIMINUTION_RATIO),
                "y": str(world._image_origin._y / IMAGE_DIMINUTION_RATIO)
            }
        else:
            return {
                "x": "",
                "y": ""
            }

    def get_robot_position(self, robot):
        if robot is not None:
            robot_position = {
                "x": str((robot._world_position[0])),
                "y": str((robot._world_position[1]))
            }
            return robot_position
        else:
            return {
                "x": "",
                "y": ""
            }

    def get_robot_orientation(self, robot):
        if robot is not None:
            return str(np.deg2rad(robot._angle))
        else:
            return ""

    def get_obstacles(self, obstacles):

        if obstacles is not None:
            return [{"position": {"x": obstacle._world_position[0], "y": obstacle._world_position[1]},
                     "tag": obstacle._orientation.upper(),
                     "dimension": {"width": "190", "length": "190"}}
                    for obstacle in obstacles]
        else:
            return []

    def prepare_image(self, image):
        image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        cnt = cv2.imencode('.jpeg', image)[1]
        image_data = base64.b64encode(cnt)
        image_data = image_data.decode('utf-8')
        return image_data

    def get_drawing_area(self, drawing_area):
        if drawing_area is not None:
            return {
                "dimension": {
                    "width": drawing_area._inner_square_dimension['width'] * 10,
                    "length": drawing_area._inner_square_dimension['length'] * 10
                }

            }
        else:
            return ""

    def extract_obstacles(self, world_elements):
        obstacles = []
        for element in world_elements:
            if isinstance(element, list):
                obstacles = element
        return obstacles

    def extract_drawing_area(self, world_elements):
        drawing_areas = [element for element in world_elements if isinstance(element, DrawingArea)]
        if len(drawing_areas) > 0:
            return drawing_areas[0]
        else:
            return None
