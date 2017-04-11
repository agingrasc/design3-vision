import datetime
import json
from time import sleep

import cv2

from websocket import create_connection

from infrastructure.imagesource.savevideoimagesource import SaveVideoImageSource
from src.infrastructure.imagesource.httpimagesource import HTTPImageSource
from src.service.image.imagesegmentation import segment_image
from src.infrastructure.messageassembler import MessageAssembler

ROBOT_VIDEO_SERVICE_URL = "http://192.168.0.27:4040/take-picture"

if __name__ == '__main__':
    connection = create_connection("ws://localhost:3000")
    message_assembler = MessageAssembler()

    index = 0
    image_source = HTTPImageSource(ROBOT_VIDEO_SERVICE_URL)
    # image_source = SaveVideoImageSource('/Users/jeansebastien/Desktop/videos/robot_video2.avi')

    while True:
        print('Fetching image: {}'.format(datetime.datetime.now()))

        image = image_source.next_image()

        try:
            found_segments, inner_figure, center_of_mass, figure_mask = segment_image(image)
            figure_mask = cv2.resize(figure_mask, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC)
            cv2.imshow('thres', inner_figure)
            cv2.imshow('figure mask', figure_mask)
        except Exception as e:
            print(type(e).__name__)

        image = cv2.resize(image, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC)

        cv2.imshow('Image', image)

        # connection.send(json.dumps({"headers": "push_robot_feed", "data": {"image": message_assembler.prepare_image(image) }}))

        # cv2.imwrite('../data/images/robot_feed/image{}.jpg'.format(index), image)
        # index += 1
        cv2.waitKey(1)
