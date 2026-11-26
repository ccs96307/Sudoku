"""Sudoku rules, solving, and puzzle generation."""

import random
from typing import Iterable, Optional

Grid = list[list[int]]
_DIGITS = set(range(1, 10))


def is_valid(grid: Grid) -> bool:
    """Return whether a grid has no duplicate nonzero values."""
    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        return False
    for row in grid:
        values = [value for value in row if value]
        if any(value not in _DIGITS for value in values):
            return False
        if len(values) != len(set(values)):
            return False
    for index in range(9):
        column = [grid[row][index] for row in range(9)]
        if not _unique_nonzero(column):
            return False
    for box_row in range(0, 9, 3):
        for box_column in range(0, 9, 3):
            box = [grid[row][column]
                   for row in range(box_row, box_row + 3)
                   for column in range(box_column, box_column + 3)]
            if not _unique_nonzero(box):
                return False
    return True


def _unique_nonzero(values: Iterable[int]) -> bool:
    present = [value for value in values if value]
    return all(value in _DIGITS for value in present) and len(present) == len(
        set(present)
    )


def candidates(grid: Grid, row: int, column: int) -> set[int]:
    """Return legal digits for an empty cell."""
    if grid[row][column]:
        return set()
    used = set(grid[row])
    used.update(grid[index][column] for index in range(9))
    box_row, box_column = row // 3 * 3, column // 3 * 3
    used.update(grid[r][c] for r in range(box_row, box_row + 3)
                for c in range(box_column, box_column + 3))
    return _DIGITS - used


def solve(grid: Grid, *, randomize: bool = False) -> Optional[Grid]:
    """Return a solved copy of grid, or None when it is unsolvable."""
    board = [row[:] for row in grid]
    if not is_valid(board):
        return None

    def search() -> bool:
        best_cell = None
        best_options = None
        for row in range(9):
            for column in range(9):
                if board[row][column] == 0:
                    options = list(candidates(board, row, column))
                    if not options:
                        return False
                    if best_options is None or len(options) < len(best_options):
                        best_cell, best_options = (row, column), options
                        if len(options) == 1:
                            break
            if best_options is not None and len(best_options) == 1:
                break
        if best_cell is None:
            return True
        if randomize:
            random.shuffle(best_options)
        row, column = best_cell
        for value in best_options:
            board[row][column] = value
            if search():
                return True
        board[row][column] = 0
        return False

    return board if search() else None


def count_solutions(grid: Grid, limit: int = 2) -> int:
    """Count solutions, stopping at limit."""
    board = [row[:] for row in grid]
    if not is_valid(board):
        return 0
    count = 0

    def search() -> None:
        nonlocal count
        if count >= limit:
            return
        best_cell = None
        best_options = None
        for row in range(9):
            for column in range(9):
                if board[row][column] == 0:
                    options = candidates(board, row, column)
                    if not options:
                        return
                    if best_options is None or len(options) < len(best_options):
                        best_cell, best_options = (row, column), options
        if best_cell is None:
            count += 1
            return
        row, column = best_cell
        for value in best_options:
            board[row][column] = value
            search()
            board[row][column] = 0
            if count >= limit:
                return

    search()
    return count


def generate(difficulty: str = "medium") -> tuple[Grid, Grid]:
    """Generate a puzzle and its unique solution."""
    target_clues = {"easy": 40, "medium": 34, "hard": 29, "expert": 25}
    if difficulty not in target_clues:
        raise ValueError(f"Unknown difficulty: {difficulty}")
    solution = solve([[0] * 9 for _ in range(9)], randomize=True)
    assert solution is not None
    puzzle = [row[:] for row in solution]
    cells = list(range(81))
    random.shuffle(cells)
    clues = 81
    for cell in cells:
        if clues <= target_clues[difficulty]:
            break
        row, column = divmod(cell, 9)
        value = puzzle[row][column]
        puzzle[row][column] = 0
        if count_solutions(puzzle) == 1:
            clues -= 1
        else:
            puzzle[row][column] = value
    return puzzle, solution
