from abc import ABCMeta, abstractmethod


class WorldElementDetector(metaclass=ABCMeta):
    def __init__(self, shape_factory):
        self._shape_factory = shape_factory

    @abstractmethod
    def detect(self, image):
        pass
