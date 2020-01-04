import time


# Settings
start_time = time.time()


class Sudoku():
    def __init__(self):
        self.board = [[8, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 3, 6, 0, 0, 0, 0, 0],
                      [0, 7, 0, 0, 9, 0, 2, 0, 0],
                      [0, 5, 0, 0, 0, 7, 0, 0, 0],
                      [0, 0, 0, 0, 4, 5, 7, 0, 0],
                      [0, 0, 0, 1, 0, 0, 0, 3, 0],
                      [0, 0, 1, 0, 0, 0, 0, 6, 8],
                      [0, 0, 8, 5, 0, 0, 0, 1, 0],
                      [0, 9, 0, 0, 0, 0, 4, 0, 0]]

        self.size = len(self.board[0])
        self.choices = [-1 if self.board[i][j] else 1
                        for i in range(self.size)
                        for j in range(self.size)]
        
        self.x = 0
        self.y = 0

    def plot(self):
        cn = 0
        for row in self.board:
            print(row)

            for _ in row:
                if _ != 0:
                    cn += 1

        print('===========================', cn)

    def row(self, n):
        return n in self.board[self.y]

    def col(self, n):
        return n in [self.board[_][self.x]
                     for _ in range(9)]

    def square(self, n):
        return n in [self.board[b][a]
                     for a in range(self.x//3*3, self.x//3*3+3)
                     for b in range(self.y//3*3, self.y//3*3+3)]

    def collision(self, n):
        if self.row(n) or\
           self.col(n) or\
           self.square(n):
            return True
        else: return False

    def backward(self):
        self.board[self.y][self.x] = 0
        self.choices[self.c] = 1
        if self.x == 0:
            self.x = 8
            self.y -= 1
        else:
            self.x -= 1

        while self.choices[self.y * self.size + self.x] == -1:
            if self.x == 0:
                self.x = 8
                self.y -= 1
            else:
                self.x -= 1

    def forward(self):
        if self.x == 8:
            self.x = 0
            self.y += 1
        else:
            self.x += 1

    def isEnd(self):
        for row in self.board:
            if 0 in row:
                return False

        return True

    def run(self):
        while not self.isEnd():
            self.c = self.y*self.size+self.x
            if self.choices[self.c] != -1:
                if self.collision(self.choices[self.c]):

                    # Error
                    if self.choices[self.c] != 9:
                        self.choices[self.c] += 1
                        continue

                    # Back
                    else:
                        self.backward()

                # Success
                else:
                    self.board[self.y][self.x] = self.choices[self.c]
                    # plot()

                    self.forward()

            else:
                self.forward()

        self.plot()
        print('time:', time.time()-start_time)


if __name__ == '__main__':
    s = Sudoku()
    s.run()
