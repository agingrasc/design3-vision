import json
from threading import Thread

import cv2
import numpy as np
from websocket import create_connection

import config
from domain.camera.camerafactory import CameraFactory
from domain.detector.worldelement.drawingareadetector import DrawingAreaDetector
from domain.detector.worldelement.obstaclepositiondetector import ObstacleDetector, ShapeDetector
from domain.detector.worldelement.robotdetector import RobotDetector
from domain.detector.worldelement.shapefactory import ShapeFactory
from domain.detector.worldelement.tabledetector import TableDetector
from infrastructure.applicationfactory import ApplicationFactory
from infrastructure.datalogger import DataLogger
from infrastructure.imagesource.savevideoimagesource import SaveVideoImageSource
from infrastructure.jsoncameramodelrepository import JSONCameraModelRepository
from infrastructure.messageassembler import MessageAssembler
from infrastructure.renderingengine import RenderingEngine
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagestranslationservice import ImageToWorldTranslator


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
    application_factory = ApplicationFactory()

    camera_factory = CameraFactory()
    camera_model_repository = JSONCameraModelRepository(config.CAMERA_MODELS_FILE_PATH, camera_factory)
    camera_model = camera_model_repository.find_by_id(config.TABLE_CAMERA_MODEL_ID)

    shape_factory = ShapeFactory()
    shape_detector = ShapeDetector()
    robot_detector = RobotDetector(shape_factory)
    table_detector = TableDetector(shape_factory)
    drawing_area_detector = DrawingAreaDetector(shape_factory)
    obstacles_detector = ObstacleDetector(shape_detector)
    table_detector = DetectOnceProxy(table_detector)
    drawing_area_detector = DetectOnceProxy(drawing_area_detector)
    obstacles_detector = DetectOnceProxy(obstacles_detector)

    detection_service = application_factory.create_detection_service([
        robot_detector,
        table_detector,
        drawing_area_detector,
        obstacles_detector
    ])

    image_to_world_translator = ImageToWorldTranslator(camera_model, detection_service)

    api = application_factory.create_rest_api(data_logger, detection_service, image_to_world_translator,
                                              message_assembler)
    api_thread = Thread(target=api.run, kwargs={"host": '0.0.0.0'})
    api_thread.start()

    # image_source = VideoStreamImageSource(config.CAMERA_ID, VIDEO_WRITE)
    image_source = SaveVideoImageSource('/Users/jeansebastien/Desktop/videos/video26.avi')

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
