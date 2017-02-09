import os

from flask import Flask, jsonify, make_response, send_file


app = Flask(__name__)


@app.route('/images-infos', methods=["GET"])
def send_image_infos():
    calibration_images = [create_image_response_object(filename) for filename in os.listdir('./calibration')]
    raw_images = [create_image_response_object(filename) for filename in os.listdir('./raw')]

    response_body = {
        "calibration": { "images": calibration_images }
    }

    response = make_response(jsonify(response_body))
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response


def create_image_response_object(filename):
    return { "name": filename, "src": 'http://localhost:5000/images/' + filename }


@app.route('/images/<path:filename>', methods=["GET"])
def send_image(filename):
    return send_file('./calibration/' + filename, mimetype='image/jpeg')


if __name__ == "__main__":
    app.run()
