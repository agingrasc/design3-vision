from world.worldelement import WorldElement


class DrawingArea(WorldElement):
    def __init__(self, inner_square, outer_square):
        self._inner_square = inner_square
        self._outer_square = outer_square
        self._inner_square_dimension = None

    def draw_in(self, image):
        self._inner_square.draw_in(image)
        self._outer_square.draw_in(image)

    def set_inner_square_dimension(self, inner_square_dimension):
        self._inner_square_dimension = inner_square_dimension
