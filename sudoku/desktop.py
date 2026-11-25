"""PySide6 desktop interface for Beautiful Sudoku."""

import json
import time
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QVBoxLayout, QWidget, QGraphicsOpacityEffect)

from sudoku.engine import generate, is_valid

_STATE_PATH = Path.home() / ".beautiful-sudoku.json"
_STYLES = """
QMainWindow, QWidget { background: #101918; color: #e9f1e9; font-family: 'Inter', 'Aptos', sans-serif; }
QLabel#eyebrow { color: #91c7a4; letter-spacing: 3px; font-size: 11px; font-weight: 700; }
QLabel#title { color: #f3f5e9; font-family: Georgia, serif; font-size: 38px; }
QLabel#subtitle, QLabel#muted { color: #91a39a; font-size: 13px; }
QLabel#stat { color: #d8e7d8; font-size: 14px; font-weight: 600; }
QPushButton { background: #263633; border: 1px solid #344b43; border-radius: 12px; color: #e6eee5; padding: 11px 16px; font-size: 13px; font-weight: 600; }
QPushButton:hover { background: #324a40; border-color: #79b58a; }
QPushButton#primary { background: #c4e7a2; border: 0; color: #14231b; }
QPushButton#primary:hover { background: #d5f2ba; }
QPushButton#number { background: #1d2a27; border: 1px solid #31433d; font-size: 20px; padding: 8px; }
QPushButton#number:hover { background: #c4e7a2; color: #14231b; }
QPushButton#cell { background: #172320; border: 0; border-radius: 0; color: #dff1e2; font-size: 23px; padding: 0; }
QPushButton#cell:disabled { color: #f2f2de; background: #22332d; }
QPushButton#cell[selected="true"] { background: #41634f; }
QPushButton#cell[related="true"] { background: #202e2a; }
QPushButton#cell[same="true"] { background: #344c3c; color: #c4e7a2; }
QPushButton#cell[error="true"] { color: #ff9385; background: #482e2b; }
QComboBox { background: #1d2a27; border: 1px solid #344b43; border-radius: 10px; padding: 9px 12px; }
QFrame#board { background: #c4e7a2; border-radius: 16px; }
"""


