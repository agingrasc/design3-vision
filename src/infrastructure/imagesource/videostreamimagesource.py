import datetime
from threading import Thread
from time import sleep

import cv2

import config


class VideoStreamImageSource:
    def __init__(self, camera_index, write=False):
        self._cap = cv2.VideoCapture(camera_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAP_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAP_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS, 15)
        self._write = write
        if self._write:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            self._out = cv2.VideoWriter()
            self._out.open('../data/videos/{}.avi'.format(datetime.datetime.now().isoformat()), fourcc, 15,
                           (config.CAP_WIDTH, config.CAP_HEIGHT),
                           True)

        self._has_next_image, self._next_image = self._cap.read()
        self._capture_thread = Thread(target=self._update_image).start()

        sleep(3)

    def has_next_image(self):
        return self._cap.isOpened()

    def _update_image(self):
        while self._cap.isOpened():
            self._has_next_image, self._next_image = self._cap.read()
            if self._has_next_image:
                if self._write:
                    self._out.write(self._next_image)

    def next_image(self):
        if self.has_next_image():
            return self._next_image
        else:
            return None
