"""Launch the PySide6 Sudoku application."""

import sys

from PySide6.QtWidgets import QApplication

from sudoku.desktop import SudokuWindow


def main():
    """Start the application event loop."""
    app = QApplication(sys.argv)
    app.setApplicationName("Beautiful Sudoku")
    app.setStyle("Fusion")
    window = SudokuWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
