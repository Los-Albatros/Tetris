import sys
import pygame
import random
from pygame.locals import *

pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

font_large = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 36)

pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

tetrimino_S = [['.....',
                '.....',
                '..00.',
                '.00..',
                '.....'],
               ['.....',
                '..0..',
                '..00.',
                '...0.',
                '.....']]

tetrimino_Z = [['.....',
                '.....',
                '.00..',
                '..00.',
                '.....'],
               ['.....',
                '..0..',
                '.00..',
                '.0...',
                '.....']]

tetrimino_I = [['..0..',
                '..0..',
                '..0..',
                '..0..',
                '.....'],
               ['.....',
                '0000.',
                '.....',
                '.....',
                '.....']]

tetrimino_O = [['.....',
                '.....',
                '.00..',
                '.00..',
                '.....']]

tetrimino_J = [['.....',
                '.0...',
                '.000.',
                '.....',
                '.....'],
               ['.....',
                '..00.',
                '..0..',
                '..0..',
                '.....'],
               ['.....',
                '.....',
                '.000.',
                '...0.',
                '.....'],
               ['.....',
                '..0..',
                '..0..',
                '.00..',
                '.....']]

tetrimino_L = [['.....',
                '...0.',
                '.000.',
                '.....',
                '.....'],
               ['.....',
                '..0..',
                '..0..',
                '..00.',
                '.....'],
               ['.....',
                '.....',
                '.000.',
                '.0...',
                '.....'],
               ['.....',
                '.00..',
                '..0..',
                '..0..',
                '.....']]

tetrimino_T = [['.....',
                '..0..',
                '.000.',
                '.....',
                '.....'],
               ['.....',
                '..0..',
                '..00.',
                '..0..',
                '.....'],
               ['.....',
                '.....',
                '.000.',
                '..0..',
                '.....'],
               ['.....',
                '..0..',
                '.00..',
                '..0..',
                '.....']]

shapes = [tetrimino_S, tetrimino_Z, tetrimino_I, tetrimino_O, tetrimino_J, tetrimino_L, tetrimino_T]
shape_colors = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 165, 20), (80, 60, 205), (128, 0, 128)]


class Piece(object):  # *
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos):  # *
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    layout = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(layout):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, color):
    label = font_large.render(text, 1, color)

    surface.blit(label, (
        top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))


def clear_rows(grid, locked):
    inc = 0
    ind = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except KeyError:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda e: e[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    label = font_small.render('Next Shape', 1, WHITE)

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    layout = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(layout):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color,
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))


def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()

    label = font_small.render('Score: ' + str(score), 1, WHITE)

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    draw_grid(surface, grid)
    pygame.draw.rect(surface, WHITE, (top_left_x - 3, top_left_y - 3, play_width + 6, play_height + 6), 4)


def pause():
    text_pause = font_large.render("Pause", True, YELLOW)
    rect = pygame.Rect(10, 10, text_pause.get_width(), text_pause.get_height())
    win.blit(text_pause, rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                if event.key == pygame.K_p:
                    pygame.draw.rect(win, BLACK, rect)
                    pygame.display.update()
                    return
            elif event.type == JOYBUTTONDOWN:
                if event.button == 7:
                    pygame.draw.rect(win, BLACK, rect)
                    pygame.display.update()
                    return
                elif event.button == 1:
                    main_menu()


def game():  # *
    locked_positions = {}

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0
    MOVE_DELAY = 100
    move_timer = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                if event.key == pygame.K_p:
                    pause()
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                if event.key == pygame.K_DOWN:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
            elif event.type == JOYHATMOTION:
                if event.value == (-1, 0):  # left
                    current_piece.x -= 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1
                elif event.value == (1, 0):  # right
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1
                elif event.value == (0, 1):  # up
                    current_piece.rotation += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                elif event.value == (0, -1):  # down
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
            elif event.type == JOYBUTTONDOWN:
                if event.button == 7:
                    pause()

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            if pygame.time.get_ticks() - move_timer > MOVE_DELAY:
                for pos in shape_pos:
                    p = (pos[0], pos[1])
                    locked_positions[p] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                change_piece = False
                score += clear_rows(grid, locked_positions) * 10
                move_timer = pygame.time.get_ticks()

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", WHITE)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False


def quit_game():
    pygame.quit()
    sys.exit()


def main_menu():
    global joystick
    clock = pygame.time.Clock()
    button_width = 200
    button_height = 50
    button_left = win.get_width() // 2 - button_width // 2
    button_top = 200
    button_play = pygame.Rect(button_left, button_top, button_width, button_height)
    button_exit = pygame.Rect(button_left, button_top + 200, button_width, button_height)

    while True:
        win.fill(BLACK)
        text_play = font_small.render("Play", True, WHITE)
        text_exit = font_small.render("Exit", True, WHITE)
        mx, my = pygame.mouse.get_pos()
        play_color = (0, 0, 155)
        exit_color = (155, 0, 0)
        if button_play.collidepoint(mx, my):
            play_color = BLUE
        elif button_exit.collidepoint(mx, my):
            exit_color = RED

        buttons = [(button_play, play_color), (button_exit, exit_color)]

        for button in buttons:
            pygame.draw.rect(win, button[1], button[0])

        win.blit(text_play,
                 text_play.get_rect(center=(button_left + button_width // 2, button_top + button_height // 2)))
        win.blit(text_exit,
                 text_exit.get_rect(center=(button_left + button_width // 2, button_top + 200 + button_height // 2)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(mx, my):
                    game()
                if button_exit.collidepoint(mx, my):
                    quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                if event.key == pygame.K_g:
                    game()
            elif event.type == JOYBUTTONDOWN:
                if event.button == 7:
                    game()
                elif event.button == 1:
                    quit_game()
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
