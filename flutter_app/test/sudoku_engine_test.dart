import 'package:flutter_test/flutter_test.dart';
import 'package:still_sudoku/sudoku_engine.dart';

const puzzle = <List<int>>[
  [8, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 3, 6, 0, 0, 0, 0, 0],
  [0, 7, 0, 0, 9, 0, 2, 0, 0],
  [0, 5, 0, 0, 0, 7, 0, 0, 0],
  [0, 0, 0, 0, 4, 5, 7, 0, 0],
  [0, 0, 0, 1, 0, 0, 0, 3, 0],
  [0, 0, 1, 0, 0, 0, 0, 6, 8],
  [0, 0, 8, 5, 0, 0, 0, 1, 0],
  [0, 9, 0, 0, 0, 0, 4, 0, 0],
];

void main() {
  test('solves a puzzle without mutating the input', () {
    final original = copyGrid(puzzle);
    final solution = solveSudoku(puzzle);

    expect(solution, isNotNull);
    expect(isValidGrid(solution!), isTrue);
    expect(solution.every((row) => row.every((value) => value != 0)), isTrue);
    expect(puzzle, original);
  });

  test('counts the unique solution and rejects invalid boards', () {
    expect(countSolutions(puzzle), 1);
    final invalid = copyGrid(puzzle)..[0][1] = 8;
    expect(countSolutions(invalid), 0);
  });

  test('generated easy puzzle has exactly one solution', () {
    final generated = generatePuzzle('easy');
    expect(countSolutions(generated.puzzle), 1);
    expect(isValidGrid(generated.solution), isTrue);
  });
}
