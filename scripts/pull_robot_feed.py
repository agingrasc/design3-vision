import datetime

import cv2

from src.infrastructure.imagesource.httpimagesource import HTTPImageSource
from src.service.image.imagesegmentation import segment_image

ROBOT_VIDEO_SERVICE_URL = "http://192.168.0.27:4040/take-picture"

if __name__ == '__main__':
    index = 0
    image_source = HTTPImageSource(ROBOT_VIDEO_SERVICE_URL)

    while True:
        print('Fetching image: {}'.format(datetime.datetime.now()))

        image = image_source.next_image()

        try:
            found_segments, inner_figure, center_of_mass, figure_mask = segment_image(image)
            cv2.imshow('thres', figure_mask)

        except Exception as e:
            print(e)

        image = cv2.resize(image, None, fx=0.7, fy=0.7, interpolation=cv2.INTER_CUBIC)

        cv2.imshow('image', image)
        # cv2.imwrite('../data/images/robot_feed/image{}.jpg'.format(index), image)
        index += 1
        cv2.waitKey(1)
