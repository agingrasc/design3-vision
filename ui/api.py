import os

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import send_file
from flask import send_from_directory

CALIBRATION_IMAGES_DIRECTORY = '../calibration'
CHESSBOARD_IMAGES_DIRECTORY = '../chessboard/'

app = Flask(__name__)


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
    return send_from_directory('static', 'index.html')


@app.route('/images/<path:filename>', methods=["GET"])
def get_image(filename):
    return send_file(CALIBRATION_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')


@app.route('/images/<string:id>/chessboard', methods=["GET"])
def get_chessboard(id):
    filename = id + '.jpg'
    return send_file(CHESSBOARD_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')


@app.route('/css/<path:filename>', methods=['GET'])
def css(filename):
    return send_from_directory('static/css', filename)


@app.route('/js/<path:filename>', methods=['GET'])
def js(filename):
    return send_from_directory('static/js', filename)


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
        "chessboard_url": "http://localhost:5000/images/" + filename.split('.jpg')[0] + "/chessboard",
        "created_at": os.path.getctime(CALIBRATION_IMAGES_DIRECTORY + '/' + filename)
    }


if __name__ == "__main__":
    app.run()
