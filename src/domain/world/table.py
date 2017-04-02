from domain.world.worldelement import WorldElement


class Table(WorldElement):
    def __init__(self, rectangle):
        self._rectangle = rectangle

    def draw_in(self, image):
        self._rectangle.draw_in(image)
