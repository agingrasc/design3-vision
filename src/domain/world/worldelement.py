from abc import ABCMeta, abstractmethod


class WorldElement(metaclass=ABCMeta):
    @abstractmethod
    def draw_in(self, image):
        pass
