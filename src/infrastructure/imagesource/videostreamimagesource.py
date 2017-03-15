import cv2


class VideoStreamImageSource:
    def __init__(self, camera_index):
        self._cap = cv2.VideoCapture(camera_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
        self._cap.set(cv2.CAP_PROP_FPS, 15)
        self._has_next_image, self._next_image = self._cap.read()

    def has_next_image(self):
        return self._cap.isOpened() and self._has_next_image

    def next_image(self):
        self._has_next_image, self._next_image = self._cap.read()
        if self.has_next_image():
            return self._next_image
        else:
            return None
