from abc import ABCMeta
from abc import abstractmethod


class ImageSource(metaclass=ABCMeta):
    @abstractmethod
    def has_next_image(self):
        pass

    @abstractmethod
    def next_image(self):
        pass
