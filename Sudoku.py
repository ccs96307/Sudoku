# -*- coding: utf-8 -*-


class Sudoku:
    def __init__(self, board):
        if board and len(board) == 9 and len(board[0]) == 9: self.board = board
        else: raise ValueError

        # List all possible number
        self.positionState = [[[n for n in range(1, 10)] for r in range(9)] for c in range(9)]
        self.setNumberHistory = []
        self.boardNum = self.setNum()
        self.i, self.j = self.simplifyBoard()

    def plotBoard(self):
        for n in range(9): print(self.board[n])
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

    def row_col(self, x, n):
        return n in self.board[x]

    def column_col(self, y, n):
        return n in [self.board[_][y] for _ in range(9)]

    def square_col(self, x, y, n):
        new_x = x//3*3
        new_y = y//3*3
        square_list = [self.board[a][b] for a in range(new_x, new_x+3) for b in range(new_y, new_y+3)]

        if n in square_list:
            return True

    # Count the number we set into the board
    def setNum(self):
        return sum([1 for a in range(9) for b in range(9) if self.board[a][b]])

    def simplifyBoard(self):
        for a in range(9):
            for b in range(9):
                if self.board[a][b] == 0:
                    result = self.onlyOneCheck(a, b)
                    if result: self.board[a][b] = result

        return 0, 0

    def check_end(self):
        for r in range(9):
            if 0 in self.board[r]:
                return False

        return True

    def update(self):
        if self.j == 8:
            self.i += 1
            self.j = 0
        else:
            self.j += 1

    def run(self):
        while True:
            if self.board[self.i][self.j]:
                self.update()
                continue

            if self.positionState[self.i][self.j]:
                n = self.positionState[self.i][self.j].pop()
                if not (self.row_col(self.i, n) or self.column_col(self.j, n) or self.square_col(self.i, self.j, n)):
                    self.board[self.i][self.j] = n
                    self.setNumberHistory.append([self.i, self.j])
                    result = self.check_end()

                    if result:
                        break

                    self.update()

            else:
                self.positionState[self.i][self.j] = [_ for _ in range(1, 10)]
                self.i, self.j = self.setNumberHistory.pop()
                self.board[self.i][self.j] = 0


if __name__ == '__main__':
    question = [[1, 0, 0, 0, 7, 9, 0, 8, 0],
                [5, 9, 0, 0, 0, 2, 7, 3, 4],
                [7, 0, 0, 5, 3, 8, 0, 0, 9],
                [0, 0, 0, 3, 4, 0, 0, 2, 0],
                [3, 4, 0, 7, 2, 0, 0, 5, 1],
                [0, 5, 0, 8, 0, 0, 0, 0, 3],
                [0, 0, 7, 9, 0, 3, 5, 0, 8],
                [9, 1, 0, 0, 0, 0, 3, 0, 0],
                [6, 0, 0, 0, 0, 0, 1, 9, 0]]

    sudoku = Sudoku(question)
    sudoku.run()
    sudoku.plotBoard()
