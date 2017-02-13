import os
import json

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from flask import send_file
from flask import send_from_directory

from camera.camera import Camera

CALIBRATION_IMAGES_DIRECTORY = './data/images/calibration'
CHESSBOARD_IMAGES_DIRECTORY = './data/images/chessboard/'
UNDISTORT_IMAGES_DIRECTORY = './data/images/undistort/'
CONFIG_DIRECTORY = './config/'
STATIC_FOLDER = './static'

app = Flask(__name__)
camera = Camera()
camera.load_camera_model(os.path.abspath('./config/camera_matrix.json'))


@app.route('/images-infos', methods=["GET"])
def send_image_infos():
    response_body = {
        "calibration": {
            "images": get_calibration_images_infos()
        }
    }

    response = make_response(jsonify(response_body))
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response


@app.route('/', methods=["GET"])
def index():
    return send_from_directory(STATIC_FOLDER, 'index.html')


@app.route('/images/<path:filename>', methods=["GET"])
def get_image(filename):
    return send_file(CALIBRATION_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')


@app.route('/images/<string:id>/undistorted', methods=["GET"])
def get_undistorted_image(id):
    filename = id + ".jpg"
    return send_file(UNDISTORT_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')


@app.route('/images/<string:id>/chessboard', methods=["GET"])
def get_chessboard(id):
    filename = id + '.jpg'
    return send_file(CHESSBOARD_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')


@app.route('/camera_parameters', methods=["GET"])
def get_camera_parameters():
    return send_from_directory(CONFIG_DIRECTORY, 'camera_matrix.json')


@app.route('/world_coordinates', methods=['POST'])
def get_world_coordinates():
    coordinate = request.get_json()
    world_coordinates = camera.compute_image_to_world_coordinate(coordinate['x'], coordinate['y'], 0)
    return make_response(jsonify({"world_coordinates": world_coordinates}))


@app.route('/css/<path:filename>', methods=['GET'])
def css(filename):
    return send_from_directory(STATIC_FOLDER + "/css", filename)


@app.route('/js/<path:filename>', methods=['GET'])
def js(filename):
    return send_from_directory(STATIC_FOLDER + "/js", filename)


def get_calibration_images_infos():
    filenames = os.listdir(CALIBRATION_IMAGES_DIRECTORY)
    calibration_images = [create_image_dto(filename) for filename in filenames]
    calibration_images.sort(key=lambda item: item['created_at'], reverse=True)
    return calibration_images


def create_image_dto(filename):
    id = filename.split('.jpg')[0]

    return {
        "name": id,
        "url": 'http://localhost:5000/images/' + filename,
        "chessboard_url": "http://localhost:5000/images/" + id + "/chessboard",
        "undistorted_url": "http://localhost:5000/images/" + id + "/undistorted",
        "created_at": os.path.getctime(CALIBRATION_IMAGES_DIRECTORY + '/' + filename)
    }


if __name__ == "__main__":
    app.run()
