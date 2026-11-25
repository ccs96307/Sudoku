"""PySide6 desktop interface for Beautiful Sudoku."""

import json
import time
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSettings,
    Qt,
    QTimer,
)
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sudoku.engine import generate, is_valid
from sudoku.themes import THEMES

_STATE_PATH = Path.home() / ".beautiful-sudoku.json"
_STYLES = """
QMainWindow, QWidget {
  background: @bg@;
  color: @text@;
  font-family: 'Inter', 'Aptos', sans-serif;
}
QLabel#eyebrow {
  color: @accent@;
  letter-spacing: 3px;
  font-size: 11px;
  font-weight: 700;
}
QLabel#title {
  color: @text@;
  font-family: Georgia, serif;
  font-size: 38px;
}
QLabel#subtitle, QLabel#muted {
  color: @muted@;
  font-size: 13px;
}
QLabel#stat {
  color: @text@;
  font-size: 14px;
  font-weight: 600;
}
QLabel#legendGiven {
  color: @given@;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 1px;
}
QLabel#legendEntry {
  color: @entry@;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 1px;
}
QPushButton {
  background: @panel2@;
  border: 1px solid @line@;
  border-radius: 12px;
  color: @text@;
  padding: 11px 16px;
  font-size: 13px;
  font-weight: 600;
}
QPushButton:hover {
  background: @selected@;
  border-color: @accent@;
}
QPushButton#primary {
  background: @accent@;
  border: 0;
  color: @ink@;
}
QPushButton#primary:hover {
  background: @text@;
  color: @bg@;
}
QPushButton#number {
  background: @panel2@;
  border: 1px solid @line@;
  color: @entry@;
  font-size: 20px;
  padding: 8px;
  font-weight: 700;
}
QPushButton#number:hover, QPushButton#number[armed="true"] {
  background: @accent@;
  color: @ink@;
}
QPushButton#cell {
  background: @panel@;
  border: 0;
  border-radius: 0;
  color: @entry@;
  font-size: 23px;
  font-weight: 700;
  padding: 0;
}
QPushButton#cell[related="true"] {
  background: @related@;
}
QPushButton#cell[same="true"] {
  background: @same@;
  color: @entry@;
}
QPushButton#cell[fixed="true"] {
  color: @given@;
  background: @panel2@;
  font-weight: 800;
}
QPushButton#cell[fixed="true"][related="true"] {
  background: @related@;
}
QPushButton#cell[fixed="true"][selected="true"] {
  background: @selected@;
  color: @given@;
}
QPushButton#cell[selected="true"] {
  background: @selected@;
  color: #ffffff;
}
QPushButton#cell[note="true"] {
  color: @accent@;
  font-size: 9px;
}
QPushButton#cell[error="true"] {
  color: @error@;
  background: @error_bg@;
}
QComboBox, QCheckBox {
  color: @text@;
}
QComboBox {
  background: @panel2@;
  border: 1px solid @line@;
  border-radius: 10px;
  padding: 9px 12px;
}
QComboBox QAbstractItemView {
  background: @panel2@;
  color: @text@;
  selection-background-color: @selected@;
}
QDialog {
  background: @bg@;
}
QFrame#board {
  background: @accent@;
  border-radius: 16px;
}
"""


