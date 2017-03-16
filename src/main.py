import base64
import json
import cv2
import numpy as np

from enum import Enum
from websocket import create_connection

import config

from detector.worldelement.drawingareadetector import DrawingAreaDetector
from detector.worldelement.robotdetector import RobotDetector
from detector.worldelement.shapefactory import ShapeFactory
from detector.worldelement.tabledetector import TableDetector
from infrastructure.camera import JSONCameraModelRepository
from infrastructure.imagesource.directoryimagesource import DirectoryImageSource
from infrastructure.imagesource.videostreamimagesource import VideoStreamImageSource
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagedetectionservice import ImageToWorldTranslator
from service.image.imagedetectionservice import ImageDetectionService

IMAGE_DIMINUTION_RATIO = 2
TARGET_SIDE_LENGTH = 44 # in mm

AppEnvironment = Enum('AppEnvironment', 'TESTING_VISION, COMPETITION, DEBUG')


def get_world_dimension(world):
    if world is not None:
        return {
            "width": str(world._width),
            "height": str(world._length)
        }
    else:
        return {
            "width": "",
            "height": ""
        }


def get_world_origin(world):
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


def get_robot_position(robot):
    if robot is not None:
        robot_position = {
            "x": str((robot._world_position[0] * TARGET_SIDE_LENGTH)),
            "y": str((robot._world_position[1] * TARGET_SIDE_LENGTH))
        }
        print(robot_position)
        return robot_position
    else:
        return {
            "x": "",
            "y": ""
        }


def prepare_image(image):
    image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    cnt = cv2.imencode('.png', image)[1]
    image_data = base64.b64encode(cnt)
    image_data = image_data.decode('utf-8')
    return image_data


def format_message(world, robot, image):
    return {
        "headers": "push_vision_data",
        "data": {
            "image": {
                "ratio": "2.58",
                "origin": get_world_origin(world),

                "data": prepare_image(image),
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
                    "dimension": get_world_dimension(world)
                },
                "robot": {
                    "position": get_robot_position(robot)
                }
            },

        }
    }


def homogeneous_to_cart(coordinate):
    return [
        coordinate[0] / coordinate[2],
        coordinate[1] / coordinate[2]
    ]


if __name__ == "__main__":
    APP_ENVIRONMENT = AppEnvironment.COMPETITION

    WEBSOCKET = True
    VIDEO_DEBUG = not WEBSOCKET
    VIDEO_WRITE = True

    camera_model_repository = JSONCameraModelRepository(config.CAMERA_MODELS_FILE_PATH)
    camera_model = camera_model_repository.get_camera_model_by_id(config.TABLE_CAMERA_MODEL_ID)

    shape_factory = ShapeFactory()
    robot_detector = RobotDetector(shape_factory)
    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    image_source = None

    if APP_ENVIRONMENT == AppEnvironment.COMPETITION:
        table_detector = DetectOnceProxy(table_detector)
        drawing_area_detector = DetectOnceProxy(drawing_area_detector)
        image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
    elif APP_ENVIRONMENT == AppEnvironment.DEBUG:
        image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
    elif APP_ENVIRONMENT == AppEnvironment.TESTING_VISION:
        image_source = DirectoryImageSource(config.TEST_IMAGE_DIRECTORY_PATH)

    image_to_world_translator = ImageToWorldTranslator(camera_model)
    detection_service = ImageDetectionService(image_to_world_translator)

    detection_service.register_detector(robot_detector)
    detection_service.register_detector(drawing_area_detector)
    detection_service.register_detector(table_detector)

    if WEBSOCKET:
        try:
            connection = create_connecgtion(config.BASESTATION_WEBSOCKET_URL)
            print("Connection to BaseStation established at " + config.BASESTATION_WEBSOCKET_URL + '\n')
        except ConnectionRefusedError:
            print("Could not establish connection to BaseStation url: " + config.BASESTATION_WEBSOCKET_URL)
            print("Terminating...")
            exit(0)

    while image_source.has_next_image():
        image = image_source.next_image()
        if image is not None:
            image = camera_model.undistort_image(image)
            world, robot = detection_service.translate_image_to_world(image)

            if world:
                if robot:
                    robot_target_position = np.array([
                        robot._world_position[0],
                        robot._world_position[1],
                        1
                    ])

                    robot_world_position = homogeneous_to_cart(np.dot(world._target_to_world, robot_target_position))
                    robot.set_world_position(robot_world_position)

            message = format_message(world, robot, image)

            if WEBSOCKET:
                try:
                    connection.send(json.dumps(message))
                except NameError:
                    print("No connection to websocket")

            if VIDEO_DEBUG:
                cv2.imshow("Image debug", image)
                cv2.waitKey(1)