class SudokuWindow(QMainWindow):
    """Elegant, keyboard-friendly Sudoku game window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku — A little clarity")
        self.setMinimumSize(620, 820)
        self.selected = (0, 0)
        self.notes_mode = False
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.history = []
        self.elapsed = 0
        self.started_at = time.monotonic()
        self.cells = []
        self._build_ui()
        self._load_or_start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._render()

    def _build_ui(self):
        self.setStyleSheet(_STYLES)
        root = QWidget()
        page = QVBoxLayout(root)
        page.setContentsMargins(30, 24, 30, 24)
        page.setSpacing(15)
        page.addWidget(self._label("DAILY RITUAL  ·  NO RUSH", "eyebrow"))
        page.addWidget(self._label("A little clarity.", "title"))
        page.addWidget(self._label("One quiet square at a time.", "subtitle"))
        controls = QHBoxLayout()
        self.difficulty = QComboBox()
        self.difficulty.addItems(["easy", "medium", "hard", "expert"])
        self.difficulty.setCurrentText("medium")
        controls.addWidget(self.difficulty)
        new_button = QPushButton("New puzzle")
        new_button.setObjectName("primary")
        new_button.clicked.connect(self._new_game)
        controls.addWidget(new_button)
        controls.addStretch()
        self.time_label = self._label("00:00", "stat")
        controls.addWidget(self.time_label)
        page.addLayout(controls)
        board_frame = QFrame()
        board_frame.setObjectName("board")
        board_grid = QGridLayout(board_frame)
        board_grid.setContentsMargins(5, 5, 5, 5)
        board_grid.setSpacing(2)
        for row in range(9):
            row_cells = []
            for column in range(9):
                cell = QPushButton("")
                cell.setObjectName("cell")
                cell.clicked.connect(lambda checked=False, r=row, c=column: self._select(r, c))
                board_grid.addWidget(cell, row, column)
                row_cells.append(cell)
            self.cells.append(row_cells)
        for index in range(9):
            board_grid.setColumnStretch(index, 1)
            board_grid.setRowStretch(index, 1)
        self.board = board_frame
        page.addWidget(board_frame, 1)
        self.status_label = self._label("A fresh page. Take your time.", "muted")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page.addWidget(self.status_label)
        digits = QHBoxLayout()
        for value in range(1, 10):
            button = QPushButton(str(value))
            button.setObjectName("number")
            button.clicked.connect(lambda checked=False, number=value: self._enter(number))
            digits.addWidget(button)
        page.addLayout(digits)
        actions = QHBoxLayout()
        for title, callback in [("Undo", self._undo), ("Notes", self._toggle_notes),
                                ("Hint", self._hint), ("Erase", self._erase)]:
            button = QPushButton(title)
            button.clicked.connect(callback)
            actions.addWidget(button)
        page.addLayout(actions)
        footer = self._label("ARROW KEYS TO MOVE  ·  1–9 TO FILL  ·  N FOR NOTES", "eyebrow")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page.addWidget(footer)
        self.setCentralWidget(root)

    @staticmethod
    def _label(text, name):
        label = QLabel(text)
        label.setObjectName(name)
        return label

    def _load_or_start(self):
        if _STATE_PATH.exists():
            try:
                state = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
                self.grid = state["grid"]
                self.givens = state["givens"]
                self.solution = state["solution"]
                self.elapsed = int(state.get("elapsed", 0))
                self.started_at = time.monotonic()
                return
            except (OSError, ValueError, KeyError, TypeError):
                pass
        self._new_game()

    def _new_game(self):
        self.grid, self.solution = generate(self.difficulty.currentText())
        self.givens = [row[:] for row in self.grid]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.history.clear()
        self.elapsed = 0
        self.started_at = time.monotonic()
        self.selected = next(((r, c) for r in range(9) for c in range(9)
                              if self.grid[r][c] == 0), (0, 0))
        self.status_label.setText("A fresh page. Take your time.")
        self._save()
        self._animate_board()
        self._render()

    def _animate_board(self):
        effect = QGraphicsOpacityEffect(self.board)
        self.board.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(420)
        animation.setStartValue(0.35)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self._board_animation = animation

    def _select(self, row, column):
        self.selected = (row, column)
        self._render()

    def _enter(self, value):
        row, column = self.selected
        if self.givens[row][column]:
            return
        if self.notes_mode:
            if value in self.notes[row][column]:
                self.notes[row][column].remove(value)
            else:
                self.notes[row][column].add(value)
        else:
            self.history.append((row, column, self.grid[row][column], self.notes[row][column].copy()))
            self.grid[row][column] = value
            self.notes[row][column].clear()
            if not is_valid(self.grid):
                self.status_label.setText("That number conflicts with this row, column, or box.")
            elif self.grid == self.solution:
                self.status_label.setText("Beautifully done. You made space for clarity.")
            else:
                self.status_label.setText("A good next step.")
        self._save()
        self._render()

    def _erase(self):
        row, column = self.selected
        if not self.givens[row][column]:
            self.history.append((row, column, self.grid[row][column], self.notes[row][column].copy()))
            self.grid[row][column] = 0
            self.notes[row][column].clear()
            self._save()
            self._render()

    def _undo(self):
        if self.history:
            row, column, value, notes = self.history.pop()
            self.grid[row][column] = value
            self.notes[row][column] = notes
            self.selected = (row, column)
            self._save()
            self._render()

    def _hint(self):
        row, column = self.selected
        if self.givens[row][column]:
            row, column = next(((r, c) for r in range(9) for c in range(9)
                                if not self.grid[r][c]), (row, column))
            self.selected = (row, column)
        self._enter(self.solution[row][column])
        self.status_label.setText("A little nudge, right where you needed it.")

    def _toggle_notes(self):
        self.notes_mode = not self.notes_mode
        self.status_label.setText("Pencil notes on." if self.notes_mode else "Pencil notes off.")

    def _tick(self):
        seconds = self.elapsed + int(time.monotonic() - self.started_at)
        self.time_label.setText(f"{seconds // 60:02d}:{seconds % 60:02d}")
        self._save()

    def _save(self):
        if not hasattr(self, "grid"):
            return
        state = {"grid": self.grid, "givens": self.givens,
                 "solution": self.solution, "elapsed": self.elapsed + int(time.monotonic() - self.started_at)}
        try:
            _STATE_PATH.write_text(json.dumps(state), encoding="utf-8")
        except OSError:
            pass

    def _render(self):
        row, column = self.selected
        selected_value = self.grid[row][column]
        has_error = not is_valid(self.grid)
        for r in range(9):
            for c in range(9):
                button = self.cells[r][c]
                value = self.grid[r][c]
                button.setText(str(value) if value else "·" if self.notes[r][c] else "")
                button.setEnabled(not self.givens[r][c])
                button.setProperty("selected", r == row and c == column)
                button.setProperty("related", r == row or c == column or
                                   (r // 3 == row // 3 and c // 3 == column // 3))
                button.setProperty("same", bool(selected_value and value == selected_value))
                button.setProperty("error", bool(value and has_error))
                button.style().unpolish(button)
                button.style().polish(button)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        row, column = self.selected
        directions = {Qt.Key.Key_Up: (-1, 0), Qt.Key.Key_Down: (1, 0),
                      Qt.Key.Key_Left: (0, -1), Qt.Key.Key_Right: (0, 1)}
        if key in directions:
            dr, dc = directions[key]
            self.selected = ((row + dr) % 9, (column + dc) % 9)
            self._render()
        elif Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            self._enter(key - Qt.Key.Key_0)
        elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_0):
            self._erase()
        elif key == Qt.Key.Key_N:
            self._toggle_notes()
        elif key == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._undo()
        else:
            super().keyPressEvent(event)
