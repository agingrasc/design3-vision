from threading import Thread
from time import sleep

import cv2


class VideoStreamImageSource:
    def __init__(self, camera_index):
        self._cap = cv2.VideoCapture(camera_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
        self._cap.set(cv2.CAP_PROP_FPS, 15)
        self._has_next_image, self._next_image = self._cap.read()
        self._capture_thread = Thread(target=self._update_image).start()
        sleep(2)

    def has_next_image(self):
        return self._cap.isOpened()

    def _update_image(self):
        while self._cap.isOpened():
            self._has_next_image, self._next_image = self._cap.read()

    def next_image(self):
        if self.has_next_image():
            return self._next_image
        else:
            return None
