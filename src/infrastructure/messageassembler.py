import base64

import cv2

from config import TARGET_SIDE_LENGTH

IMAGE_DIMINUTION_RATIO = 2


class MessageAssembler:
    def format_message(self, world, robot, image):
        return {
            "headers": "push_vision_data",
            "data": {
                "image": {
                    "ratio": "0.38",
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
                    "unit": "cm",
                    "base_table": {
                        "dimension": self.get_world_dimension(world)
                    },
                    "robot": {
                        "position": self.get_robot_position(robot)
                    }
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
                "x": str((robot._world_position[0] * TARGET_SIDE_LENGTH)),
                "y": str((robot._world_position[1] * TARGET_SIDE_LENGTH))
            }
            return robot_position
        else:
            return {
                "x": "",
                "y": ""
            }

    def prepare_image(self, image):
        image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        cnt = cv2.imencode('.png', image)[1]
        image_data = base64.b64encode(cnt)
        image_data = image_data.decode('utf-8')
        return image_data
