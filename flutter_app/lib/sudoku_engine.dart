import 'dart:math';

typedef SudokuGrid = List<List<int>>;

class GeneratedPuzzle {
  const GeneratedPuzzle({required this.puzzle, required this.solution});

  final SudokuGrid puzzle;
  final SudokuGrid solution;
}

SudokuGrid copyGrid(SudokuGrid grid) =>
    grid.map((row) => List<int>.of(row)).toList();

bool isValidGrid(SudokuGrid grid) {
  if (grid.length != 9 || grid.any((row) => row.length != 9)) {
    return false;
  }

  for (var row = 0; row < 9; row++) {
    final values = grid[row].where((value) => value != 0).toList();
    if (values.any((value) => value < 1 || value > 9) ||
        values.toSet().length != values.length) {
      return false;
    }
  }

  for (var column = 0; column < 9; column++) {
    final values = [
      for (var row = 0; row < 9; row++) grid[row][column],
    ].where((value) => value != 0).toList();
    if (values.toSet().length != values.length) return false;
  }

  for (var boxRow = 0; boxRow < 9; boxRow += 3) {
    for (var boxColumn = 0; boxColumn < 9; boxColumn += 3) {
      final values = [
        for (var row = boxRow; row < boxRow + 3; row++)
          for (var column = boxColumn; column < boxColumn + 3; column++)
            grid[row][column],
      ].where((value) => value != 0).toList();
      if (values.toSet().length != values.length) return false;
    }
  }
  return true;
}

List<int> candidatesFor(SudokuGrid grid, int row, int column) {
  if (grid[row][column] != 0) return const [];
  final used = <int>{};
  used.addAll(grid[row].where((value) => value != 0));
  for (var index = 0; index < 9; index++) {
    if (grid[index][column] != 0) used.add(grid[index][column]);
  }
  final boxRow = row ~/ 3 * 3;
  final boxColumn = column ~/ 3 * 3;
  for (var currentRow = boxRow; currentRow < boxRow + 3; currentRow++) {
    for (
      var currentColumn = boxColumn;
      currentColumn < boxColumn + 3;
      currentColumn++
    ) {
      final value = grid[currentRow][currentColumn];
      if (value != 0) used.add(value);
    }
  }
  return [
    for (var value = 1; value <= 9; value++)
      if (!used.contains(value)) value,
  ];
}

SudokuGrid? solveSudoku(SudokuGrid grid, {bool randomize = false}) {
  if (!isValidGrid(grid)) return null;
  final board = copyGrid(grid);
  final random = Random();

  bool search() {
    var bestRow = -1;
    var bestColumn = -1;
    List<int>? bestOptions;
    for (var row = 0; row < 9; row++) {
      for (var column = 0; column < 9; column++) {
        if (board[row][column] != 0) continue;
        final options = candidatesFor(board, row, column);
        if (options.isEmpty) return false;
        if (bestOptions == null || options.length < bestOptions.length) {
          bestRow = row;
          bestColumn = column;
          bestOptions = options;
          if (options.length == 1) break;
        }
      }
      if (bestOptions?.length == 1) break;
    }
    final optionsForCell = bestOptions;
    if (optionsForCell == null) return true;
    if (randomize) optionsForCell.shuffle(random);

    for (final value in optionsForCell) {
      board[bestRow][bestColumn] = value;
      if (search()) return true;
    }
    board[bestRow][bestColumn] = 0;
    return false;
  }

  return search() ? board : null;
}

int countSolutions(SudokuGrid grid, {int limit = 2}) {
  if (!isValidGrid(grid)) return 0;
  final board = copyGrid(grid);
  var count = 0;

  void search() {
    if (count >= limit) return;
    var bestRow = -1;
    var bestColumn = -1;
    List<int>? bestOptions;
    for (var row = 0; row < 9; row++) {
      for (var column = 0; column < 9; column++) {
        if (board[row][column] != 0) continue;
        final options = candidatesFor(board, row, column);
        if (options.isEmpty) return;
        if (bestOptions == null || options.length < bestOptions.length) {
          bestRow = row;
          bestColumn = column;
          bestOptions = options;
          if (options.length == 1) break;
        }
      }
      if (bestOptions?.length == 1) break;
    }
    if (bestOptions == null) {
      count++;
      return;
    }
    for (final value in bestOptions) {
      board[bestRow][bestColumn] = value;
      search();
      board[bestRow][bestColumn] = 0;
      if (count >= limit) return;
    }
  }

  search();
  return count;
}

GeneratedPuzzle generatePuzzle(String difficulty) {
  const targetClues = <String, int>{
    'easy': 40,
    'medium': 34,
    'hard': 29,
    'expert': 25,
  };
  final target = targetClues[difficulty];
  if (target == null) throw ArgumentError.value(difficulty, 'difficulty');

  final solution = solveSudoku(
    List.generate(9, (_) => List.filled(9, 0)),
    randomize: true,
  );
  if (solution == null) throw StateError('Unable to build a solved grid.');
  final puzzle = copyGrid(solution);
  final cells = List<int>.generate(81, (index) => index)..shuffle();
  var clues = 81;
  for (final cell in cells) {
    if (clues <= target) break;
    final row = cell ~/ 9;
    final column = cell % 9;
    final value = puzzle[row][column];
    puzzle[row][column] = 0;
    if (countSolutions(puzzle) == 1) {
      clues--;
    } else {
      puzzle[row][column] = value;
    }
  }
  return GeneratedPuzzle(puzzle: puzzle, solution: solution);
}

GeneratedPuzzle generatePuzzleForIsolate(String difficulty) =>
    generatePuzzle(difficulty);
