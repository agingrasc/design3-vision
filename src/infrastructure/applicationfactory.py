import base64
import glob
import random
import cv2
import numpy as np
from PIL import Image
from flask import Flask, make_response, jsonify, request, json
from io import BytesIO

import config
from service.image.imagedetectionservice import ImageDetectionService
from service.image.imagesegmentation import segment_image, NoSegmentsFound

ORIENTATION = {
    "SOUTH": 0,
    "NORTH": 180,
    "EAST": 270,
    "WEST": 90
}


class ApplicationFactory:
    def create_detection_service(self, detectors):
        detection_service = ImageDetectionService()
        for detector in detectors:
            detection_service.register_detector(detector)
        return detection_service

    def create_rest_api(self, data_logger, detection_service, image_to_world_translation, message_assembler):
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

        @api.route('/vision/reset-obstacles', methods=['POST'])
        def reset_obstacles():
            detection_service.reset_obstacles()
            return make_response(jsonify({"message": "ok"}))

        @api.route('/world-dimensions')
        def get_world_dimension():
            world = image_to_world_translation.get_world()
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
            data_logger.reset_robot_positions()
            data_logger.set_path(image_to_world_translation.translate_path(path))
            return make_response(jsonify({"message": "ok"}))

        @api.route('/obstacles', methods=["GET"])
        def get_obstacles():
            obstacles = image_to_world_translation.get_obstacles()
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
                orientation = float(ORIENTATION[data['orientation']])

                try:
                    segments, segmented_image, center_of_mass, mask = segment_image(image)
                    segments, world_segments = image_to_world_translation.transform_segments(segmented_image, segments,
                                                                                             scaling_factor,
                                                                                             orientation)
                    data_logger.set_figure_drawing(segments)

                    success, segmented_image_encoded = cv2.imencode('.jpg', segmented_image)
                    ret, mask_encoded = cv2.imencode('.jpg', mask)

                    body = {
                        "image": base64.b64encode(segmented_image_encoded).decode('utf-8'),
                        "thresholded_image": base64.b64encode(mask_encoded).decode('utf-8'),
                        "segments": world_segments
                    }
                except NoSegmentsFound as e:
                    body = {
                        "error": type(e).__name__
                    }

                return make_response(jsonify(body))
            else:
                data = request.json

                scaling_factor = float(data['scaling'])
                orientation = float(ORIENTATION[data['orientation']])

                try:
                    image = base64.b64decode(data['image'])
                    img = Image.open(BytesIO(image)).convert('RGB')
                    opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    segments, segmented_image, center_of_mass, mask = segment_image(opencv_image)
                    success, segmented_image_encoded = cv2.imencode('.jpg', segmented_image)
                    success, mask_encoded = cv2.imencode('.jpg', opencv_image)
                    segments, world_segments = image_to_world_translation.transform_segments(segmented_image, segments,
                                                                                             scaling_factor,
                                                                                             orientation)
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
                except NoSegmentsFound as e:
                    return make_response(jsonify({"error": type(e).__name__}), 404)

        return api
