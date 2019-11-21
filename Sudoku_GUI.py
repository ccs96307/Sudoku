# -*- coding: utf-8 -*-
import sys
import pygame
from Sudoku import Sudoku


# preset
pygame.init()
pygame.display.set_caption('Sudoku')
screen = pygame.display.set_mode([1200, 800])
my_font = pygame.font.Font('Fonts/mingliu.ttc', 32)
running = True

board = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
         [6, 0, 0, 1, 9, 5, 0, 0, 0],
         [0, 9, 8, 0, 0, 0, 0, 6, 0],
         [8, 0, 0, 0, 6, 0, 0, 0, 3],
         [4, 0, 0, 8, 0, 3, 0, 0, 1],
         [7, 0, 0, 0, 2, 0, 0, 0, 6],
         [0, 6, 0, 0, 0, 0, 2, 8, 0],
         [0, 0, 0, 4, 1, 9, 0, 0, 5],
         [0, 0, 0, 0, 8, 0, 0, 7, 9]]

get0 = [0, 650, 350, 'C']
get10 = [0, 600, 350, 'S']
get1 = [0, 650, 300, '1']
get2 = [0, 650, 250, '2']
get3 = [0, 650, 200, '3']
get4 = [0, 650, 150, '4']
get5 = [0, 650, 100, '5']
get6 = [0, 600, 300, '6']
get7 = [0, 600, 250, '7']
get8 = [0, 600, 200, '8']
get9 = [0, 600, 150, '9']
get_set = [get0, get10, get1, get2, get3, get4, get5, get6, get7, get8, get9]

# Color
white = (255, 255, 255)
black = (0, 0, 0)
gray = (120, 120, 120)
red = (255, 0, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)


def init():
    global board
    board = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0]]


def run():
    global board
    sudoku = Sudoku(board)
    i, j = sudoku.simplify_sudoku(sudoku.board_num)
    result = sudoku.check_end()
    if result:
        print('The End')
    else:
        sudoku.run()

    board = sudoku.board


def check_get():
    for get in get_set:
        if get[0] == 1 and get[3] != 'S' and get[3] != 'C':
            mouse_x, mouse_y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
            pygame.draw.rect(screen, white, [mouse_x-20-6, mouse_y-20, 40, 40])
            screen.blit(my_font.render(get[3], True, black), (mouse_x+5-20, mouse_y+5-20))
        elif get[0] == 1 and get[3] == 'C':
            init()
            get[0] = 0
        elif get[0] == 1 and get[3] == 'S':
            run()
            get[0] = 0
        elif get[0] == 0:
            pygame.draw.rect(screen, white, [get[1], get[2], 40, 40])
            screen.blit(my_font.render(get[3], True, black), (get[1]+12, get[2]+5))


def start():
    global running

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mouse.set_visible(False)
                mouse_x, mouse_y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]

                for get in get_set:
                    if get[0] == 0:
                        min_x = get[1]
                        max_x = get[1]+40
                        min_y = get[2]
                        max_y = get[2]+40
                        if min_x < mouse_x < max_x and min_y < mouse_y < max_y:
                            get[0] = 1

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]

                for i in range(9):
                    for j in range(9):
                        if j*41+200+j//3 < mouse_x < j*41+200+40 and i*41+100 < mouse_y < i*41+100+40:
                            for get in get_set:
                                if get[0]:
                                    board[i][j] = get[3]
                                    break

                for get in get_set:
                    get[0] = 0
                pygame.mouse.set_visible(True)

        # Plot
        screen.fill(black)

        for i in range(9):
            for j in range(9):
                pygame.draw.rect(screen, white, [j*41+200+j//3, i*41+100+i//3, 40, 40])

                if board[i][j]:
                    text_surface = my_font.render(str(board[i][j]), True, black)
                    screen.blit(text_surface, (j*41+200+12+j//3, i*41+100+3+i//3))

        check_get()

        # Update
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    start()
