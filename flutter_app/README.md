# Still Sudoku — Flutter

This is the mobile and cross-platform app edition of Still Sudoku. The Flutter
source shares the same quiet visual direction and core interaction model as
the PySide6 desktop and static web editions.

## Requirements

- Flutter 3.38 or newer
- Dart 3.10 or newer
- `uv` is used for the Python desktop/web tooling in the parent repository;
  Flutter dependencies are managed by `flutter pub`.

## Create platform runners and launch

From this directory, create the platform-specific runner folders once, then
fetch dependencies and launch on a connected device or simulator:

```bash
flutter create --no-overwrite --project-name still_sudoku --platforms=android,ios,web,windows,macos,linux .
flutter pub get
flutter run
```

For a Flutter Web build suitable for a static host:

```bash
flutter build web
```

The web bundle is written to `build/web/`. Android and iOS builds use the
usual `flutter build apk` and `flutter build ios` commands. Building iOS needs
macOS and Xcode.

## Features

- 20 palettes with color and miniature-board previews. Selecting one previews
  it live; **Cancel** restores the previous palette, while **Keep changes**
  saves the choice.
- Quick number-first placement: choose a digit, then tap as many editable
  cells as needed. Turn off Quick entry in Settings to select a cell first.
- Pencil notes, erase, undo, hints, keyboard navigation, and one-tap animated
  solving.
- Easy, medium, hard, and expert puzzle generation. Generation runs away from
  the UI thread and keeps puzzles uniquely solvable.
- Local game and settings persistence through `SharedPreferencesAsync`.
- Responsive layout for narrow phones through wide desktop windows.

## Keyboard

Arrow keys move the selection; `1`–`9` enter a digit; `0`, Backspace, or Delete
clears a cell; `N` toggles notes; `Ctrl+Z` undoes; `S` reveals the solution;
`Esc` clears the selected quick-entry digit.

## Checks

Run `flutter analyze` and `flutter test` from this directory. The engine tests
cover solving, input immutability, invalid boards, and unique puzzle generation.
