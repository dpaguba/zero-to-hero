class Tetris:
    height = 0
    width = 0
    field = []
    score = 0
    state = "start"

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"

        # Bestimmung der Position von Figuren. Wenn 0 - nichts, 1 - besetzt
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)

            self.field.append(new_line)
