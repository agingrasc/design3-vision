import base64
import cv2
import requests
import numpy as np
import datetime

from PIL import Image
from io import BytesIO

from src.service.image.imagesegmentation import segment_image

if __name__ == '__main__':
    index = 0
    while True:
        print('Fetching image: {}'.format(datetime.datetime.now()))
        data = requests.post(url="http://192.168.0.27:4040/take-picture").json()

        image = base64.b64decode(data['image'])
        img = Image.open(BytesIO(image)).convert('RGB')
        image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        try:
            found_segments, inner_figure, center_of_mass, figure_mask = segment_image(image)
            cv2.imshow('thres', figure_mask)

        except Exception as e:
            print(e)

        image = cv2.resize(image, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_CUBIC)

        cv2.imshow('image', image)
        cv2.imwrite('./data/images/robot_feed/image{}.jpg'.format(index), image)
        index += 1
        cv2.waitKey(1)
