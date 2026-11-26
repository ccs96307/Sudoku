'use strict';

const SIZE = 9;
const TARGET_CLUES = 34;

function cloneGrid(grid) {
  return grid.map((row) => [...row]);
}

function hasGridShape(grid) {
  return Array.isArray(grid) && grid.length === SIZE &&
    grid.every((row) => Array.isArray(row) && row.length === SIZE &&
      row.every((value) => Number.isInteger(value) && value >= 0 && value <= 9));
}

function candidates(grid, row, column) {
  const used = new Set(grid[row]);
  for (let index = 0; index < SIZE; index++) used.add(grid[index][column]);
  const boxRow = Math.floor(row / 3) * 3;
  const boxColumn = Math.floor(column / 3) * 3;
  for (let currentRow = boxRow; currentRow < boxRow + 3; currentRow++) {
    for (let currentColumn = boxColumn; currentColumn < boxColumn + 3; currentColumn++) {
      used.add(grid[currentRow][currentColumn]);
    }
  }
  used.delete(0);
  return [1, 2, 3, 4, 5, 6, 7, 8, 9].filter((value) => !used.has(value));
}

function isValidGrid(grid) {
  if (!hasGridShape(grid)) return false;
  for (let row = 0; row < SIZE; row++) {
    const values = grid[row].filter(Boolean);
    if (new Set(values).size !== values.length) return false;
  }
  for (let column = 0; column < SIZE; column++) {
    const values = grid.map((row) => row[column]).filter(Boolean);
    if (new Set(values).size !== values.length) return false;
  }
  for (let boxRow = 0; boxRow < SIZE; boxRow += 3) {
    for (let boxColumn = 0; boxColumn < SIZE; boxColumn += 3) {
      const values = [];
      for (let row = boxRow; row < boxRow + 3; row++) {
        for (let column = boxColumn; column < boxColumn + 3; column++) {
          if (grid[row][column]) values.push(grid[row][column]);
        }
      }
      if (new Set(values).size !== values.length) return false;
    }
  }
  return true;
}

function solveSudoku(input, random = Math.random) {
  if (!isValidGrid(input)) return null;
  const grid = cloneGrid(input);
  function search() {
    let best = null;
    for (let row = 0; row < SIZE; row++) {
      for (let column = 0; column < SIZE; column++) {
        if (grid[row][column]) continue;
        const options = candidates(grid, row, column);
        if (!options.length) return false;
        if (best === null || options.length < best.options.length) {
          best = {row, column, options};
          if (options.length === 1) break;
        }
      }
      if (best?.options.length === 1) break;
    }
    if (best === null) return true;
    for (let index = best.options.length - 1; index > 0; index--) {
      const swap = Math.floor(random() * (index + 1));
      [best.options[index], best.options[swap]] = [best.options[swap], best.options[index]];
    }
    for (const value of best.options) {
      grid[best.row][best.column] = value;
      if (search()) return true;
    }
    grid[best.row][best.column] = 0;
    return false;
  }
  return search() ? grid : null;
}

function countSolutions(input, limit = 2) {
  if (!isValidGrid(input)) return 0;
  const grid = cloneGrid(input);
  let count = 0;
  function search() {
    if (count >= limit) return;
    let best = null;
    for (let row = 0; row < SIZE; row++) {
      for (let column = 0; column < SIZE; column++) {
        if (grid[row][column]) continue;
        const options = candidates(grid, row, column);
        if (!options.length) return;
        if (best === null || options.length < best.options.length) {
          best = {row, column, options};
          if (options.length === 1) break;
        }
      }
      if (best?.options.length === 1) break;
    }
    if (best === null) {
      count++;
      return;
    }
    for (const value of best.options) {
      grid[best.row][best.column] = value;
      search();
      grid[best.row][best.column] = 0;
      if (count >= limit) return;
    }
  }
  search();
  return count;
}

function seededRandom(seed) {
  let value = seed >>> 0;
  return () => {
    value += 0x6D2B79F5;
    let current = value;
    current = Math.imul(current ^ current >>> 15, current | 1);
    current ^= current + Math.imul(current ^ current >>> 7, current | 61);
    return ((current ^ current >>> 14) >>> 0) / 4294967296;
  };
}

function makeDailyPuzzle(date) {
  const seed = Number(date.replaceAll('-', ''));
  const random = seededRandom(seed);
  const solution = solveSudoku(Array.from({length: SIZE}, () => Array(SIZE).fill(0)), random);
  const puzzle = cloneGrid(solution);
  const cells = Array.from({length: SIZE * SIZE}, (_, index) => index);
  for (let index = cells.length - 1; index > 0; index--) {
    const swap = Math.floor(random() * (index + 1));
    [cells[index], cells[swap]] = [cells[swap], cells[index]];
  }
  let clues = 81;
  for (const index of cells) {
    if (clues <= TARGET_CLUES) break;
    const row = Math.floor(index / SIZE);
    const column = index % SIZE;
    const value = puzzle[row][column];
    puzzle[row][column] = 0;
    if (countSolutions(puzzle) === 1) clues--;
    else puzzle[row][column] = value;
  }
  return {puzzle, solution, difficulty: 'medium', clueCount: clues};
}

module.exports = {countSolutions, hasGridShape, isValidGrid, makeDailyPuzzle, solveSudoku};
