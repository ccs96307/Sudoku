# -*- coding: utf-8 -*-


class Sudoku:
    def __init__(self, board=None):
        if board and len(board) == 9 and len(board[0]) == 9:
            self.board = board
        else:
            self.board = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
                          [0, 0, 3, 6, 0, 0, 0, 0, 0],
                          [0, 7, 0, 0, 9, 0, 2, 0, 0],
                          [0, 5, 0, 0, 0, 7, 0, 0, 0],
                          [0, 0, 0, 0, 4, 5, 7, 0, 0],
                          [0, 0, 0, 1, 0, 0, 0, 3, 0],
                          [0, 0, 1, 0, 0, 0, 0, 6, 8],
                          [0, 0, 8, 5, 0, 0, 0, 1, 0],
                          [0, 9, 0, 0, 0, 0, 4, 0, 0]]

        self.positionState = [[[n for n in range(1, 10)] for a in range(9)] for b in range(9)]
        self.setList = []
        self.iterTimes = 0
        self.boardNum = self.setNum()

    def clean(self):
        None


    def plotBoard(self):
        for _ in range(9):
            print(self.board[_])
        print('-------------------------------------', self.setNum())

    def onlyOneCheck(self, x, y):
        new_x, new_y = x//3*3, y//3*3
        row = self.board[x]
        column = [self.board[_][y] for _ in range(9)]
        square = [self.board[a][b] for a in range(new_x, new_x+3) for b in range(new_y, new_y+3)]

        total_collision_num_list = list(set(row+column+square))
        total_num_list = [n for n in range(1, 10)]

        for n in total_collision_num_list:
            if n in total_num_list:
                total_num_list.remove(n)

        if len(total_num_list) == 1: return total_num_list[0]
        else: return False

    def row_col(self, x, y, n):
        return n in self.board[x]

    def column_col(self, x, y, n):
        column_list = [self.board[_][y] for _ in range(9)]
        return n in column_list

    def square_col(self, x, y, n):
        new_x = x//3*3
        new_y = y//3*3
        square_list = [self.board[a][b] for a in range(new_x, new_x+3) for b in range(new_y, new_y+3)]

        if n in square_list:
            return True

    # Count the number we set into the board
    def setNum(self):
        num = 0

        for a in range(9):
            for b in range(9):
                if self.board[a][b] != 0:
                    num += 1

        return num

    def board_num_add_check(self, n):
        board_num_now = self.setNum()

        if board_num_now > n:
            return True, board_num_now
        else:
            return False, board_num_now

    def simplify_sudoku(self, n):
        for a in range(9):
            for b in range(9):
                if self.board[a][b] == 0:
                    result = self.onlyOneCheck(a, b)

                    if not result:
                        continue
                    else:
                        self.board[a][b] = result

        test, num = self.board_num_add_check(n)

        if test:
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
                if self.positionState[i][j]:
                    n = self.positionState[i][j].pop()
                    if self.row_col(i, j, n) or self.column_col(i, j, n) or self.square_col(i, j, n):
                        continue
                    else:
                        self.board[i][j] = n
                        # self.board_plot()
                        self.setList.append([i, j])
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
                    self.positionState[i][j] = [_ for _ in range(1, 10)]
                    i, j = self.setList.pop()
                    self.board[i][j] = 0

            else:
                if j == 8:
                    i += 1
                    j = 0
                else:
                    j += 1


if __name__ == '__main__':
    question = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
                [3, 4, 0, 0, 5, 0, 0, 0, 1],
                [6, 0, 5, 0, 2, 0, 4, 3, 0],
                [5, 0, 0, 0, 0, 9, 8, 1, 0],
                [0, 9, 0, 6, 0, 0, 0, 0, 5],
                [4, 0, 0, 0, 0, 1, 2, 7, 0],
                [2, 0, 8, 0, 9, 0, 1, 6, 0],
                [1, 6, 0, 0, 4, 0, 0, 0, 7],
                [0, 0, 4, 0, 0, 0, 0, 0, 0]]


    sudoku = Sudoku(question)
    i, j = sudoku.simplify_sudoku(sudoku.boardNum)
    result = sudoku.check_end()
    if result:
        print('The End')
    else:
        sudoku.run()

    sudoku.plotBoard()
