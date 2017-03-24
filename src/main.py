import base64
import json
import cv2

from enum import Enum
from io import BytesIO
from threading import Thread
from PIL import Image
from flask import Flask, jsonify
from flask import make_response
from flask import request
from websocket import create_connection

import config
from detector.worldelement.drawingareadetector import DrawingAreaDetector
from detector.worldelement.obstaclepositiondetector import ObstacleDetector
from detector.worldelement.obstaclepositiondetector import ShapeDetector
from detector.worldelement.robotdetector import RobotDetector, np
from detector.worldelement.shapefactory import ShapeFactory
from detector.worldelement.tabledetector import TableDetector
from infrastructure.camera import JSONCameraModelRepository
from infrastructure.datalogger import DataLogger
from infrastructure.imagesource.directoryimagesource import DirectoryImageSource
from infrastructure.imagesource.savevideoimagesource import SaveVideoImageSource
from infrastructure.imagesource.videostreamimagesource import VideoStreamImageSource
from infrastructure.messageassembler import MessageAssembler
from infrastructure.renderingengine import RenderingEngine
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagesegmentation import segment_image
from service.image.imagedetectionservice import ImageDetectionService
from service.image.imagestranslationservice import ImageToWorldTranslator
from world.drawingarea import DrawingArea

AppEnvironment = Enum('AppEnvironment', 'TESTING_VISION, COMPETITION, DEBUG')


def create_rest_api(data_logger):
    api = Flask(__name__)

    @api.route('/vision/reset-rendering', methods=['POST'])
    def reset_rendering():
        data_logger.reset_robot_positions()
        response = make_response(jsonify({"message": "ok"}))
        return response

    @api.route('/image/segmentation', methods=["POST"])
    def receive_image():
        data = request.json

        try:
            image = base64.b64decode(data['image'])
            img = Image.open(BytesIO(image)).convert('RGB')
            opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            segments = segment_image(opencv_image)
            success, encoded = cv2.imencode('.jpg', segments)
            body = {"image": base64.b64encode(encoded).decode('utf-8')}
            return make_response(jsonify(body))
        except KeyError:
            error_message = "No image in request"
            print(error_message)
            return make_response(jsonify({"error": error_message}), 404)

    return api


def preprocess_image(image):
    image = cv2.medianBlur(image, ksize=5)
    image = cv2.GaussianBlur(image, (5, 5), 1)
    return image


def extract_obstacles(world_elements):
    obstacles = []
    for element in world_elements:
        if isinstance(element, list):
            obstacles = element
    return obstacles


def extract_drawing_area(world_elements):
    drawing_areas = [element for element in world_elements if isinstance(element, DrawingArea)]
    if len(drawing_areas) > 0:
        return drawing_areas[0]
    else:
        return None


if __name__ == "__main__":
    APP_ENVIRONMENT = AppEnvironment.COMPETITION

    WEB_SOCKET = True
    VIDEO_DEBUG = not WEB_SOCKET
    VIDEO_WRITE = False
    RENDER_PATH = True
    VERBOSE = False

    camera_model_repository = JSONCameraModelRepository(config.CAMERA_MODELS_FILE_PATH)
    camera_model = camera_model_repository.get_camera_model_by_id(config.TABLE_CAMERA_MODEL_ID)
    message_assembler = MessageAssembler()
    rendering_engine = RenderingEngine()
    data_logger = DataLogger(verbose=VERBOSE)

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
        obstacles_detector = DetectOnceProxy(obstacles_detector)
        # image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
        image_source = SaveVideoImageSource('/Users/jeansebastien/Desktop/videos/video26.avi')
    elif APP_ENVIRONMENT == AppEnvironment.DEBUG:
        image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
    elif APP_ENVIRONMENT == AppEnvironment.TESTING_VISION:
        image_source = DirectoryImageSource(config.TEST_IMAGE_DIRECTORY_PATH)

    detection_service = ImageDetectionService()
    detection_service.register_detector(robot_detector)
    detection_service.register_detector(table_detector)
    detection_service.register_detector(drawing_area_detector)
    detection_service.register_detector(obstacles_detector)

    image_to_world_translator = ImageToWorldTranslator(camera_model, detection_service)

    api = create_rest_api(data_logger)
    api_thread = Thread(target=api.run, kwargs={"host": '0.0.0.0'}).start()

    if WEB_SOCKET:
        try:
            connection = create_connection(config.BASESTATION_WEBSOCKET_URL)
            print("Connection to web socket established at {}\n".format(config.BASESTATION_WEBSOCKET_URL))
        except ConnectionRefusedError:
            print("Could not establish connection to web socket {}".format(config.BASESTATION_WEBSOCKET_URL))
            print("Falling back to VIDEO DEBUG")
            VIDEO_DEBUG = True
            WEB_SOCKET = False

    while image_source.has_next_image():
        image = image_source.next_image()
        if image is not None:
            image = camera_model.undistort_image(image)
            image = preprocess_image(image)
            world, robot, world_elements = image_to_world_translator.translate_image_to_world(image)
            rendering_engine.render_all_elements(image, world_elements)

            if robot and world:
                data_logger.log_robot_position(robot)

            if RENDER_PATH:
                rendering_engine.render_robot_path(image, data_logger.get_robot_positions())

            if WEB_SOCKET:
                try:
                    connection.send(json.dumps({"headers": "pull_path"}))

                    try:
                        path_data = json.loads(connection.recv())['data']
                    except KeyError:
                        pass

                    obstacles = extract_obstacles(world_elements)
                    drawing_area = extract_drawing_area(world_elements)
                    message = message_assembler.format_message(world, robot, image, obstacles, drawing_area)
                    connection.send(json.dumps(message))
                    ok = connection.recv()
                except NameError as e:
                    print(e)

            if VIDEO_DEBUG:
                cv2.imshow("Image debug", image)
                cv2.waitKey(1)
