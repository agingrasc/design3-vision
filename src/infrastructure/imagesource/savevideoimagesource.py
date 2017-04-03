import cv2

from infrastructure.imagesource.imagesource import ImageSource


class SaveVideoImageSource(ImageSource):
    def __init__(self, filename):
        self._cap = cv2.VideoCapture(filename)
        self._has_next_image, self._next_image = self._cap.read()

    def has_next_image(self):
        return self._cap.isOpened()

    def next_image(self):
        if self.has_next_image():
            self._has_next_image, self._next_image = self._cap.read()
            return self._next_image
        else:
            return None
