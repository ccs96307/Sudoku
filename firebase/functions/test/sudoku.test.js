'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const {countSolutions, hasGridShape, isValidGrid, makeDailyPuzzle, solveSudoku} = require('../src/sudoku');

test('validates a complete Sudoku solution', () => {
  const solution = solveSudoku(Array.from({length: 9}, () => Array(9).fill(0)));
  assert.equal(hasGridShape(solution), true);
  assert.equal(isValidGrid(solution), true);
  assert.equal(solution.flat().every((value) => value >= 1 && value <= 9), true);
});

test('daily puzzle is deterministic and has a unique solution', () => {
  const first = makeDailyPuzzle('2026-11-26');
  const second = makeDailyPuzzle('2026-11-26');
  assert.deepEqual(first, second);
  assert.equal(countSolutions(first.puzzle), 1);
  assert.ok(first.clueCount >= 34);
});
