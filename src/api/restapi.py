import os

from flask import Flask
from flask import send_file
from flask import send_from_directory
from flask import make_response
from flask import jsonify
from flask import request

import requests

import numpy as np

from detector.robotpositiondetector import get_robot_angle

CALIBRATION_IMAGES_DIRECTORY = '../data/images/calibration'
CHESSBOARD_IMAGES_DIRECTORY = '../../data/images/chessboard'
UNDISTORT_IMAGES_DIRECTORY = '../../data/images/undistort'


class FlaskRESTAPI:
    def __init__(self, static_folder, camera_service, calibration_service, image_repository, camera_model_repository):
        self.static_folder = static_folder
        self.camera_service = camera_service
        self.calibration_service = calibration_service
        self.image_repository = image_repository
        self.camera_model_repository = camera_model_repository
        self.robot_position = [0, 0, 0]

        self.api = Flask(__name__, static_folder=static_folder)

        self.api.add_url_rule('/', 'index', self.index)
        self.api.add_url_rule('/css/<path:filename>', 'css', self.css)
        self.api.add_url_rule('/js/<path:filename>', 'js', self.js)

        self.api.add_url_rule('/images-infos', 'images-infos', self.send_image_infos, methods=['GET'])
        self.api.add_url_rule('/images/<string:filename>', 'image', self.get_image)
        self.api.add_url_rule('/images/<string:id>/undistorted', 'undistorted', self.get_undistorted_image)
        self.api.add_url_rule('/images/<string:id>/chessboard', 'chessboard', self.get_chessboard)

        self.api.add_url_rule('/set_robot_position', 'robot-position', self.set_robot_position, methods=["POST"])
        self.api.add_url_rule('/go_to', 'go_to', self.go_to, methods=["POST"])

        self.api.add_url_rule('/calibration/create', 'calibration-create', self.create_calibration)

        self.api.add_url_rule('/world_coordinates', 'world-coordinates', self.get_world_coordinates, methods=['POST'])

    def send_image_infos(self):
        response_body = {
            "calibration": {
                "images": self.get_calibration_images_infos()
            }
        }

        response = make_response(jsonify(response_body))
        response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    def index(self):
        return send_from_directory(self.static_folder, 'index.html')

    def livefeed(self):
        return send_from_directory(self.static_folder, 'livefeed.html')

    def get_image(self, filename):
        return send_file('../../data/images/calibration' + "/" + filename, mimetype='image/jpeg')

    def get_undistorted_image(self, id):
        filename = id + ".jpg"
        return send_file(UNDISTORT_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')

    def get_chessboard(self, id):
        filename = id + '.jpg'
        return send_file(CHESSBOARD_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')

    def get_world_coordinates(self):
        coordinate = request.get_json()

        print(coordinate)

        world_coordinates = self.camera_service.compute_image_to_world_coordinates(
            coordinate['x'], coordinate['y'], coordinate['z'])

        response = make_response(jsonify({"world_coordinates": world_coordinates}))
        response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    def set_robot_position(self):
        self.robot_position = request.get_json()
        print(self.robot_position)
        self.robot_position = {
            "center": self.camera_service.compute_image_to_world_coordinates(
            self.robot_position['center'][0], self.robot_position['center'][1], 10),
            "direction": self.robot_position['direction']
        }
        return make_response(jsonify({"message": "robot position set", "data": self.robot_position}))

    def go_to(self):
        next_position = request.get_json()

        world = self.camera_service.compute_image_to_world_coordinates(
            next_position['x'], next_position['y'], 0)

        transform = self.camera_service.compute_transform_matrix(self.robot_position['direction'], self.robot_position['center'])

        next = 4.7 * np.dot(transform, np.array([world[0], world[1], 0]))

        body = {
            'x': next.tolist()[0],
            'y': next.tolist()[1],
            "theta": np.deg2rad(self.robot_position['direction'])
        }

        try:
            go_to = requests.post("http://192.168.0.29:8080/go-to-position", json=body).json()
        except Exception as e:
            print(e)

        response = make_response(jsonify(next.tolist()))
        response.headers['Access-Control-Allow-Origin'] = "*"
        return response

    def css(self, filename):
        return send_from_directory(self.static_folder + "/css", filename)

    def js(self, filename):
        return send_from_directory(self.static_folder + "/js", filename)

    def create_calibration(self):
        directory = "../data/images/calibration"
        images_filenames = [directory + "/" + filename for filename in os.listdir(directory)]
        images = self.image_repository.load_all_images(images_filenames)
        camera_model = self.calibration_service.calibrate_from_images(images)
        return make_response(jsonify(camera_model))

    def get_calibration_images_infos(self):
        filenames = os.listdir(CALIBRATION_IMAGES_DIRECTORY)
        calibration_images = [self.create_image_dto(filename) for filename in filenames]
        calibration_images.sort(key=lambda item: item['created_at'], reverse=True)
        return calibration_images

    def create_image_dto(self, filename):
        id = filename.split('.jpg')[0]

        return {
            "name": id,
            "url": 'http://localhost:5000/images/' + filename,
            "chessboard_url": "http://localhost:5000/images/" + id + "/chessboard",
            "undistorted_url": "http://localhost:5000/images/" + id + "/undistorted",
            "created_at": os.path.getctime(CALIBRATION_IMAGES_DIRECTORY + '/' + filename)
        }

    def run(self):
        return self.api.run()
