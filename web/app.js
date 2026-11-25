'use strict';

const SIZE = 9;
const STORAGE_KEY = 'still-sudoku-v1';
const TARGET_CLUES = {easy: 40, medium: 34, hard: 29, expert: 25};
const $ = (selector) => document.querySelector(selector);
const boardElement = $('#board');
const numberPad = $('#number-pad');
const statusElement = $('#status');
const timerElement = $('#timer');
const state = {grid: [], givens: [], solution: [], selected: 0, notes: Array.from({length: 81}, () => new Set()), noteMode: false, history: [], seconds: 0, startedAt: Date.now()};
let toastTimeout;

function cloneGrid(grid) { return grid.map((row) => row.slice()); }
function cellPeers(index) {
  const row = Math.floor(index / 9), col = index % 9;
  const peers = new Set();
  for (let i = 0; i < 9; i++) { peers.add(row * 9 + i); peers.add(i * 9 + col); }
  const top = Math.floor(row / 3) * 3, left = Math.floor(col / 3) * 3;
  for (let r = top; r < top + 3; r++) for (let c = left; c < left + 3; c++) peers.add(r * 9 + c);
  peers.delete(index);
  return [...peers];
}
function optionsAt(grid, index) {
  if (grid[Math.floor(index / 9)][index % 9]) return [];
  const peers = cellPeers(index);
  const used = new Set(peers.map((peer) => grid[Math.floor(peer / 9)][peer % 9]));
  return [1, 2, 3, 4, 5, 6, 7, 8, 9].filter((value) => !used.has(value));
}
function valid(grid) {
  for (let index = 0; index < 81; index++) {
    const value = grid[Math.floor(index / 9)][index % 9];
    if (!value) continue;
    if (cellPeers(index).some((peer) => grid[Math.floor(peer / 9)][peer % 9] === value)) return false;
  }
  return true;
}
function solve(grid, randomize = false) {
  if (!valid(grid)) return null;
  const board = cloneGrid(grid);
  function search() {
    let selected = -1, choices = null;
    for (let index = 0; index < 81; index++) {
      if (board[Math.floor(index / 9)][index % 9]) continue;
      const options = optionsAt(board, index);
      if (!options.length) return false;
      if (!choices || options.length < choices.length) { selected = index; choices = options; }
    }
    if (selected < 0) return true;
    if (randomize) choices.sort(() => Math.random() - .5);
    const row = Math.floor(selected / 9), col = selected % 9;
    for (const value of choices) { board[row][col] = value; if (search()) return true; }
    board[row][col] = 0;
    return false;
  }
  return search() ? board : null;
}
function countSolutions(grid, limit = 2) {
  if (!valid(grid)) return 0;
  const board = cloneGrid(grid); let count = 0;
  function search() {
    if (count >= limit) return;
    let selected = -1, choices = null;
    for (let index = 0; index < 81; index++) {
      if (board[Math.floor(index / 9)][index % 9]) continue;
      const options = optionsAt(board, index);
      if (!options.length) return;
      if (!choices || options.length < choices.length) { selected = index; choices = options; }
    }
    if (selected < 0) { count++; return; }
    const row = Math.floor(selected / 9), col = selected % 9;
    for (const value of choices) { board[row][col] = value; search(); board[row][col] = 0; if (count >= limit) return; }
  }
  search(); return count;
}
function makePuzzle(difficulty) {
  const solution = solve(Array.from({length: 9}, () => Array(9).fill(0)), true);
  const puzzle = cloneGrid(solution);
  const cells = Array.from({length: 81}, (_, index) => index).sort(() => Math.random() - .5);
  let clues = 81;
  for (const index of cells) {
    if (clues <= TARGET_CLUES[difficulty]) break;
    const row = Math.floor(index / 9), col = index % 9, value = puzzle[row][col];
    puzzle[row][col] = 0;
    if (countSolutions(puzzle) === 1) clues--; else puzzle[row][col] = value;
  }
  return {puzzle, solution};
}
function buildBoard() {
  boardElement.replaceChildren(); numberPad.replaceChildren();
  for (let index = 0; index < 81; index++) {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'cell'; button.setAttribute('role', 'gridcell');
    button.setAttribute('aria-label', `Row ${Math.floor(index / 9) + 1}, column ${index % 9 + 1}`);
    button.addEventListener('click', () => { state.selected = index; render(); });
    boardElement.append(button);
  }
  for (let value = 1; value <= 9; value++) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = value;
    button.setAttribute('aria-label', `Enter ${value}`); button.addEventListener('click', () => enter(value)); numberPad.append(button);
  }
}
function render(popIndex = -1) {
  const selectedValue = state.grid[Math.floor(state.selected / 9)][state.selected % 9];
  const buttons = [...boardElement.children]; const filled = state.grid.flat().filter(Boolean).length;
  for (let index = 0; index < 81; index++) {
    const row = Math.floor(index / 9), col = index % 9, value = state.grid[row][col], button = buttons[index];
    const selectedRow = Math.floor(state.selected / 9), selectedCol = state.selected % 9;
    const related = row === selectedRow || col === selectedCol || (Math.floor(row / 3) === Math.floor(selectedRow / 3) && Math.floor(col / 3) === Math.floor(selectedCol / 3));
    const conflict = Boolean(value && cellPeers(index).some((peer) => state.grid[Math.floor(peer / 9)][peer % 9] === value));
    button.className = ['cell', state.givens[row][col] ? 'given' : '', index === state.selected ? 'selected' : '', related ? 'related' : '', selectedValue && value === selectedValue ? 'same' : '', conflict ? 'conflict' : '', !value && state.notes[index].size ? 'note' : '', index === popIndex ? 'pop' : ''].filter(Boolean).join(' ');
    button.textContent = value || (state.notes[index].size ? [...state.notes[index]].sort().join('') : '');
    button.setAttribute('aria-selected', String(index === state.selected));
  }
  const counts = Array(10).fill(0); state.grid.flat().forEach((value) => { if (value) counts[value]++; });
  [...numberPad.children].forEach((button, index) => button.classList.toggle('complete', counts[index + 1] >= 9));
  $('#progress-label').textContent = `${filled} / 81 filled`;
  $('#progress').style.width = `${filled / 81 * 100}%`;
}
function save() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify({...state, notes: state.notes.map((notes) => [...notes]), history: []})); } catch (_) { showToast('Could not save this game on this device.'); }
}
function newGame() {
  const {puzzle, solution} = makePuzzle($('#difficulty').value);
  state.grid = puzzle; state.givens = cloneGrid(puzzle); state.solution = solution; state.selected = puzzle.flat().findIndex((value) => !value);
  state.notes = Array.from({length: 81}, () => new Set()); state.history = []; state.noteMode = false; state.seconds = 0; state.startedAt = Date.now();
  statusElement.textContent = 'A fresh page. Take your time.'; $('#notes').classList.remove('active');
  save(); render(); boardElement.animate([{opacity:.35,transform:'scale(.985)'},{opacity:1,transform:'scale(1)'}], {duration:420,easing:'cubic-bezier(.2,.7,.2,1)'});
}
function enter(value) {
  const index = state.selected, row = Math.floor(index / 9), col = index % 9;
  if (state.givens[row][col]) return;
  if (state.noteMode) {
    if (state.notes[index].has(value)) state.notes[index].delete(value); else state.notes[index].add(value);
  } else {
    state.history.push({index, value: state.grid[row][col], notes: [...state.notes[index]]});
    state.grid[row][col] = value; state.notes[index].clear();
    const button = boardElement.children[index]; button.animate([{transform:'scale(.8)',opacity:.5},{transform:'scale(1)',opacity:1}],{duration:250,easing:'cubic-bezier(.2,.9,.3,1.4)'});
    if (!valid(state.grid)) { statusElement.textContent = 'That number conflicts with this row, column, or box.'; button.classList.add('conflict'); }
    else if (state.grid.flat().every((digit, i) => digit === state.solution[Math.floor(i / 9)][i % 9])) { statusElement.textContent = 'Beautifully done. You made space for clarity.'; showToast('Puzzle complete · beautifully done'); }
    else statusElement.textContent = 'A good next step.';
  }
  save(); render(index);
}
function erase() {
  const index = state.selected, row = Math.floor(index / 9), col = index % 9;
  if (state.givens[row][col]) return;
  state.history.push({index, value: state.grid[row][col], notes: [...state.notes[index]]}); state.grid[row][col] = 0; state.notes[index].clear(); save(); render();
}
function undo() {
  const previous = state.history.pop(); if (!previous) return;
  const row = Math.floor(previous.index / 9), col = previous.index % 9;
  state.grid[row][col] = previous.value; state.notes[previous.index] = new Set(previous.notes); state.selected = previous.index; save(); render();
}
function hint() {
  if (state.givens[Math.floor(state.selected / 9)][state.selected % 9]) {
    const index = state.grid.flat().findIndex((value) => !value); if (index >= 0) state.selected = index;
  }
  const row = Math.floor(state.selected / 9), col = state.selected % 9;
  if (!state.grid[row][col]) enter(state.solution[row][col]);
  statusElement.textContent = 'A little nudge, right where you needed it.';
}
function showToast(message) {
  const toast = $('#toast'); toast.textContent = message; toast.classList.add('show'); clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.remove('show'), 2400);
}
function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved && saved.grid?.length === 9 && saved.solution?.length === 9) {
      Object.assign(state, saved); state.notes = (saved.notes || []).map((items) => new Set(items));
      while (state.notes.length < 81) state.notes.push(new Set()); state.history = []; state.startedAt = Date.now(); return;
    }
  } catch (_) { /* Start a clean game when stored data is incomplete. */ }
  newGame();
}
$('#new-game').addEventListener('click', newGame);
$('#undo').addEventListener('click', undo);
$('#erase').addEventListener('click', erase);
$('#hint').addEventListener('click', hint);
$('#notes').addEventListener('click', () => { state.noteMode = !state.noteMode; $('#notes').classList.toggle('active', state.noteMode); statusElement.textContent = state.noteMode ? 'Pencil notes on.' : 'Pencil notes off.'; });
$('#theme-button').addEventListener('click', () => { document.body.classList.toggle('light'); localStorage.setItem('still-sudoku-theme', document.body.classList.contains('light') ? 'light' : 'dark'); });
window.addEventListener('keydown', (event) => {
  const direction = {ArrowUp: -9, ArrowDown: 9, ArrowLeft: -1, ArrowRight: 1};
  if (event.key in direction) { event.preventDefault(); state.selected = (state.selected + direction[event.key] + 81) % 81; render(); }
  else if (/^[1-9]$/.test(event.key)) enter(Number(event.key));
  else if (event.key === '0' || event.key === 'Backspace' || event.key === 'Delete') erase();
  else if (event.key.toLowerCase() === 'n') { state.noteMode = !state.noteMode; $('#notes').classList.toggle('active', state.noteMode); }
  else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') undo();
});
setInterval(() => { state.seconds = Math.max(0, Math.floor((Date.now() - state.startedAt) / 1000)); timerElement.textContent = `${String(Math.floor(state.seconds / 60)).padStart(2,'0')}:${String(state.seconds % 60).padStart(2,'0')}`; save(); }, 1000);
buildBoard();
if (localStorage.getItem('still-sudoku-theme') === 'light') document.body.classList.add('light');
load(); render();

if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  window.addEventListener('load', () => navigator.serviceWorker.register('./sw.js').catch(() => {}));
}
