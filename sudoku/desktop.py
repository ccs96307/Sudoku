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
    Slot,
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
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sudoku.cloud import CloudTask, FirebaseRestClient
from sudoku.engine import generate, is_valid, solve
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
  border: 1px solid @accent@;
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
  background: @accent@;
  color: @ink@;
  border: 3px solid #ffffff;
}
QPushButton#cell[selected="true"] {
  background: @accent@;
  color: @ink@;
  border: 3px solid #ffffff;
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
QLabel#previewGiven {
  color: @given@;
  background: @panel2@;
  font-size: 17px;
  font-weight: 800;
}
QLabel#previewEntry {
  color: @entry@;
  background: @panel@;
  font-size: 17px;
  font-weight: 700;
}
QLabel#previewSelected {
  color: @ink@;
  background: @accent@;
  border: 3px solid #ffffff;
  font-size: 17px;
  font-weight: 800;
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
        self.cloud = FirebaseRestClient.from_environment()
        self._cloud_tasks = []
        self._cloud_pending = None
        self._cloud_signature = None
        self._cloud_pending_signature = None
        self._cloud_upload_signature = None
        self._cloud_last_sync_at = 0.0
        self._cloud_sync_timer = QTimer(self)
        self._cloud_sync_timer.setSingleShot(True)
        self._cloud_sync_timer.timeout.connect(self._push_cloud_game)
        self.daily_date = None
        self.hints_used = 0
        self.used_solve = False
        self.saved_at_ms = 0
        self._build_ui()
        self._load_or_start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        if self.grid == self.solution:
            self.timer.stop()
        self._render()

    def _build_ui(self):
        self._apply_theme(self.theme_name)
        root = QWidget()
        page = QVBoxLayout(root)
        page.setContentsMargins(30, 24, 30, 24)
        page.setSpacing(15)
        self.eyebrow = self._label("DAILY RITUAL  ·  NO RUSH", "eyebrow")
        page.addWidget(self.eyebrow)
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
        self.account_button = QPushButton("Account")
        self.account_button.clicked.connect(self._show_account)
        controls.addWidget(self.account_button)
        controls.addStretch()
        self.time_label = self._label("00:00", "stat")
        controls.addWidget(self.time_label)
        page.addLayout(controls)
        cloud_controls = QHBoxLayout()
        daily_button = QPushButton("Daily challenge")
        daily_button.clicked.connect(self._start_daily_challenge)
        cloud_controls.addWidget(daily_button)
        leaderboard_button = QPushButton("Leaderboard")
        leaderboard_button.clicked.connect(self._show_leaderboard)
        cloud_controls.addWidget(leaderboard_button)
        self.cloud_status = self._label(
            "Guest mode · offline saves are on this device", "muted"
        )
        self.cloud_status.setWordWrap(True)
        cloud_controls.addWidget(self.cloud_status, 1)
        page.addLayout(cloud_controls)
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
            ("Solve", self._solve_game),
        ]:
            button = QPushButton(title)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.clicked.connect(callback)
            actions.addWidget(button)
        page.addLayout(actions)
        self.footer = self._label(
            "CHOOSE A NUMBER · TAP TO FILL · S TO SOLVE", "eyebrow"
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
        """Preview palettes and save preferences only when confirmed."""
        original_theme = self.theme_name
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        form = QFormLayout(dialog)
        palette = QComboBox()
        palette.addItems(THEMES.keys())
        palette.setCurrentText(self.theme_name)
        rapid = QCheckBox("Choose a number, then tap cells to fill them")
        rapid.setChecked(self.rapid_entry)
        form.addRow("Color palette", palette)
        preview = QFrame()
        preview_grid = QGridLayout(preview)
        preview_grid.setContentsMargins(5, 5, 5, 5)
        preview_grid.setSpacing(3)
        preview_roles = [
            "previewGiven",
            "previewGiven",
            "previewEntry",
            "previewEntry",
            "previewSelected",
            "previewGiven",
            "previewEntry",
            "previewGiven",
            "previewEntry",
        ]
        for index, role in enumerate(preview_roles):
            sample = QLabel(str(index % 9 + 1))
            sample.setObjectName(role)
            sample.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sample.setMinimumSize(34, 34)
            preview_grid.addWidget(sample, index // 3, index % 3)
        form.addRow("Live preview", preview)
        form.addRow("Quick entry", rapid)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Confirm")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        palette.currentTextChanged.connect(self._apply_theme)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.theme_name = palette.currentText()
            self.rapid_entry = rapid.isChecked()
            self.footer.setText(
                "CHOOSE A NUMBER · TAP TO FILL · S TO SOLVE"
                if self.rapid_entry
                else "SELECT A CELL · PRESS 1–9 · S TO SOLVE"
            )
            self.armed_digit = None
            self.settings.setValue("theme", self.theme_name)
            self.settings.setValue("rapid_entry", self.rapid_entry)
            self._apply_theme(self.theme_name)
            self._render()
            self.status_label.setText("Settings saved.")
        else:
            self._apply_theme(original_theme)

    def _load_or_start(self):
        if _STATE_PATH.exists():
            try:
                state = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
                self.grid = state["grid"]
                self.givens = state["givens"]
                self.solution = state["solution"]
                boards = (self.grid, self.givens, self.solution)
                if any(
                    len(board) != 9
                    or any(
                        len(row) != 9
                        or any(
                            not isinstance(value, int) or not 0 <= value <= 9
                            for value in row
                        )
                        for row in board
                    )
                    for board in boards
                ):
                    raise ValueError(
                        "Saved Sudoku board has invalid dimensions."
                    )
                if (
                    any(not value for row in self.solution for value in row)
                    or not is_valid(self.solution)
                    or not is_valid(self.givens)
                ):
                    raise ValueError("Saved Sudoku puzzle is invalid.")
                if any(
                    self.givens[row][column]
                    and self.grid[row][column] != self.givens[row][column]
                    for row in range(9)
                    for column in range(9)
                ):
                    raise ValueError("Saved givens were modified.")
                saved_notes = state.get("notes", [])
                if len(saved_notes) == 9 and all(
                    len(row) == 9 for row in saved_notes
                ):
                    self.notes = [
                        [
                            {
                                value
                                for value in values
                                if isinstance(value, int) and 1 <= value <= 9
                            }
                            for values in row
                        ]
                        for row in saved_notes
                    ]
                else:
                    self.notes = [[set() for _ in range(9)] for _ in range(9)]
                saved_selection = state.get("selected", [0, 0])
                self.selected = tuple(saved_selection)
                if len(self.selected) != 2 or any(
                    not isinstance(value, int) or not 0 <= value < 9
                    for value in self.selected
                ):
                    self.selected = (0, 0)
                self.elapsed = max(0, int(state.get("elapsed", 0)))
                self.daily_date = state.get("daily_date")
                self.hints_used = max(0, int(state.get("hints_used", 0)))
                self.used_solve = bool(state.get("used_solve", False))
                self.saved_at_ms = max(0, int(state.get("saved_at_ms", 0)))
                difficulty = state.get("difficulty", "medium")
                if difficulty in {"easy", "medium", "hard", "expert"}:
                    self.difficulty.setCurrentText(difficulty)
                    self.difficulty_name = difficulty
                self.started_at = time.monotonic()
                return
            except (OSError, ValueError, KeyError, TypeError):
                pass
        self._new_game()

    def _new_game(self):
        self.grid, self.solution = generate(self.difficulty.currentText())
        self.difficulty_name = self.difficulty.currentText()
        self.givens = [row[:] for row in self.grid]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.history.clear()
        self.armed_digit = None
        self.notes_mode = False
        self.elapsed = 0
        self.daily_date = None
        self.hints_used = 0
        self.used_solve = False
        self.started_at = time.monotonic()
        if hasattr(self, "timer"):
            self.timer.start(1000)
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
            self._render()
            return
        if self.notes_mode:
            self.history.append(
                {
                    "type": "cell",
                    "row": row,
                    "column": column,
                    "value": self.grid[row][column],
                    "notes": self.notes[row][column].copy(),
                }
            )
            if value in self.notes[row][column]:
                self.notes[row][column].remove(value)
            else:
                self.notes[row][column].add(value)
        else:
            self.history.append(
                {
                    "type": "cell",
                    "row": row,
                    "column": column,
                    "value": self.grid[row][column],
                    "notes": self.notes[row][column].copy(),
                }
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
        if self.grid == self.solution:
            self.elapsed += int(time.monotonic() - self.started_at)
            self.started_at = time.monotonic()
            self.timer.stop()
        elif not self.timer.isActive():
            self.started_at = time.monotonic()
            self.timer.start(1000)
        self._save()
        self._render()
        if (
            self.daily_date
            and self.grid == self.solution
            and not self.used_solve
        ):
            self._submit_daily_run()

    def _erase(self):
        row, column = self.selected
        if not self.givens[row][column]:
            self.history.append(
                {
                    "type": "cell",
                    "row": row,
                    "column": column,
                    "value": self.grid[row][column],
                    "notes": self.notes[row][column].copy(),
                }
            )
            self.grid[row][column] = 0
            self.notes[row][column].clear()
            if self.grid != self.solution and not self.timer.isActive():
                self.started_at = time.monotonic()
                self.timer.start(1000)
            self._save()
            self._render()

    def _undo(self):
        if not self.history:
            return
        action = self.history.pop()
        if action["type"] == "board":
            self.grid = [row[:] for row in action["grid"]]
            self.notes = [
                [notes.copy() for notes in row] for row in action["notes"]
            ]
            self.started_at = time.monotonic()
            self.timer.start(1000)
        else:
            row, column = action["row"], action["column"]
            self.grid[row][column] = action["value"]
            self.notes[row][column] = action["notes"].copy()
            self.selected = (row, column)
            if self.grid != self.solution and not self.timer.isActive():
                self.started_at = time.monotonic()
                self.timer.start(1000)
        self.status_label.setText("Last move undone.")
        self._save()
        self._render()

    def _solve_game(self):
        """Fill the board with its solution as one undoable action."""
        if self.grid == self.solution:
            self.status_label.setText("This puzzle is already solved.")
            return
        self.history.append(
            {
                "type": "board",
                "grid": [row[:] for row in self.grid],
                "notes": [
                    [notes.copy() for notes in row] for row in self.notes
                ],
            }
        )
        if self.daily_date:
            self.used_solve = True
            self._run_cloud_task(
                "reveal",
                lambda: self.cloud.call(
                    "recordDailySolutionReveal", {"date": self.daily_date}
                ),
            )
        self.grid = [row[:] for row in self.solution]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.armed_digit = None
        self.notes_mode = False
        self.elapsed += int(time.monotonic() - self.started_at)
        self.started_at = time.monotonic()
        self.timer.stop()
        self.status_label.setText("Solved. Use Undo to restore your board.")
        self._save()
        self._render()
        for row in range(9):
            for column in range(9):
                if not self.givens[row][column]:
                    delay = (row * 9 + column) * 8
                    QTimer.singleShot(
                        delay,
                        lambda r=row, c=column: self._animate_cell(r, c),
                    )

    def _hint(self):
        if self.daily_date:
            self._run_cloud_task(
                "hint",
                lambda: self.cloud.call(
                    "recordDailyHint", {"date": self.daily_date}
                ),
            )
            return
        self._apply_hint()

    def _apply_hint(self):
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
        if self.grid == self.solution:
            self.timer.stop()
            return
        seconds = self.elapsed + int(time.monotonic() - self.started_at)
        self.time_label.setText(f"{seconds // 60:02d}:{seconds % 60:02d}")
        self._save()

    def _save(self):
        if not hasattr(self, "grid"):
            return
        elapsed = self.elapsed
        if self.grid != self.solution:
            elapsed += int(time.monotonic() - self.started_at)
        state = {
            "grid": self.grid,
            "givens": self.givens,
            "solution": self.solution,
            "difficulty": getattr(self, "difficulty_name", "medium"),
            "notes": [[sorted(values) for values in row] for row in self.notes],
            "selected": list(self.selected),
            "elapsed": elapsed,
            "daily_date": self.daily_date,
            "hints_used": self.hints_used,
            "used_solve": self.used_solve,
            "saved_at_ms": int(time.time() * 1000),
        }
        self.saved_at_ms = state["saved_at_ms"]
        try:
            _STATE_PATH.write_text(json.dumps(state), encoding="utf-8")
        except OSError:
            pass
        if self.cloud.signed_in:
            self._schedule_cloud_sync(state, elapsed)

    def _local_state(self):
        """Return the current offline game without mutable references."""
        return {
            "grid": [row[:] for row in self.grid],
            "givens": [row[:] for row in self.givens],
            "solution": [row[:] for row in self.solution],
            "difficulty": getattr(self, "difficulty_name", "medium"),
            "notes": [[sorted(items) for items in row] for row in self.notes],
            "selected": list(self.selected),
            "elapsed": self.elapsed,
            "saved_at_ms": self.saved_at_ms,
        }

    def _cloud_game(self, state, elapsed):
        """Convert desktop storage to the shared cross-platform schema."""
        theme = "-".join(self.theme_name.replace("&", "").lower().split())
        return {
            "grid": state["grid"],
            "givens": state["givens"],
            "solution": state["solution"],
            "difficulty": state["difficulty"],
            "notes": [
                state["notes"][row][column]
                for row in range(9)
                for column in range(9)
            ],
            "selected": self.selected[0] * 9 + self.selected[1],
            "seconds": elapsed,
            "theme": theme,
            "rapidEntry": self.rapid_entry,
            "dailyDate": self.daily_date,
            "hintsUsed": self.hints_used,
            "usedSolve": self.used_solve,
            "savedAt": state["saved_at_ms"],
        }

    def _schedule_cloud_sync(self, state, elapsed):
        """Coalesce cloud writes and ignore timer-only changes."""
        game = self._cloud_game(state, elapsed)
        signature = json.dumps(
            {
                key: value
                for key, value in game.items()
                if key not in {"seconds", "savedAt"}
            },
            sort_keys=True,
        )
        if signature == self._cloud_signature:
            return
        self._cloud_pending = game
        self._cloud_pending_signature = signature
        if not self._cloud_sync_timer.isActive():
            delay = max(
                1000,
                30000
                - int((time.monotonic() - self._cloud_last_sync_at) * 1000),
            )
            self._cloud_sync_timer.start(delay)

    def _push_cloud_game(self):
        """Upload the latest game on a background worker."""
        if not self.cloud.signed_in or not self._cloud_pending:
            return
        game = self._cloud_pending
        self._cloud_pending = None
        self._cloud_upload_signature = self._cloud_pending_signature
        self._cloud_pending_signature = None
        self._run_cloud_task(
            "sync", lambda: self.cloud.call("syncSavedGame", {"game": game})
        )

    def _run_cloud_task(self, action, operation):
        """Run one network request without blocking the UI."""
        task = CloudTask(action, operation)
        self._cloud_tasks.append(task)
        task.succeeded.connect(self._on_cloud_success)
        task.failed.connect(self._on_cloud_failure)
        task.finished.connect(task.deleteLater)
        task.start()

    @Slot(str, object)
    def _on_cloud_success(self, action, result):
        """Apply the result of a completed cloud request."""
        task = self.sender()
        if task in self._cloud_tasks:
            self._cloud_tasks.remove(task)
        if action == "auth":
            profile, saved = result
            self.cloud.display_name = profile.get(
                "displayName", self.cloud.display_name
            )
            self.account_button.setText(
                self.cloud.display_name[:12] or "Account"
            )
            self.cloud_status.setText(f"Signed in as {self.cloud.email}")
            self.account_dialog.accept()
            if saved.get("game"):
                self._restore_cloud_game(saved["game"])
            else:
                self._schedule_cloud_sync(self._local_state(), self.elapsed)
        elif action == "daily":
            self._apply_daily_challenge(result)
        elif action == "hint":
            self.hints_used = result["hintsUsed"]
            self._apply_hint()
        elif action == "leaderboard":
            self._show_leaderboard_results(result)
        elif action == "submit":
            self.status_label.setText(
                "Daily result ranked."
                if result.get("improved")
                else "Your faster daily result is already ranked."
            )
        elif action == "sync":
            self._cloud_signature = self._cloud_upload_signature
            self._cloud_upload_signature = None
            self._cloud_last_sync_at = time.monotonic()
            self.cloud_status.setText("Cloud save up to date")
            if self._cloud_pending:
                self._schedule_cloud_sync(self._local_state(), self.elapsed)

    @Slot(str, str)
    def _on_cloud_failure(self, action, message):
        """Show cloud errors while preserving offline play."""
        task = self.sender()
        if task in self._cloud_tasks:
            self._cloud_tasks.remove(task)
        self.cloud_status.setText(f"Cloud unavailable: {message}")
        if action == "auth":
            self.account_status.setText(message)
        elif action == "daily":
            self.status_label.setText(f"Daily challenge unavailable: {message}")
        elif action == "leaderboard":
            QMessageBox.warning(self, "Leaderboard", message)
        elif action == "hint":
            self.status_label.setText(f"Could not record daily hint: {message}")

    def _show_account(self):
        """Open email/password or Google sign-in for cloud play."""
        if not self.cloud.configured:
            QMessageBox.information(
                self,
                "Cloud account setup",
                "Set STILL_SUDOKU_FIREBASE_API_KEY and "
                "STILL_SUDOKU_FIREBASE_PROJECT_ID.\n\n"
                "Google sign-in also needs STILL_SUDOKU_GOOGLE_CLIENT_ID.\n"
                "See firebase/README.md for the setup instructions.",
            )
            return
        if self.cloud.signed_in:
            answer = QMessageBox.question(
                self,
                "Account",
                f"Signed in as {self.cloud.email}.\n\nSign out?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self.cloud.id_token = ""
                self.cloud.refresh_token = ""
                self.cloud.uid = ""
                self.cloud.email = ""
                self.account_button.setText("Account")
                self.cloud_status.setText(
                    "Guest mode · offline saves are on this device"
                )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Your Sudoku journey")
        form = QFormLayout(dialog)
        name = QLineEdit()
        name.setPlaceholderText("Leaderboard name (for registration)")
        email = QLineEdit()
        email.setPlaceholderText("you@example.com")
        password = QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        password.setPlaceholderText("At least 6 characters")
        form.addRow("Display name", name)
        form.addRow("Email", email)
        form.addRow("Password", password)
        self.account_status = self._label(
            "Sign in to sync games and join the daily rankings.", "muted"
        )
        self.account_status.setWordWrap(True)
        form.addRow(self.account_status)
        email_buttons = QHBoxLayout()
        sign_in_button = QPushButton("Sign in")
        register_button = QPushButton("Create account")
        email_buttons.addWidget(sign_in_button)
        email_buttons.addWidget(register_button)
        form.addRow(email_buttons)
        google_button = QPushButton("Continue with Google")
        form.addRow(google_button)
        sign_in_button.clicked.connect(
            lambda: self._start_auth_task(
                "signin", email.text(), password.text(), name.text()
            )
        )
        register_button.clicked.connect(
            lambda: self._start_auth_task(
                "register", email.text(), password.text(), name.text()
            )
        )
        google_button.clicked.connect(
            lambda: self._start_auth_task("google", "", "", "")
        )
        self.account_dialog = dialog
        dialog.exec()

    def _start_auth_task(self, mode, email, password, display_name):
        """Validate credentials and authenticate on a worker thread."""
        if mode == "register" and len(display_name.strip()) < 3:
            self.account_status.setText(
                "Choose a display name with at least 3 characters."
            )
            return
        self.account_status.setText("Connecting securely…")
        if mode == "google":

            def authenticate():
                return self.cloud.sign_in_google()
        elif mode == "register":

            def authenticate():
                return self.cloud.register(
                    email.strip(), password, display_name.strip()
                )
        else:

            def authenticate():
                return self.cloud.sign_in(email.strip(), password)

        def load_account():
            authenticate()
            return (
                self.cloud.call("getProfile"),
                self.cloud.call("getSavedGame"),
            )

        self._run_cloud_task("auth", load_account)

    def _start_daily_challenge(self):
        """Fetch today's shared Sudoku challenge."""
        if not self.cloud.configured:
            self.cloud_status.setText("Configure Firebase to use daily play.")
            return
        if not self.cloud.signed_in:
            self._show_account()
            if not self.cloud.signed_in:
                return
        self.status_label.setText("Fetching today's shared puzzle…")
        self._run_cloud_task(
            "daily", lambda: self.cloud.call("getDailyChallenge")
        )

    def _apply_daily_challenge(self, challenge):
        """Replace the current game with today's shared puzzle."""
        puzzle = challenge.get("puzzle")
        solution = solve(puzzle) if isinstance(puzzle, list) else None
        if solution is None or not is_valid(puzzle):
            self.status_label.setText("The daily puzzle is invalid.")
            return
        self.grid = [row[:] for row in puzzle]
        self.givens = [row[:] for row in puzzle]
        self.solution = solution
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.history.clear()
        self.selected = next(
            (
                (row, column)
                for row in range(9)
                for column in range(9)
                if not self.grid[row][column]
            ),
            (0, 0),
        )
        self.elapsed = 0
        self.started_at = time.monotonic()
        self.daily_date = challenge.get("date")
        self.hints_used = 0
        self.used_solve = False
        self.difficulty_name = challenge.get("difficulty", "medium")
        self.difficulty.setCurrentText(self.difficulty_name)
        self.eyebrow.setText(f"DAILY CHALLENGE  ·  {self.daily_date}")
        self.timer.start(1000)
        self.status_label.setText(
            "Today's shared puzzle. Play fair, take your time."
        )
        self._save()
        self._render()

    def _submit_daily_run(self):
        """Submit a correct daily solution unless it was revealed."""
        if not self.daily_date or self.used_solve or not self.cloud.signed_in:
            return
        elapsed = self.elapsed + int(time.monotonic() - self.started_at)
        data = {
            "date": self.daily_date,
            "grid": self.grid,
            "elapsedSeconds": elapsed,
            "hintsUsed": self.hints_used,
            "usedSolve": self.used_solve,
            "displayName": self.cloud.display_name,
        }
        self._run_cloud_task(
            "submit", lambda: self.cloud.call("submitDailyRun", data)
        )

    def _show_leaderboard(self):
        """Fetch today's ranked results."""
        if not self.cloud.signed_in:
            self._show_account()
            if not self.cloud.signed_in:
                return
        self._run_cloud_task(
            "leaderboard", lambda: self.cloud.call("getDailyLeaderboard")
        )

    def _show_leaderboard_results(self, result):
        """Display daily ranking positions and times."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Daily leaderboard · {result.get('date', '')}")
        layout = QVBoxLayout(dialog)
        entries = result.get("entries", [])
        for entry in entries:
            seconds = int(entry.get("score", 0))
            row = QLabel(
                f"{entry.get('rank', 0):>2}.  "
                f"{entry.get('displayName', 'Player')}"
                f" — {seconds // 60:02d}:{seconds % 60:02d}"
                f" · {entry.get('hintsUsed', 0)} hints"
            )
            layout.addWidget(row)
        if not entries:
            layout.addWidget(QLabel("No ranked times yet. Be the first."))
        dialog.exec()

    def _restore_cloud_game(self, game):
        """Apply a valid cloud game if it is newer than the desktop save."""
        try:
            grid, givens, solution = (
                game[key] for key in ("grid", "givens", "solution")
            )
            saved_at = int(game.get("savedAt", 0))
            if (
                len(grid) != 9
                or any(len(row) != 9 for row in grid)
                or not is_valid(givens)
                or not is_valid(solution)
                or any(not value for row in solution for value in row)
            ):
                return
            if saved_at <= self.saved_at_ms:
                if saved_at < self.saved_at_ms:
                    self._schedule_cloud_sync(self._local_state(), self.elapsed)
                return
            if any(
                givens[row][column]
                and givens[row][column] != solution[row][column]
                for row in range(9)
                for column in range(9)
            ):
                return
            if any(
                givens[row][column] and grid[row][column] != givens[row][column]
                for row in range(9)
                for column in range(9)
            ):
                return
            self.grid = [row[:] for row in grid]
            self.givens = [row[:] for row in givens]
            self.solution = [row[:] for row in solution]
            self.selected = divmod(
                max(0, min(80, int(game.get("selected", 0)))), 9
            )
            self.elapsed = max(0, int(game.get("seconds", 0)))
            notes = game.get("notes", [])
            if len(notes) == 81:
                self.notes = [
                    [set(notes[row * 9 + column]) for column in range(9)]
                    for row in range(9)
                ]
            self.daily_date = game.get("dailyDate")
            self.hints_used = max(0, int(game.get("hintsUsed", 0)))
            self.used_solve = bool(game.get("usedSolve", False))
            self.saved_at_ms = saved_at
            self.difficulty_name = game.get("difficulty", "medium")
            self.difficulty.setCurrentText(self.difficulty_name)
            theme_id = game.get("theme", "midnight-garden")
            self.theme_name = next(
                (
                    name
                    for name in THEMES
                    if "-".join(name.replace("&", "").lower().split())
                    == theme_id
                ),
                "Midnight Garden",
            )
            self.rapid_entry = bool(game.get("rapidEntry", True))
            if self.daily_date:
                self.eyebrow.setText(f"DAILY CHALLENGE  ·  {self.daily_date}")
            if self.grid == self.solution:
                self.timer.stop()
            else:
                self.started_at = time.monotonic()
                self.timer.start(1000)
            self._apply_theme(self.theme_name)
            self._render()
            self.status_label.setText("Your latest cloud game is ready.")
        except (KeyError, TypeError, ValueError):
            self.cloud_status.setText("Cloud save could not be restored.")

    def _render(self):
        row, column = self.selected
        selected_value = self.grid[row][column]
        conflicts = self._conflicting_cells()
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
                button.setProperty("error", (r, c) in conflicts)
                button.style().unpolish(button)
                button.style().polish(button)
        for value, button in enumerate(self.number_buttons, start=1):
            button.setProperty("armed", value == self.armed_digit)
            button.style().unpolish(button)
            button.style().polish(button)

    def _conflicting_cells(self):
        """Return only cells participating in row, column, or box conflicts."""
        conflicts = set()
        for row in range(9):
            for column in range(9):
                value = self.grid[row][column]
                if not value:
                    continue
                for other_column in range(column + 1, 9):
                    if self.grid[row][other_column] == value:
                        conflicts.update({(row, column), (row, other_column)})
                for other_row in range(row + 1, 9):
                    if self.grid[other_row][column] == value:
                        conflicts.update({(row, column), (other_row, column)})
                box_row, box_column = row // 3 * 3, column // 3 * 3
                for other_row in range(box_row, box_row + 3):
                    for other_column in range(box_column, box_column + 3):
                        if (other_row, other_column) <= (row, column):
                            continue
                        if self.grid[other_row][other_column] == value:
                            conflicts.update(
                                {(row, column), (other_row, other_column)}
                            )
        return conflicts

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
        elif key == Qt.Key.Key_S:
            self._solve_game()
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
