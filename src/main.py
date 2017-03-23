import json
import cv2

from enum import Enum

import time
from websocket import create_connection

import config

from detector.worldelement.drawingareadetector import DrawingAreaDetector
from detector.worldelement.obstaclepositiondetector import ObstacleDetector
from detector.worldelement.obstaclepositiondetector import ShapeDetector
from detector.worldelement.robotdetector import RobotDetector
from detector.worldelement.shapefactory import ShapeFactory
from detector.worldelement.tabledetector import TableDetector
from infrastructure.camera import JSONCameraModelRepository
from infrastructure.imagesource.directoryimagesource import DirectoryImageSource
from infrastructure.imagesource.savevideoimagesource import SaveVideoImageSource
from infrastructure.imagesource.videostreamimagesource import VideoStreamImageSource
from infrastructure.messageassembler import MessageAssembler
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagestranslationservice import ImageToWorldTranslator
from service.image.imagedetectionservice import ImageDetectionService

AppEnvironment = Enum('AppEnvironment', 'TESTING_VISION, COMPETITION, DEBUG')


def preprocess_image(image):
    image = cv2.medianBlur(image, ksize=5)
    image = cv2.GaussianBlur(image, (5, 5), 1)
    return image


robot_positions = []


def draw_robot_path(image, robot_positions):
    for pos in robot_positions:
        cv2.circle(image, pos, 2, (0, 0, 255), 2)


def log_robot_position(robot):
    image_x, image_y = robot._image_position
    world_x, world_y = robot._world_position

    robot_positions.append((
        int(image_x), int(image_y)
    ))

    print("Robot at --> ({}, {})".format(
        int(world_x),
        int(world_y)
    ))


def extract_obstacles(world_elements):
    obstacles = []
    for element in world_elements:
        if isinstance(element, list):
            obstacles = element
    return obstacles


def render_all_elements(image, world_elements):
    for element in world_elements:
        if isinstance(element, list):
            for obstacle in element:
                obstacle.draw_in(image)
        else:
            element.draw_in(image)


start_position = None


def render_path(image, current_robot, path):
    if path:
        prev = tuple(current_robot)
        for coord in path:
            next = coord
            cv2.line(image, prev, next, (0, 255, 0), 3)
            prev = next


if __name__ == "__main__":
    APP_ENVIRONMENT = AppEnvironment.COMPETITION

    WEBSOCKET = True
    VIDEO_DEBUG = not WEBSOCKET
    VIDEO_WRITE = False
    DRAW_PATH = True

    camera_model_repository = JSONCameraModelRepository(config.CAMERA_MODELS_FILE_PATH)
    camera_model = camera_model_repository.get_camera_model_by_id(config.TABLE_CAMERA_MODEL_ID)
    message_assembler = MessageAssembler()

    shape_factory = ShapeFactory()
    shape_detector = ShapeDetector()
    robot_detector = RobotDetector(shape_factory)
    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    obstacles_detector = ObstacleDetector(shape_detector)

    image_source = None

    if APP_ENVIRONMENT == AppEnvironment.COMPETITION:
        table_detector = DetectOnceProxy(table_detector)
        drawing_area_detector = DetectOnceProxy(drawing_area_detector)
        # obstacles_detector = DetectOnceProxy(obstacles_detector)
        image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
        # image_source = SaveVideoImageSource('/Users/jeansebastien/Desktop/videos/video26.avi')
    elif APP_ENVIRONMENT == AppEnvironment.DEBUG:
        image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
    elif APP_ENVIRONMENT == AppEnvironment.TESTING_VISION:
        image_source = DirectoryImageSource(config.TEST_IMAGE_DIRECTORY_PATH)

    detection_service = ImageDetectionService()
    detection_service.register_detector(robot_detector)
    detection_service.register_detector(table_detector)
    # detection_service.register_detector(drawing_area_detector)
    # detection_service.register_detector(obstacles_detector)

    image_to_world_translator = ImageToWorldTranslator(camera_model, detection_service)

    if WEBSOCKET:
        try:
            connection = create_connection(config.BASESTATION_WEBSOCKET_URL)
            print("Connection to BaseStation established at " + config.BASESTATION_WEBSOCKET_URL + '\n')
        except ConnectionRefusedError:
            print("Could not establish connection to BaseStation url: " + config.BASESTATION_WEBSOCKET_URL)
            print("Terminating...")
            exit(0)

    while image_source.has_next_image():
        image = image_source.next_image()
        if image is not None:
            image = camera_model.undistort_image(image)
            image = preprocess_image(image)

            world, robot, world_elements = image_to_world_translator.translate_image_to_world(image)

            obstacles = extract_obstacles(world_elements)

            render_all_elements(image, world_elements)

            if robot and world:
                log_robot_position(robot)

            if DRAW_PATH:
                draw_robot_path(image, robot_positions)

            if WEBSOCKET:
                try:
                    connection.send(json.dumps({"headers": "pull_path"}))

                    try:
                        path_data = json.loads(connection.recv())['data']
                        path_data = [(int(seg['x']), int(seg['y'])) for seg in path_data]
                        path_data = [camera_model.compute_world_to_image_coordinates(seg[0] / 44, seg[1] / 44, 0) for
                                     seg in
                                     path_data]

                        path_data = [(int(seg[0] * 0.6), int(seg[1] * 0.6)) for seg in path_data]

                        if start_position is None:
                            start_position = robot._image_position

                        render_path(image, start_position, path_data)

                    except KeyError:
                        pass

                    message = message_assembler.format_message(world, robot, image, obstacles)
                    connection.send(json.dumps(message))
                    ok = connection.recv()
                except NameError as e:
                    print(e)

            if VIDEO_DEBUG:
                cv2.imshow("Image debug", image)
                cv2.waitKey(1)
