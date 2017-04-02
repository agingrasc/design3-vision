import json
from threading import Thread

import cv2
from websocket import create_connection

import config
from domain.camera.camerafactory import CameraFactory
from domain.detector.worldelement.drawingareadetector import DrawingAreaDetector
from domain.detector.worldelement.obstaclepositiondetector import ObstacleDetector, ShapeDetector
from domain.detector.worldelement.robotdetector import RobotDetector
from domain.detector.worldelement.shapefactory import ShapeFactory
from domain.detector.worldelement.tabledetector import TableDetector
from infrastructure.applicationfactory import ApplicationFactory
from infrastructure.graphics.renderingengine import RenderingEngine
from infrastructure.imagesource.savevideoimagesource import SaveVideoImageSource
from infrastructure.messageassembler import MessageAssembler
from infrastructure.persistance.datalogger import DataLogger
from infrastructure.persistance.jsoncameramodelrepository import JSONCameraModelRepository
from service.image.detectonceproxy import DetectOnceProxy
from service.image.imagestranslationservice import ImageToWorldTranslator


class VisionApplication:
    def __init__(self):
        self._started = False

    def start(self):
        self._started = True
        WEB_SOCKET = True
        VIDEO_DEBUG = not WEB_SOCKET
        VIDEO_WRITE = False
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

        image_to_world_translator = ImageToWorldTranslator(camera_model)

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

        while self._started:
            if image_source.has_next_image():
                image = image_source.next_image()
                image = self.preprocess_image(image, camera_model)

                image_elements = detection_service.detect_all_world_elements(image)
                world_state = image_to_world_translator.translate_image_elements_to_world(image_elements)

                if world_state.robot_was_detected() and world_state.world_was_detected():
                    data_logger.log_robot_position(world_state.get_robot())

                if world_state.robot_was_detected():
                    rendering_engine.render_figure_drawing(image, data_logger.get_figure_drawing())
                    rendering_engine.render_planned_path(image, world_state.get_robot()._world_position,
                                                         data_logger.get_path())
                    rendering_engine.render_actual_path(image, data_logger.get_robot_positions())

                rendering_engine.render_all_elements(image, world_state.get_image_elements())

                if WEB_SOCKET:
                    try:
                        world_state_dto = message_assembler.create_world_state_dto(image, world_state)
                        connection.send(json.dumps(world_state_dto))
                        ok = connection.recv()
                    except NameError as e:
                        print(e)

                if VIDEO_DEBUG:
                    cv2.imshow("Image debug", image)
                    cv2.waitKey(1)

    def preprocess_image(self, image, camera_model):
        image = camera_model.undistort_image(image)
        image = cv2.medianBlur(image, ksize=5)
        image = cv2.GaussianBlur(image, (5, 5), 1)
        return image


if __name__ == "__main__":
    app = VisionApplication()
    app.start()
