import base64
import glob
import json
from time import sleep

import cv2
from websocket import create_connection

from detector.worldelement.drawingareadetector import DrawingAreaDetector
from detector.worldelement.robotdetector import RobotDetector
from detector.worldelement.shapefactory import ShapeFactory
from detector.worldelement.tabledetector import TableDetector
from infrastructure.camera import JSONCameraModelRepository
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagedetectionservice import ImageToWorldTranslator, ImageDetectionService

video = cv2.VideoCapture(1)

video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
video.set(cv2.CAP_PROP_FPS, 15)


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
            "x": str(world._origin['x'] / 2),
            "y": str(world._origin['y'] / 2)
        }
    else:
        return {
            "x": "",
            "y": ""
        }


if __name__ == "__main__":
    camera_model_repository = JSONCameraModelRepository('../data/camera_models/camera_models.json')
    camera_model = camera_model_repository.get_camera_model_by_id(0)
    image_to_world_translator = ImageToWorldTranslator(camera_model)

    shape_factory = ShapeFactory()
    robot_detector = RobotDetector(shape_factory)
    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)

    COMPETITION_CONTEXT = False
    if COMPETITION_CONTEXT:
        table_detector = DetectOnceProxy(table_detector)
        drawing_area_detector = DetectOnceProxy(drawing_area_detector)

    detection_service = ImageDetectionService(image_to_world_translator)
    detection_service.register_detector(robot_detector)
    detection_service.register_detector(drawing_area_detector)
    detection_service.register_detector(table_detector)

    # connection = create_connection("ws://localhost:3000")

    sleep(2)

    while video.isOpened():
        ret, image = video.read()
        if ret:
            image = camera_model.undistort_image(image)
            world = detection_service.translate_image_to_world(image)

            if world is not None:
                world_origin_in_target = camera_model.compute_image_to_world_coordinates(world._image_origin._x,
                                                                                         world._image_origin._y, 0)

            cv2.imshow('World Image', image)
            cv2.waitKey(1)
            # image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)

            # cnt = cv2.imencode('.png', image)[1]

            # image_data = base64.b64encode(cnt)
            #
            # response = {
            #     "headers": "push_vision_data",
            #     "data": {
            #         "image": {
            #             "ratio": "2.58",
            #             "origin": get_world_origin(world),
            #
            #             "data": image_data.decode('utf-8'),
            #             "original_dimension": {
            #                 "width": "1280",
            #                 "height": "800"
            #             },
            #             "sent_dimension": {
            #                 "width": "1280",
            #                 "height": "800"
            #             }
            #         },
            #         "world": {
            #             "unit": "cm",
            #             "base_table": {
            #                 "dimension": get_world_dimension(world)
            #             }
            #         }
            #     }
            # }

            # print(json.dumps(response))
            # print("")

            # connection.send(json.dumps(response))
