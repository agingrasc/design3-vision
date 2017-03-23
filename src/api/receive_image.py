import base64
import json
from io import BytesIO
from PIL import Image

import cv2
import numpy as np
from flask import Flask, jsonify
from flask import make_response
from flask import request

app = Flask(__name__)


def save_image(image):
    print(type(image))
    with open('image.png', 'wb') as f:
        f.write(image)


@app.route('/image/segmentation', methods=["POST"])
def receive_image():
    data = json.loads(request.json)

    try:
        image = base64.b64decode(data['image'])

        img = Image.open(BytesIO(image)).convert('RGB')

        opencv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        print(opencv_image.shape)
        cv2.imwrite('robot_image.png', opencv_image)

    except KeyError:
        print("No image in request")

    return make_response(jsonify({"message": "ok"}))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)

