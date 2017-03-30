import base64
import glob
import json
import random
import cv2

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
from infrastructure.imagesource.savevideoimagesource import SaveVideoImageSource
from infrastructure.imagesource.videostreamimagesource import VideoStreamImageSource
from infrastructure.messageassembler import MessageAssembler
from infrastructure.renderingengine import RenderingEngine
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagesegmentation import segment_image
from service.image.imagedetectionservice import ImageDetectionService
from service.image.imagestranslationservice import ImageToWorldTranslator


def create_rest_api(data_logger, detection_service, image_to_world_translation, message_assembler):
    api = Flask(__name__)

    @api.route('/vision/reset-rendering', methods=['POST'])
    def reset_rendering():
        data_logger.reset_robot_positions()
        data_logger.reset_path()
        response = make_response(jsonify({"message": "ok"}))
        return response

    @api.route('/vision/reset-detection', methods=['POST'])
    def reset_detection():
        detection_service.reset_detection()
        return make_response(jsonify({"message": "ok"}))

    @api.route('/world-dimensions')
    def get_world_dimension():
        world = image_to_world_translator.get_world()
        world_dimension_body = message_assembler.get_world_dimension(world)
        response_body = {"world_dimensions": world_dimension_body}
        return make_response(jsonify(response_body))

    @api.route('/path', methods=["POST"])
    def create_path():
        if not isinstance(request.json, dict):
            data = json.loads(request.json)
        else:
            data = request.json

        path = data['data']['path']
        data_logger.set_path(image_to_world_translator.translate_path(path))
        return make_response(jsonify({"message": "ok"}))

    @api.route('/obstacles', methods=["GET"])
    def get_obstacles():
        obstacles = image_to_world_translator.get_obstacles()
        obstacles_body = message_assembler.get_obstacles(obstacles)
        response_body = {"data": {"obstacles": obstacles_body}}
        return make_response(jsonify(response_body))

    @api.route('/drawzone-corners')
    def get_drawzone_corners():
        top_right = image_to_world_translation._drawing_area._top_right
        return make_response(jsonify({
            "data": {
                "top_right": {
                    "x": str(top_right[0] * config.TARGET_SIDE_LENGTH),
                    "y": str(top_right[1] * config.TARGET_SIDE_LENGTH)
                }
            }
        }))

    @api.route('/image/segmentation', methods=["POST"])
    def receive_image():
        if request.args.get('fake'):
            images = glob.glob('../data/images/figures/*.jpg')
            image = cv2.imread(random.choice(images))
            data = request.json
            scaling_factor = float(data['scaling'])
            segments, segmented_image, center_of_mass, mask = segment_image(image)
            segments, world_segments = image_to_world_translation.transform_segments(segmented_image, segments,
                                                                                     scaling_factor)
            data_logger.set_figure_drawing(segments)

            success, segmented_image_encoded = cv2.imencode('.jpg', segmented_image)
            ret, mask_encoded = cv2.imencode('.jpg', mask)

            body = {
                "image": base64.b64encode(segmented_image_encoded).decode('utf-8'),
                "thresholded_image": base64.b64encode(mask_encoded).decode('utf-8'),
                "segments": world_segments
            }

            return make_response(jsonify(body))
        else:
            data = request.json

            scaling_factor = float(data['scaling'])

            try:
                image = base64.b64decode(data['image'])
                img = Image.open(BytesIO(image)).convert('RGB')
                opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                segments, segmented_image, center_of_mass, mask = segment_image(opencv_image)
                success, segmented_image_encoded = cv2.imencode('.jpg', segmented_image)
                success, mask_encoded = cv2.imencode('.jpg', opencv_image)
                segments, world_segments = image_to_world_translation.transform_segments(segmented_image, segments,
                                                                                         scaling_factor)
                data_logger.set_figure_drawing(segments)
                body = {
                    "image": base64.b64encode(segmented_image_encoded).decode('utf-8'),
                    "thresholded_image": base64.b64encode(mask_encoded).decode('utf-8'),
                    "segments": world_segments
                }
                return make_response(jsonify(body))
            except KeyError:
                error_message = "No image in request"
                return make_response(jsonify({"error": error_message}), 404)

    return api


def create_detection_service():
    shape_factory = ShapeFactory()
    shape_detector = ShapeDetector()
    robot_detector = RobotDetector(shape_factory)
    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    obstacles_detector = ObstacleDetector(shape_detector)
    table_detector = DetectOnceProxy(table_detector)
    drawing_area_detector = DetectOnceProxy(drawing_area_detector)
    obstacles_detector = DetectOnceProxy(obstacles_detector)
    detection_service = ImageDetectionService()
    detection_service.register_detector(robot_detector)
    detection_service.register_detector(table_detector)
    detection_service.register_detector(drawing_area_detector)
    detection_service.register_detector(obstacles_detector)
    return detection_service


def preprocess_image(image, camera_model):
    image = camera_model.undistort_image(image)
    image = cv2.medianBlur(image, ksize=5)
    image = cv2.GaussianBlur(image, (5, 5), 1)
    return image


if __name__ == "__main__":
    WEB_SOCKET = True
    VIDEO_DEBUG = not WEB_SOCKET
    VIDEO_WRITE = False
    RENDER_PATH = True
    VERBOSE = True

    message_assembler = MessageAssembler()
    rendering_engine = RenderingEngine()
    data_logger = DataLogger(verbose=VERBOSE)

    camera_model_repository = JSONCameraModelRepository(config.CAMERA_MODELS_FILE_PATH)
    camera_model = camera_model_repository.get_camera_model_by_id(config.TABLE_CAMERA_MODEL_ID)
    detection_service = create_detection_service()
    image_to_world_translator = ImageToWorldTranslator(camera_model, detection_service)

    api = create_rest_api(data_logger, detection_service, image_to_world_translator, message_assembler)
    api_thread = Thread(target=api.run, kwargs={"host": '0.0.0.0'})
    api_thread.start()

    # image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
    image_source = SaveVideoImageSource('/Users/jeansebastien/Desktop/videos/video24.avi')

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
            image = preprocess_image(image, camera_model)
            world, robot, world_elements = image_to_world_translator.translate_image_to_world(image)
            rendering_engine.render_all_elements(image, world_elements)

            if robot and world:
                data_logger.log_robot_position(robot)

            if RENDER_PATH and robot:
                if data_logger._figure_drawing is not None:
                    figure_drawing = np.array(data_logger._figure_drawing).astype('int')

                    cv2.drawContours(image, [figure_drawing], -1, (0, 255, 0), 2)

                rendering_engine.render_actual_trajectory(image, data_logger.get_robot_positions())
                rendering_engine.render_planned_path(image, robot._world_position, data_logger.get_path())

            if WEB_SOCKET:
                try:
                    message = message_assembler.format_message(world, robot, image, world_elements)
                    connection.send(json.dumps(message))
                    ok = connection.recv()
                except NameError as e:
                    print(e)

            if VIDEO_DEBUG:
                cv2.imshow("Image debug", image)
                cv2.waitKey(1)
