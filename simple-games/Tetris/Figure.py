import random


# colors for blocks
colors = [
    (0, 0, 0),
    (0, 240, 240),
    (0, 0, 240),
    (240, 160, 0),
    (240, 240, 0),
    (0, 240, 0),
    (160, 0, 240),
    (240, 0, 0),
]


class Figure:
    x = 0
    y = 0

    # Figures Positioning
    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # J
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # L
        [[1, 2, 5, 6]],  # O
        [[6, 7, 9, 10], [1, 5, 6, 10]],  # S
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # T
        [[4, 5, 9, 10], [2, 6, 5, 9]]  # Z

    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        # eine bestimmte Figur
        self.type = random.randint(0, len(self.figures) - 1)
        # self.type = 0
        self.color = colors[self.type + 1]
        self.rotation = 0

    # gibt die Figur in bestimmter Rotation zurueck
    def image(self):
        return self.figures[self.type][self.rotation]

    # rotation ist nur nen Index, der die Position der Figur bestimmt.
    # Damit man kein ArrayOutOfBounds kriegt, muss man der Index durch Module
    # rechen.
    # type in diesem Fall bestimmt um welche Figur es ueberhaupt geht
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])
