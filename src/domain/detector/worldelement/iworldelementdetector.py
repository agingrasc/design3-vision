from abc import ABCMeta, abstractmethod


class IWorldElementDetector(metaclass=ABCMeta):
    @abstractmethod
    def detect(self, image):
        pass
