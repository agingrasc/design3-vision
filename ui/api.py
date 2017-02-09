import os

from flask import Flask
from flask import jsonify
from flask import make_response
from flask import send_file
from flask import send_from_directory

CALIBRATION_IMAGES_DIRECTORY = '../calibration'

app = Flask(__name__)


@app.route('/images-infos', methods=["GET"])
def send_image_infos():
    calibration_images = [create_image_response_object(filename) for filename in
                          os.listdir(CALIBRATION_IMAGES_DIRECTORY)]

    calibration_images.sort(key=lambda item: item['created_at'], reverse=True)

    response_body = {
        "calibration": {
            "images": calibration_images
        }
    }

    response = make_response(jsonify(response_body))
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response


@app.route('/', methods=["GET"])
def index():
    return send_from_directory('static/app', 'index.html')


@app.route('/css/<path:filename>', methods=['GET'])
def css(filename):
    return send_from_directory('static/app/css', filename)


@app.route('/js/<path:filename>', methods=['GET'])
def js(filename):
    return send_from_directory('static/app/js', filename)


@app.route('/images/<path:filename>', methods=["GET"])
def send_image(filename):
    return send_file(CALIBRATION_IMAGES_DIRECTORY + "/" + filename, mimetype='image/jpeg')


def create_image_response_object(filename):
    return {
        "name": filename,
        "src": 'http://localhost:5000/images/' + filename,
        "created_at": os.path.getctime(CALIBRATION_IMAGES_DIRECTORY + '/' + filename)
    }


if __name__ == "__main__":
    app.run()
