import pygame

from Tetris import Tetris
from Figure import Figure

# initialiyation of pygame
pygame.init()

""" SCREEN """

# display
screen = pygame.display.set_mode((380, 670))
# window name
pygame.display.set_caption("Tetris")


""" VARIABLES """

# quit the game
done = False
# game speed
fps = 2
# clock
clock = pygame.time.Clock()
# points
counter = 0
#
zoom = 30
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

# check if button pressed
pressing_down = pressing_left = pressing_right = False

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

""" GAME """
game = Tetris(20, 10)


# catch button clicks
while not done:
    if game.state == "start":
        game.go_down()

    # analog to js
    for event in pygame.event.get():
        # make close button responsive
        if event.type == pygame.QUIT:
            done = True

        # button arrow up is for figure's rotation responsive
        # btn arrow down speeds up dropping a figure
        # Taste pfeile nach links ist fuer die Verschiebung des Blocks um einen Block nach links zustaendig
        # Taste pfeile nach rechts ist fuer die Verschiebung des Blocks um einen Block nach rechts zustaendig
        #
        # Bei k_Up verbietet man den langen Druecken der Taste. D.h. einen Druck entspricht einer Rotation.
        # langhalten ist sinnlos
        # K_Down, K_left, k_right unterstuetzen die Moeglichkeit, dass die Taste langgehalten wird und
        # alle Aktionen werden dabei erledigt

        # taste is gedrueckt
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game.rotate()
            if event.key == pygame.K_DOWN:
                pressing_down = True
            if event.key == pygame.K_LEFT:
                pressing_left = True
            if event.key == pygame.K_RIGHT:
                pressing_right = True

        if pressing_down:
            game.down()
        if pressing_left:
            game.left()
        if pressing_right:
            game.right()

        # die Taste ist losgelassen
        if event.type == pygame.KEYUP:

            if event.key == pygame.K_DOWN:
                pressing_down = False
            if event.key == pygame.K_LEFT:
                pressing_left = False
            if event.key == pygame.K_RIGHT:
                pressing_right = False

    screen.fill(color=WHITE)

    # Zeichnen von Figuren auf display
    for i in range(game.height):
        for j in range(game.width):
            if game.field[i][j] == 0:
                color = GRAY
                just_border = 1
            else:
                color = colors[game.field[i][j]]
                just_border = 0
            # wo angezeigt wird, farbe, platz des blocks
            pygame.draw.rect(screen, color, [30 + j * zoom, 30 + i * zoom, zoom, zoom], just_border)
    if game.Figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.Figure.image():
                    pygame.draw.rect(screen, game.Figure.color,
                                     [30 + (j + game.Figure.x) * zoom, 30 + (i + game.Figure.y) * zoom, zoom, zoom])

    gameover_font = pygame.font.SysFont("Calibri", 65, True, False)
    text_gameover = gameover_font.render("Game Over!\nPress Esc", True, (255, 215, 0))

    if game.state == "gameover":
        screen.blit(text_gameover,  [30, 250])

    score_font = pygame.font.SysFont("Calibri", 15, True, False)
    text_score = gameover_font.render("Score: " + str(game.score), True, (0, 0, 0))
    screen.blit(text_score, [0, 0])

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
