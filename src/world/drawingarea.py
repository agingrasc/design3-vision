class DrawingArea:
    def __init__(self, inner_square, outer_square):
        self._inner_square = inner_square
        self._outer_square = outer_square

    def draw_in(self, image):
        self._inner_square.draw_in(image)
        self._outer_square.draw_in(image)
