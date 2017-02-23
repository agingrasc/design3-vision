import cv2


class Image:
    def __init__(self, id, path, destination, data=None):
        self.id = id
        self.path = path
        self.destination = destination
        self.data = data
        self._loaded = False

    def load(self):
        if self._loaded is False:
            self.data = cv2.imread(self.path)

    def save(self):
        cv2.imwrite(self.destination, self.data)

    def is_loaded(self):
        return self._loaded
