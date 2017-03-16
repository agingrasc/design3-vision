import glob
import cv2
from time import sleep


class DirectoryImageSource:
    def __init__(self, directory_glob):
        self._images = [cv2.imread(filename) for filename in glob.glob(directory_glob)]
        self._current_image_index = 0

    def has_next_image(self):
        return self._current_image_index < len(self._images)

    def next_image(self):
        sleep(1)
        image = self._images[self._current_image_index]
        self._current_image_index += 1
        return image
