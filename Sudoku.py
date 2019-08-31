# -*- coding: utf-8 -*-


class Sudoku:
    def __init__(self, board=None):
        self.board = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [3, 4, 0, 0, 5, 0, 0, 0, 1],
                      [6, 0, 5, 0, 2, 0, 4, 3, 0],
                      [5, 0, 0, 0, 0, 9, 8, 1, 0],
                      [0, 9, 0, 6, 0, 0, 0, 0, 5],
                      [4, 0, 0, 0, 0, 1, 2, 7, 0],
                      [2, 0, 8, 0, 9, 0, 1, 6, 0],
                      [1, 6, 0, 0, 4, 0, 0, 0, 7],
                      [0, 0, 4, 0, 0, 0, 0, 0, 0]]
        if board:
            self.board = board
        self.position_state = [[[n for n in range(1, 10)] for a in range(9)] for b in range(9)]
        self.set_list = []
        self.iter_times = 0
        self.board_num = self.set_num()

    def board_plot(self):
        for _ in range(9):
            print(self.board[_])
        print('-------------------------------------', self.set_num())

    def only_one_check(self, x, y):
        row = self.board[x]
        column = [self.board[_][y] for _ in range(9)]
        new_x = x//3*3
        new_y = y//3*3
        square = [self.board[a][b] for a in range(new_x, new_x+3) for b in range(new_y, new_y+3)]

        total_collision_num_list = list(set(row + column + square))
        total_num_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        for _ in total_collision_num_list:
            if _ in total_num_list:
                total_num_list.remove(_)

        if len(total_num_list) == 1:
            return total_num_list[0]
        else:
            return False

    def row_col(self, x, y, n):
        if n in self.board[x]:
            return True

    def column_col(self, x, y, n):
        column_list = [self.board[_][y] for _ in range(9)]

        if n in column_list:
            return True

    def square_col(self, x, y, n):
        new_x = x//3*3
        new_y = y//3*3
        square_list = [self.board[a][b] for a in range(new_x, new_x+3) for b in range(new_y, new_y+3)]

        if n in square_list:
            return True

    # count the number we set into the board
    def set_num(self):
        num = 0

        for a in range(9):
            for b in range(9):
                if self.board[a][b] != 0:
                    num += 1

        return num

    def board_num_add_check(self, n):
        board_num_now = self.set_num()

        if board_num_now > n:
            return True, board_num_now
        else:
            return False, board_num_now

    def simplify_sudoku(self, n):
        self.board_plot()
        for a in range(9):
            for b in range(9):
                if self.board[a][b] == 0:
                    result = self.only_one_check(a, b)

                    if not result:
                        continue
                    else:
                        self.board[a][b] = result

        test, num = self.board_num_add_check(n)

        if test:
            self.board_plot()
            x, y = self.simplify_sudoku(num)
            return x, y
        else:
            return 0, 0

    def check_end(self):
        for a in range(9):
            if 0 in self.board[a]:
                return False

        return True

    def run(self):
        global i, j

        while True:
            if self.board[i][j] == 0:
                if self.position_state[i][j]:
                    n = self.position_state[i][j].pop()
                    if self.row_col(i, j, n) or self.column_col(i, j, n) or self.square_col(i, j, n):
                        continue
                    else:
                        self.board[i][j] = n
                        self.board_plot()
                        self.set_list.append([i, j])
                        result = self.check_end()

                        if not result:
                            if j == 8:
                                i += 1
                                j = 0
                            else:
                                j += 1
                        else:
                            print('The End')
                            break

                else:
                    self.position_state[i][j] = [_ for _ in range(1, 10)]
                    i, j = self.set_list.pop()
                    print(i, j)
                    self.board[i][j] = 0

            else:
                if j == 8:
                    i += 1
                    j = 0
                else:
                    j += 1


if __name__ == '__main__':
    sudoku = Sudoku()
    i, j = sudoku.simplify_sudoku(sudoku.board_num)
    result = sudoku.check_end()
    if result:
        print('The End')
    else:
        sudoku.run()
