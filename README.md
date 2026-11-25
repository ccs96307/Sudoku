# Still Sudoku

A quiet, polished Sudoku experience with a native PySide6 desktop app and a
static web edition ready for GitHub Pages. Puzzles are generated locally and
are checked for a unique solution.

## Desktop app

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python main.py
```

The desktop app includes four difficulty targets, keyboard navigation, pencil
notes, undo, hints, conflict highlighting, a timer, and automatic local saves
in `~/.beautiful-sudoku.json`.

## Web app

Open `web/index.html` directly, or serve the `web/` directory with any static
HTTP server. No build step, package manager, or server API is required. The
browser edition includes responsive layouts, light and dark themes, keyboard
controls, pencil notes, undo, hints, progress tracking, a service-worker app
shell for repeat offline visits, and automatic `localStorage` saves.

To publish with GitHub Pages, merge the project into `main` or `master`, then
in the repository settings choose **Pages → GitHub Actions**. The included
workflow publishes the contents of `web/` on each relevant push.

## Structure

- `sudoku/engine.py` — validation, candidate lookup, backtracking solver, and
  randomized unique-puzzle generator.
- `sudoku/desktop.py` — PySide6 interface and desktop game state.
- `main.py` — desktop entry point.
- `web/` — self-contained static web application.
- `.github/workflows/pages.yml` — GitHub Pages deployment.

## Controls

| Action | Desktop and web |
| --- | --- |
| Select a cell | Click / tap |
| Move selection | Arrow keys |
| Enter a digit | `1`–`9` |
| Erase a cell | `0`, Backspace, or Delete |
| Toggle pencil notes | `N` or Notes button |
| Undo | `Ctrl+Z` or Undo button |
| Get a hint | Hint button |

## Design notes

The app keeps the game private and offline: puzzles, timer state, and progress
stay on the current device. The generator shuffles a solved grid and removes
clues only while the puzzle retains exactly one solution. Difficulty labels
set clue-count targets (40, 34, 29, and 25); actual human solving difficulty
also depends on the puzzle's logical techniques, so the labels are approximate.


## Further improvement ideas

The core game and both clients are intentionally framework-light. Strong next
steps include logical-technique difficulty rating (instead of clue-count labels),
a daily seeded puzzle, accessible screen-reader announcements for conflicts,
a focused test suite for generator uniqueness and UI interactions, and desktop
release bundles for Windows, macOS, and Linux. The current puzzle generator
checks uniqueness but does not rate human solving techniques, and the desktop
app currently saves one in-progress game per device.
