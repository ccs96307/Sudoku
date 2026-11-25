"""Regression tests for the Sudoku engine."""

import unittest

from sudoku.engine import candidates, count_solutions, generate, is_valid, solve

PUZZLE = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0],
]


class SudokuEngineTest(unittest.TestCase):
    """Check solver, validation, candidates, and generation behavior."""

    def test_solver_returns_valid_solution_without_mutating_input(self):
        """Solve a puzzle while preserving the caller's input grid."""
        original = [row[:] for row in PUZZLE]
        solution = solve(PUZZLE)

        self.assertIsNotNone(solution)
        self.assertTrue(is_valid(solution))
        self.assertTrue(all(all(value for value in row) for row in solution))
        self.assertEqual(PUZZLE, original)
        self.assertTrue(
            all(
                not value or solution[row][column] == value
                for row, values in enumerate(PUZZLE)
                for column, value in enumerate(values)
            )
        )

    def test_solution_counter_stops_at_two_and_detects_unique_puzzle(self):
        """Count a unique solution and reject conflicting starting clues."""
        self.assertEqual(count_solutions(PUZZLE), 1)
        invalid = [row[:] for row in PUZZLE]
        invalid[0][1] = 8
        self.assertEqual(count_solutions(invalid), 0)

    def test_candidates_exclude_row_column_and_box_values(self):
        """Exclude digits already used by any Sudoku constraint."""
        values = candidates(PUZZLE, 0, 1)

        self.assertNotIn(8, values)
        self.assertNotIn(3, values)
        self.assertNotIn(7, values)
        self.assertTrue(values)

    def test_generated_puzzle_has_unique_solution_and_preserves_clues(self):
        """Generate a uniquely solvable puzzle with its matching solution."""
        puzzle, solution = generate("easy")

        self.assertTrue(is_valid(puzzle))
        self.assertTrue(is_valid(solution))
        self.assertEqual(count_solutions(puzzle), 1)
        self.assertTrue(
            all(
                not value or solution[row][column] == value
                for row, values in enumerate(puzzle)
                for column, value in enumerate(values)
            )
        )

    def test_unknown_difficulty_is_rejected(self):
        """Reject difficulty names that have no configured clue target."""
        with self.assertRaises(ValueError):
            generate("impossible")


if __name__ == "__main__":
    unittest.main()
