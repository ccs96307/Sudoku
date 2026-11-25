'use strict';

const SIZE = 9;
const STORAGE_KEY = 'still-sudoku-v1';
const PREFERENCES_KEY = 'still-sudoku-preferences-v1';
const TARGET_CLUES = {easy: 40, medium: 34, hard: 29, expert: 25};
const THEMES = [
  ['midnight-garden','Midnight Garden','#101918','#172320','#1d2a27','#30423b','#eef2e7','#91a39a','#c4e7a2','#14231b','#fff0cf','#82dcff','#41634f','#202e2a','#344c3c','#ff9385','#482e2b'],
  ['arctic-aurora','Arctic Aurora','#0b1522','#132235','#1b2e45','#34506d','#edf7ff','#9cb5c8','#83e6ff','#082033','#fff1c2','#8bd0ff','#235b77','#1a3044','#25465d','#ff9a9a','#542b3a'],
  ['amethyst-night','Amethyst Night','#171322','#231b32','#302442','#514066','#f4edff','#b3a3c8','#d1a8ff','#28183d','#fff0cf','#8ee7ff','#5c397b','#30243e','#49345d','#ff9cbd','#542b45'],
  ['ember-library','Ember Library','#201410','#2c1d17','#3a281f','#614333','#fff1e3','#c0a08b','#ffc078','#39200e','#fff0cf','#75dcff','#754525','#3c2a20','#5a3824','#ff9a83','#5a2924'],
  ['deep-ocean','Deep Ocean','#081a20','#10272e','#17343d','#2e5963','#e7f7f5','#8cb4b5','#70e0cc','#092c2a','#fff0cf','#8ecbff','#17605c','#17343b','#20514e','#ff978b','#512d31'],
  ['graphite-neon','Graphite Neon','#111315','#1a1d20','#24282c','#454b50','#f4f5f6','#a4a9ad','#d5ff53','#202511','#ffffff','#59d9ff','#495321','#24292b','#394323','#ff7f88','#48272b'],
  ['rose-quartz','Rose Quartz','#21151b','#2e1d26','#3b2732','#634253','#fff0f5','#c3a1b1','#ffadd1','#3c1c2c','#fff0cf','#8ce4ff','#75415d','#3b2833','#5b354a','#ff9d8d','#5b2c35'],
  ['solar-flare','Solar Flare','#21190d','#30230f','#403016','#705323','#fff5df','#c3ac7c','#ffd65e','#38280b','#fff5d7','#78e6ff','#73520f','#403018','#5c4318','#ff9384','#562d22'],
  ['pine-cabin','Pine Cabin','#111b15','#1b2a20','#26382a','#405d45','#edf5e9','#9bb39c','#b5e48a','#1f3219','#fff0cf','#7edaff','#416345','#26372b','#354f38','#ff9585','#4e2d2a'],
  ['lavender-dusk','Lavender Dusk','#1a1724','#252133','#322c44','#4c4567','#f3efff','#aaa2c2','#c8b7ff','#2a2346','#fff0cf','#7de1ff','#504476','#302b40','#453b61','#ff9dab','#542e47'],
  ['mint-condition','Mint Condition','#0e1c1a','#172b27','#203a34','#37645a','#e8faf4','#8fb7a9','#8cf0c8','#12392f','#fff0cf','#86caff','#286553','#203a34','#2b5448','#ff948d','#522e32'],
  ['cobalt-studio','Cobalt Studio','#101629','#18223a','#222f4c','#3c527b','#f0f4ff','#9aaacc','#92adff','#172850','#fff0cf','#76e4ff','#38539a','#222f49','#304372','#ff929e','#552c42'],
  ['coral-reef','Coral Reef','#201512','#2e201d','#3d2b27','#654640','#fff1ea','#c19d91','#ffad91','#47261d','#fff0cf','#71dcff','#814d3c','#3c2b27','#624035','#ff858d','#572c32'],
  ['paper-ink','Paper & Ink','#f2f0e8','#fffdf7','#e7e4d9','#b9b6a8','#20251f','#646b62','#245c49','#ffffff','#17231d','#075f9a','#3e7058','#e1e9df','#c7ded0','#9c1d36','#f5d9de'],
  ['cherry-blossom','Cherry Blossom','#f7edf0','#fff9fb','#f0dfe6','#d3b4c0','#38232d','#806a75','#a63d68','#ffffff','#33202a','#075c91','#8c4a68','#f1e3e8','#e4c2d0','#a61f28','#f6dce0'],
  ['desert-sand','Desert Sand','#f4eddf','#fffbf2','#eae0ce','#cbb99a','#352a1e','#786a57','#93602b','#ffffff','#2c2118','#075c91','#79552d','#eee4d2','#dfc8a8','#a12626','#f4d8cf'],
  ['jade-palace','Jade Palace','#eaf3ed','#fbfffc','#dcebe1','#adcbb8','#1f3528','#607d6a','#237854','#ffffff','#193b29','#075b91','#38734f','#e0ede4','#c2dfcc','#9b2435','#f6dce0'],
  ['violet-hour','Violet Hour','#f0edf7','#fcfaff','#e5e0f0','#c2b8d9','#2e2940','#716984','#654da4','#ffffff','#27213a','#006289','#675890','#e8e3f1','#d5cbea','#a21d41','#f7dce5'],
  ['glacier-blue','Glacier Blue','#e9f2f7','#f9fdff','#dbe9f1','#adc7d5','#1c3441','#5d7b8a','#1f718d','#ffffff','#183444','#064f8b','#3d7187','#e0edf3','#c4e0eb','#a32135','#f6dce0'],
  ['noir-gold','Noir & Gold','#101010','#1b1a18','#282522','#544b3a','#f5f0e5','#b5a98d','#e5bd65','#2a2110','#fff2d2','#73dfff','#62502b','#282521','#423921','#ff9385','#4c2928'],
];
const $ = (selector) => document.querySelector(selector);
const boardElement = $('#board');
const numberPad = $('#number-pad');
const statusElement = $('#status');
const timerElement = $('#timer');
const state = {grid: [], givens: [], solution: [], selected: 0, notes: Array.from({length: 81}, () => new Set()), noteMode: false, history: [], seconds: 0, startedAt: Date.now()};
let toastTimeout;
let armedDigit = null;
let preferences = {theme: 'midnight-garden', rapidEntry: true};
let celebrationShown = false;
let originalTheme = preferences.theme;
let pendingTheme = preferences.theme;
let timerHandle;

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
function hasGridShape(grid) {
  return Array.isArray(grid) && grid.length === 9 &&
    grid.every((row) => Array.isArray(row) && row.length === 9 &&
      row.every((value) => Number.isInteger(value) && value >= 0 && value <= 9));
}
function valid(grid) {
  if (!hasGridShape(grid)) return false;
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
    button.addEventListener('click', () => selectCell(index));
    boardElement.append(button);
  }
  for (let value = 1; value <= 9; value++) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = value;
    button.setAttribute('aria-label', `Choose ${value}`); button.addEventListener('click', () => chooseNumber(value)); numberPad.append(button);
  }
}
function matchesPuzzle(givens, solution) {
  return givens.every((row, r) => row.every((value, c) =>
    !value || value === solution[r][c]));
}
function isSolved() {
  return state.grid.length === 9 && state.grid.flat().every(
    (value, index) => value === state.solution[Math.floor(index / 9)][index % 9]);
}
function render(popIndex = -1) {
  const selectedValue = state.grid[Math.floor(state.selected / 9)][state.selected % 9];
  const buttons = [...boardElement.children]; const filled = state.grid.flat().filter(Boolean).length;
  for (let index = 0; index < 81; index++) {
    const row = Math.floor(index / 9), col = index % 9, value = state.grid[row][col], button = buttons[index];
    const selectedRow = Math.floor(state.selected / 9), selectedCol = state.selected % 9;
    const related = row === selectedRow || col === selectedCol || (Math.floor(row / 3) === Math.floor(selectedRow / 3) && Math.floor(col / 3) === Math.floor(selectedCol / 3));
    const conflict = Boolean(value && cellPeers(index).some((peer) => state.grid[Math.floor(peer / 9)][peer % 9] === value));
    button.className = ['cell', state.givens[row][col] ? 'given' : value ? 'entry' : '', index === state.selected ? 'selected' : '', related ? 'related' : '', selectedValue && value === selectedValue ? 'same' : '', conflict ? 'conflict' : '', !value && state.notes[index].size ? 'note' : '', index === popIndex ? 'entered' : ''].filter(Boolean).join(' ');
    button.textContent = value || (state.notes[index].size ? [...state.notes[index]].sort().join('') : '');
    if (index !== popIndex && button.classList.contains('entered')) button.classList.remove('entered');
    button.classList.toggle('armed-target', Boolean(armedDigit && !value && !state.givens[row][col]));
    button.setAttribute('aria-selected', String(index === state.selected));
  }
  const counts = Array(10).fill(0); state.grid.flat().forEach((value) => { if (value) counts[value]++; });
  [...numberPad.children].forEach((button, index) => {
    button.classList.toggle('complete', counts[index + 1] >= 9);
    button.classList.toggle('armed', armedDigit === index + 1);
  });
  $('#entry-help').textContent = preferences.rapidEntry
    ? (armedDigit ? `Tap squares to place ${armedDigit} · press Esc to clear.` : 'Quick place: choose a number, then tap multiple squares to fill.')
    : 'Select a square, then choose a number to place it.';
  $('#progress-label').textContent = `${filled} / 81 filled`;
  $('#progress').style.width = `${filled / 81 * 100}%`;
}
function save() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify({...state, notes: state.notes.map((notes) => [...notes]), history: []})); } catch (_) { showToast('Could not save this game on this device.'); }
}
function newGame() {
  const {puzzle, solution} = makePuzzle($('#difficulty').value);
  celebrationShown = false; armedDigit = null;
  state.grid = puzzle; state.givens = cloneGrid(puzzle); state.solution = solution; state.difficulty = $('#difficulty').value; state.selected = puzzle.flat().findIndex((value) => !value);
  state.notes = Array.from({length: 81}, () => new Set()); state.history = []; state.noteMode = false; state.seconds = 0; state.startedAt = Date.now();
  $('#notes').classList.remove('active');
  statusElement.textContent = 'A fresh page. Take your time.';
  save(); render(); animateReveal();
  boardElement.animate([{opacity:.35,transform:'scale(.985)'},{opacity:1,transform:'scale(1)'}], {duration:520,easing:'cubic-bezier(.2,.7,.2,1)'});
}
function animateReveal() {
  [...boardElement.children].forEach((cell, index) => { cell.style.setProperty('--delay', `${index * 4}ms`); cell.classList.add('reveal'); });
}
function selectCell(index) {
  state.selected = index;
  if (preferences.rapidEntry && armedDigit) {
    enter(armedDigit, index);
    return;
  }
  render();
}
function chooseNumber(value) {
  if (preferences.rapidEntry) {
    armedDigit = armedDigit === value ? null : value;
    render();
    return;
  }
  enter(value);
}
function enter(value, index = state.selected) {
  state.selected = index;
  const row = Math.floor(index / 9), col = index % 9;
  if (state.givens[row][col]) { render(); return; }
  if (state.noteMode) {
    state.history.push({type: 'cell', index, value: state.grid[row][col], notes: [...state.notes[index]]});
    if (state.notes[index].has(value)) state.notes[index].delete(value); else state.notes[index].add(value);
  } else {
    state.history.push({type: 'cell', index, value: state.grid[row][col], notes: [...state.notes[index]]});
    state.grid[row][col] = value; state.notes[index].clear();
    const button = boardElement.children[index]; button.animate([{transform:'scale(.8)',opacity:.5},{transform:'scale(1)',opacity:1}],{duration:250,easing:'cubic-bezier(.2,.9,.3,1.4)'});
    if (!valid(state.grid)) { statusElement.textContent = 'That number conflicts with this row, column, or box.'; button.classList.add('conflict'); }
    else if (isSolved()) { pauseClock(); statusElement.textContent = 'Beautifully done. You made space for clarity.'; showToast('Puzzle complete · beautifully done'); celebrate(); }
    else statusElement.textContent = 'A good next step.';
  }
  save(); render(index);
}
function celebrate() {
  if (celebrationShown) return;
  celebrationShown = true;
  const layer = $('#celebration');
  const palette = THEMES.find((theme) => theme[0] === preferences.theme) || THEMES[0];
  const colors = [palette[8], palette[11], '#ffffff', palette[7]];
  for (let index = 0; index < 54; index++) {
    const piece = document.createElement('i'); piece.className = 'confetti';
    piece.style.setProperty('--x', `${Math.random() * 100}%`);
    piece.style.setProperty('--size', `${5 + Math.random() * 7}px`);
    piece.style.setProperty('--duration', `${1.6 + Math.random() * 1.5}s`);
    piece.style.setProperty('--delay', `${Math.random() * .55}s`);
    piece.style.setProperty('--rotation', `${Math.random() * 180}deg`);
    piece.style.setProperty('--drift', `${Math.random() * 180 - 90}px`);
    piece.style.setProperty('--confetti', colors[index % colors.length]); layer.append(piece);
    setTimeout(() => piece.remove(), 3000);
  }
}
function erase() {
  const index = state.selected, row = Math.floor(index / 9), col = index % 9;
  if (state.givens[row][col]) return;
  state.history.push({type: 'cell', index, value: state.grid[row][col], notes: [...state.notes[index]]});
  state.grid[row][col] = 0; state.notes[index].clear(); save(); render();
}
function undo() {
  const previous = state.history.pop(); if (!previous) return;
  if (previous.type === 'board') {
    state.grid = cloneGrid(previous.grid);
    state.notes = previous.notes.map((items) => items.slice());
  } else {
    const row = Math.floor(previous.index / 9), col = previous.index % 9;
    state.grid[row][col] = previous.value;
    state.notes[previous.index] = new Set(previous.notes);
    state.selected = previous.index;
  }
  if (!isSolved()) state.startedAt = Date.now() - state.seconds * 1000;
  statusElement.textContent = 'Last move undone.';
  save(); render();
}
function pauseClock() {
  state.seconds = Math.max(0, Math.floor((Date.now() - state.startedAt) / 1000));
  state.startedAt = Date.now() - state.seconds * 1000;
  timerElement.textContent = `${String(Math.floor(state.seconds / 60)).padStart(2,'0')}:${String(state.seconds % 60).padStart(2,'0')}`;
}
function solvePuzzle() {
  if (isSolved()) { statusElement.textContent = 'This puzzle is already solved.'; return; }
  state.history.push({
    type: 'board',
    grid: cloneGrid(state.grid),
    notes: state.notes.map((items) => [...items]),
  });
  pauseClock();
  state.grid = cloneGrid(state.solution);
  state.notes = Array.from({length: 81}, () => new Set());
  state.noteMode = false; armedDigit = null;
  $('#notes').classList.remove('active');
  statusElement.textContent = 'Solved. Use Undo to restore your board.';
  save(); render();
  [...boardElement.children].forEach((cell, index) => {
    const row = Math.floor(index / 9), col = index % 9;
    if (state.givens[row][col]) return;
    cell.style.setProperty('--delay', `${index * 9}ms`);
    cell.classList.add('solved-fill');
  });
  showToast('Solution revealed');
}
function hint() {
  if (state.grid[Math.floor(state.selected / 9)][state.selected % 9]) {
    const index = state.grid.flat().findIndex((value) => !value);
    if (index >= 0) state.selected = index;
  }
  const index = state.selected, row = Math.floor(index / 9), col = index % 9;
  if (!state.grid[row][col]) enter(state.solution[row][col], index);
  statusElement.textContent = 'A little nudge, right where you needed it.';
  boardElement.children[index].classList.add('hint');
}
function showToast(message) {
  const toast = $('#toast'); toast.textContent = message; toast.classList.add('show'); clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => toast.classList.remove('show'), 2400);
}
function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved && hasGridShape(saved.grid) && hasGridShape(saved.givens) &&
        hasGridShape(saved.solution) && saved.solution.flat().every(Boolean) &&
        valid(saved.solution) && valid(saved.givens) && matchesPuzzle(saved.givens, saved.solution)) {
      Object.assign(state, saved); state.notes = Array.from({length: 81}, (_, index) =>
        new Set(Array.isArray(saved.notes?.[index]) ? saved.notes[index].filter((value) => Number.isInteger(value) && value >= 1 && value <= 9) : []));
      state.history = [];
      if (!Number.isInteger(state.selected) || state.selected < 0 || state.selected >= 81) state.selected = 0;
      if (!['easy','medium','hard','expert'].includes(state.difficulty)) state.difficulty = 'medium';
      $('#difficulty').value = state.difficulty;
      state.seconds = Math.max(0, Number(state.seconds) || 0);
      state.startedAt = Date.now() - state.seconds * 1000;
      return;
    }
  } catch (_) { /* Start a clean game when stored data is incomplete. */ }
  newGame();
}
$('#new-game').addEventListener('click', newGame);
$('#undo').addEventListener('click', undo);
$('#erase').addEventListener('click', erase);
$('#hint').addEventListener('click', hint);
$('#solve').addEventListener('click', solvePuzzle);
$('#notes').addEventListener('click', () => { state.noteMode = !state.noteMode; $('#notes').classList.toggle('active', state.noteMode); statusElement.textContent = state.noteMode ? 'Pencil notes on.' : 'Pencil notes off.'; });
function applyTheme(themeId) {
  const theme = THEMES.find((item) => item[0] === themeId) || THEMES[0];
  const vars = ['--bg','--panel','--panel2','--line','--text','--muted','--accent','--accent-ink','--given','--entry','--selected','--related','--same','--error','--error-bg'];
  vars.forEach((name, index) => document.documentElement.style.setProperty(name, theme[index + 2]));
  const lightThemes = ['paper-ink','cherry-blossom','desert-sand','jade-palace','violet-hour','glacier-blue'];
  document.documentElement.style.colorScheme = lightThemes.includes(theme[0]) ? 'light' : 'dark';
  renderThemePreview(theme);
}
function renderThemePreview(theme) {
  if (!theme) return;
  const previewName = $('#theme-preview-name');
  const previewBoard = $('#theme-preview');
  if (!previewName || !previewBoard) return;
  previewName.textContent = theme[1];
  previewBoard.replaceChildren();
  const sample = [
    ['5', 'preview-given'], ['', 'preview-related'], ['8', 'preview-entry'],
    ['2', 'preview-given'], ['4', 'preview-focus'], ['7', 'preview-related'],
    ['1', 'preview-entry'], ['9', 'preview-given'], ['', 'preview-entry'],
  ];
  sample.forEach(([digit, className]) => {
    const cell = document.createElement('span');
    cell.className = className; cell.textContent = digit; previewBoard.append(cell);
  });
}
function buildThemePicker() {
  const picker = $('#theme-picker');
  picker.replaceChildren();
  THEMES.forEach((theme) => {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'palette-card';
    button.setAttribute('role', 'option'); button.dataset.theme = theme[0];
    button.setAttribute('aria-label', theme[1]);
    const swatches = document.createElement('span'); swatches.className = 'palette-swatches';
    [theme[8], theme[2], theme[10], theme[11]].forEach((color) => {
      const dot = document.createElement('i'); dot.style.backgroundColor = color; swatches.append(dot);
    });
    const name = document.createElement('span'); name.textContent = theme[1];
    button.append(swatches, name);
    button.addEventListener('click', () => {
      pendingTheme = theme[0]; applyTheme(pendingTheme); updateThemeSelection();
    });
    picker.append(button);
  });
  updateThemeSelection();
}
function updateThemeSelection() {
  document.querySelectorAll('.palette-card').forEach((button) => {
    button.setAttribute('aria-selected', String(button.dataset.theme === pendingTheme));
  });
}
function savePreferences() {
  try { localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences)); } catch (_) { /* Preferences are optional. */ }
}
function openSettings() {
  originalTheme = preferences.theme;
  pendingTheme = preferences.theme;
  $('#rapid-entry').checked = preferences.rapidEntry;
  applyTheme(pendingTheme); updateThemeSelection();
  $('#settings-dialog').showModal();
}
$('#settings-button').addEventListener('click', openSettings);
$('#settings-dialog').addEventListener('close', () => {
  if ($('#settings-dialog').returnValue === 'confirm') {
    preferences.theme = pendingTheme;
    preferences.rapidEntry = $('#rapid-entry').checked;
    armedDigit = null; savePreferences(); render();
    statusElement.textContent = 'Settings saved.';
  } else {
    pendingTheme = originalTheme;
    applyTheme(originalTheme); render();
  }
});
window.addEventListener('keydown', (event) => {
  if (event.target instanceof HTMLElement &&
      (event.target.closest('dialog') ||
       ['INPUT', 'SELECT', 'TEXTAREA'].includes(event.target.tagName))) return;
  const row = Math.floor(state.selected / 9), col = state.selected % 9;
  if (event.key === 'ArrowUp') { event.preventDefault(); state.selected = ((row + 8) % 9) * 9 + col; render(); }
  else if (event.key === 'ArrowDown') { event.preventDefault(); state.selected = ((row + 1) % 9) * 9 + col; render(); }
  else if (event.key === 'ArrowLeft') { event.preventDefault(); state.selected = row * 9 + (col + 8) % 9; render(); }
  else if (event.key === 'ArrowRight') { event.preventDefault(); state.selected = row * 9 + (col + 1) % 9; render(); }
  else if (/^[1-9]$/.test(event.key)) enter(Number(event.key));
  else if (event.key === 'Escape') { armedDigit = null; render(); }
  else if (event.key === '0' || event.key === 'Backspace' || event.key === 'Delete') erase();
  else if (event.key.toLowerCase() === 'n') { state.noteMode = !state.noteMode; $('#notes').classList.toggle('active', state.noteMode); }
  else if (event.key.toLowerCase() === 's') solvePuzzle();
  else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') undo();
});
timerHandle = setInterval(() => { if (!isSolved()) state.seconds = Math.max(0, Math.floor((Date.now() - state.startedAt) / 1000)); timerElement.textContent = `${String(Math.floor(state.seconds / 60)).padStart(2,'0')}:${String(state.seconds % 60).padStart(2,'0')}`; save(); }, 1000);
buildBoard();
buildThemePicker();
try { preferences = {...preferences, ...JSON.parse(localStorage.getItem(PREFERENCES_KEY) || '{}')}; } catch (_) { /* Use the defaults. */ }
if (!THEMES.some((theme) => theme[0] === preferences.theme)) preferences.theme = THEMES[0][0];
preferences.rapidEntry = preferences.rapidEntry !== false;
pendingTheme = preferences.theme;
applyTheme(preferences.theme); $('#rapid-entry').checked = preferences.rapidEntry;
load(); render(); animateReveal();

if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  window.addEventListener('load', () => navigator.serviceWorker.register('./sw.js').catch(() => {}));
}