class SudokuWindow(QMainWindow):
    """Elegant, keyboard-friendly Sudoku game window."""

    def __init__(self):
        """Initialize the window and restore the current game."""
        super().__init__()
        self.setWindowTitle("Sudoku — A little clarity")
        self.setMinimumSize(620, 820)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.settings = QSettings("Still", "Sudoku")
        self.theme_name = self.settings.value("theme", "Midnight Garden")
        if self.theme_name not in THEMES:
            self.theme_name = "Midnight Garden"
        self.rapid_entry = self.settings.value("rapid_entry", True, type=bool)
        self.armed_digit = None
        self.selected = (0, 0)
        self.notes_mode = False
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.history = []
        self.elapsed = 0
        self.started_at = time.monotonic()
        self.cells = []
        self.number_buttons = []
        self.cell_animations = {}
        self._build_ui()
        self._load_or_start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._render()

    def _build_ui(self):
        self._apply_theme(self.theme_name)
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
        self.difficulty.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        controls.addWidget(self.difficulty)
        new_button = QPushButton("New puzzle")
        new_button.setObjectName("primary")
        new_button.clicked.connect(self._new_game)
        controls.addWidget(new_button)
        settings_button = QPushButton("⚙")
        settings_button.setToolTip("Settings")
        settings_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        settings_button.setAccessibleName("Settings")
        settings_button.clicked.connect(self._show_settings)
        controls.addWidget(settings_button)
        controls.addStretch()
        self.time_label = self._label("00:00", "stat")
        controls.addWidget(self.time_label)
        page.addLayout(controls)
        legend = QHBoxLayout()
        legend.addStretch()
        given_legend = self._label("8  PUZZLE", "legendGiven")
        entry_legend = self._label("8  YOURS", "legendEntry")
        legend.addWidget(given_legend)
        legend.addSpacing(16)
        legend.addWidget(entry_legend)
        page.addLayout(legend)
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
                cell.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                cell.clicked.connect(
                    lambda checked=False, r=row, c=column: self._select(r, c)
                )
                board_grid.addWidget(cell, row, column)
                row_cells.append(cell)
            self.cells.append(row_cells)
        for index in range(9):
            board_grid.setColumnStretch(index, 1)
            board_grid.setRowStretch(index, 1)
        self.board = board_frame
        page.addWidget(board_frame, 1)
        self.status_label = self._label(
            "A fresh page. Take your time.", "muted"
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page.addWidget(self.status_label)
        digits = QHBoxLayout()
        for value in range(1, 10):
            button = QPushButton(str(value))
            button.setObjectName("number")
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(
                lambda checked=False, number=value: self._number_pressed(number)
            )
            digits.addWidget(button)
            self.number_buttons.append(button)
        page.addLayout(digits)
        actions = QHBoxLayout()
        for title, callback in [
            ("Undo", self._undo),
            ("Notes", self._toggle_notes),
            ("Hint", self._hint),
            ("Erase", self._erase),
        ]:
            button = QPushButton(title)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(callback)
            actions.addWidget(button)
        page.addLayout(actions)
        self.footer = self._label(
            "CHOOSE A NUMBER · TAP CELLS TO REPEAT · ARROWS TO MOVE", "eyebrow"
        )
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page.addWidget(self.footer)
        self.setCentralWidget(root)

    @staticmethod
    def _label(text, name):
        label = QLabel(text)
        label.setObjectName(name)
        return label

    def _apply_theme(self, theme_name):
        """Apply one of the built-in high-contrast palettes."""
        theme = THEMES[theme_name]
        stylesheet = _STYLES
        for name, value in theme.items():
            stylesheet = stylesheet.replace(f"@{name}@", value)
        self.setStyleSheet(stylesheet)

    def _show_settings(self):
        """Show color and rapid-entry preferences."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        form = QFormLayout(dialog)
        palette = QComboBox()
        palette.addItems(THEMES.keys())
        palette.setCurrentText(self.theme_name)
        rapid = QCheckBox("Choose a number, then tap cells to fill them")
        rapid.setChecked(self.rapid_entry)
        form.addRow("Color palette", palette)
        form.addRow("Quick entry", rapid)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.theme_name = palette.currentText()
            self.rapid_entry = rapid.isChecked()
            self.footer.setText(
                "CHOOSE A NUMBER · TAP CELLS TO REPEAT · ARROWS TO MOVE"
                if self.rapid_entry
                else "SELECT A CELL · PRESS 1–9 TO FILL · N FOR NOTES"
            )
            self.armed_digit = None
            self.settings.setValue("theme", self.theme_name)
            self.settings.setValue("rapid_entry", self.rapid_entry)
            self._apply_theme(self.theme_name)
            self._render()
            self.status_label.setText("Settings saved.")

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
        self.armed_digit = None
        self.notes_mode = False
        self.elapsed = 0
        self.started_at = time.monotonic()
        self.selected = next(
            (
                (r, c)
                for r in range(9)
                for c in range(9)
                if self.grid[r][c] == 0
            ),
            (0, 0),
        )
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
        if self.rapid_entry and self.armed_digit:
            self._enter(self.armed_digit)
            return
        self._render()

    def _number_pressed(self, value):
        if self.rapid_entry:
            self.armed_digit = None if self.armed_digit == value else value
            self.status_label.setText(
                f"Tap empty squares to place {value}."
                if self.armed_digit
                else "Number selection cleared."
            )
            self._render()
        else:
            self._enter(value)

    def _animate_cell(self, row, column):
        """Give each new entry a quick, soft reveal."""
        cell = self.cells[row][column]
        animation_pair = self.cell_animations.get(cell)
        if animation_pair is None:
            effect = QGraphicsOpacityEffect(cell)
            cell.setGraphicsEffect(effect)
            animation = QPropertyAnimation(effect, b"opacity", self)
            animation.setDuration(260)
            animation.setStartValue(0.25)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.OutBack)
            self.cell_animations[cell] = (effect, animation)
        else:
            effect, animation = animation_pair
            animation.stop()
        effect.setOpacity(0.25)
        animation.start()

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
            self.history.append(
                (
                    row,
                    column,
                    self.grid[row][column],
                    self.notes[row][column].copy(),
                )
            )
            self.grid[row][column] = value
            self.notes[row][column].clear()
            self._animate_cell(row, column)
            if not is_valid(self.grid):
                self.status_label.setText(
                    "That number conflicts with this row, column, or box."
                )
            elif self.grid == self.solution:
                self.status_label.setText(
                    "Beautifully done. You made space for clarity."
                )
            else:
                self.status_label.setText("A good next step.")
        self._save()
        self._render()

    def _erase(self):
        row, column = self.selected
        if not self.givens[row][column]:
            self.history.append(
                (
                    row,
                    column,
                    self.grid[row][column],
                    self.notes[row][column].copy(),
                )
            )
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
        if self.grid[row][column]:
            row, column = next(
                (
                    (r, c)
                    for r in range(9)
                    for c in range(9)
                    if not self.grid[r][c]
                ),
                (row, column),
            )
            self.selected = (row, column)
        self._enter(self.solution[row][column])
        self.status_label.setText("A little nudge, right where you needed it.")

    def _toggle_notes(self):
        self.notes_mode = not self.notes_mode
        self.status_label.setText(
            "Pencil notes on." if self.notes_mode else "Pencil notes off."
        )

    def _tick(self):
        seconds = self.elapsed + int(time.monotonic() - self.started_at)
        self.time_label.setText(f"{seconds // 60:02d}:{seconds % 60:02d}")
        self._save()

    def _save(self):
        if not hasattr(self, "grid"):
            return
        state = {
            "grid": self.grid,
            "givens": self.givens,
            "solution": self.solution,
            "elapsed": self.elapsed + int(time.monotonic() - self.started_at),
        }
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
                button.setText(
                    str(value)
                    if value
                    else "".join(str(note) for note in sorted(self.notes[r][c]))
                )
                button.setProperty("note", bool(self.notes[r][c]) and not value)
                button.setEnabled(True)
                button.setProperty("fixed", bool(self.givens[r][c]))
                button.setProperty("selected", r == row and c == column)
                button.setProperty(
                    "related",
                    r == row
                    or c == column
                    or (r // 3 == row // 3 and c // 3 == column // 3),
                )
                button.setProperty(
                    "same", bool(selected_value and value == selected_value)
                )
                button.setProperty("error", bool(value and has_error))
                button.style().unpolish(button)
                button.style().polish(button)
        for value, button in enumerate(self.number_buttons, start=1):
            button.setProperty("armed", value == self.armed_digit)
            button.style().unpolish(button)
            button.style().polish(button)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle digit entry, selection movement, and game shortcuts."""
        key = event.key()
        row, column = self.selected
        directions = {
            Qt.Key.Key_Up: (-1, 0),
            Qt.Key.Key_Down: (1, 0),
            Qt.Key.Key_Left: (0, -1),
            Qt.Key.Key_Right: (0, 1),
        }
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
        elif key == Qt.Key.Key_Escape and self.armed_digit:
            self.armed_digit = None
            self._render()
        elif (
            key == Qt.Key.Key_Z
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self._undo()
        else:
            super().keyPressEvent(event)
