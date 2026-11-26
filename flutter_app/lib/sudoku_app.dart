import 'dart:async';
import 'dart:convert';

import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'cloud_service.dart';
import 'sudoku_engine.dart';
import 'theme_palette.dart';

class SudokuApp extends StatelessWidget {
  const SudokuApp({super.key});

  @override
  Widget build(BuildContext context) =>
      const MaterialApp(debugShowCheckedModeBanner: false, home: SudokuHome());
}

class _Snapshot {
  const _Snapshot(this.grid, this.notes);
  final SudokuGrid grid;
  final List<Set<int>> notes;
}

class SudokuHome extends StatefulWidget {
  const SudokuHome({super.key});

  @override
  State<SudokuHome> createState() => _SudokuHomeState();
}

class _SudokuHomeState extends State<SudokuHome> {
  static const _storageKey = 'still_sudoku_state_v1';
  final _prefs = SharedPreferencesAsync();
  final _focusNode = FocusNode();
  SudokuPalette _palette = SudokuPalette.all.first;
  SudokuGrid _grid = List.generate(9, (_) => List.filled(9, 0));
  SudokuGrid _givens = List.generate(9, (_) => List.filled(9, 0));
  SudokuGrid _solution = List.generate(9, (_) => List.filled(9, 0));
  List<Set<int>> _notes = List.generate(81, (_) => <int>{});
  final List<_Snapshot> _history = [];
  int _selected = 40;
  int _seconds = 0;
  int? _armedDigit;
  String _difficulty = 'medium';
  bool _rapidEntry = true;
  bool _pencil = false;
  bool _busy = false;
  bool _loaded = false;
  Timer? _timer;
  StreamSubscription<User?>? _authSubscription;
  Future<void> _saveQueue = Future<void>.value();
  String? _message;
  String? _dailyDate;
  int _hintsUsed = 0;
  bool _usedSolve = false;
  int _savedAt = 0;
  User? _user;
  bool _cloudReady = false;
  String? _cloudError;

  @override
  void initState() {
    super.initState();
    unawaited(_restore());
    unawaited(_initializeCloud());
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted || !_loaded || _isSolved) return;
      setState(() => _seconds++);
      if (_seconds % 5 == 0) unawaited(_save());
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    unawaited(_authSubscription?.cancel());
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _initializeCloud() async {
    final cloud = CloudService.instance;
    await cloud.initialize();
    if (!mounted) return;
    setState(() {
      _cloudReady = cloud.ready;
      _cloudError = cloud.setupError;
      _user = cloud.currentUser;
    });
    _authSubscription = cloud.authChanges.listen((user) {
      if (!mounted) return;
      setState(() => _user = user);
      if (user != null) unawaited(_restoreCloudGame());
    });
  }

  bool get _isSolved =>
      _grid.every((row) => row.every((value) => value != 0)) &&
      _grid.asMap().entries.every(
        (row) => row.value.asMap().entries.every(
          (cell) => cell.value == _solution[row.key][cell.key],
        ),
      );

  Future<void> _restore() async {
    try {
      final raw = await _prefs.getString(_storageKey);
      if (raw != null) {
        final data = jsonDecode(raw) as Map<String, dynamic>;
        final grid = _decodeGrid(data['grid']);
        final givens = _decodeGrid(data['givens']);
        final solution = _decodeGrid(data['solution']);
        if (grid != null &&
            givens != null &&
            solution != null &&
            _hasGridShape(grid) &&
            isValidGrid(givens) &&
            isValidGrid(solution)) {
          _grid = grid;
          _givens = givens;
          _solution = solution;
          _seconds = (data['seconds'] as num?)?.toInt() ?? 0;
          _selected =
              (data['selected'] as num?)?.toInt().clamp(0, 80).toInt() ?? 40;
          _difficulty = data['difficulty'] as String? ?? 'medium';
          _palette = SudokuPalette.byId(
            data['theme'] as String? ?? 'midnight-garden',
          );
          _rapidEntry = data['rapidEntry'] as bool? ?? true;
          _dailyDate = data['dailyDate'] as String?;
          _hintsUsed = (data['hintsUsed'] as num?)?.toInt() ?? 0;
          _usedSolve = data['usedSolve'] as bool? ?? false;
          _savedAt = (data['savedAt'] as num?)?.toInt() ?? 0;
          final storedNotes = data['notes'];
          if (storedNotes is List && storedNotes.length == 81) {
            _notes = storedNotes
                .map(
                  (values) => (values as List)
                      .whereType<num>()
                      .map((value) => value.toInt())
                      .toSet(),
                )
                .toList();
          }
        }
      }
    } catch (_) {
      // A corrupt save should start a fresh game rather than block the app.
    }
    if (!mounted) return;
    setState(() => _loaded = true);
    if (_solution.every((row) => row.every((value) => value == 0))) {
      await _newGame();
    }
  }

  SudokuGrid? _decodeGrid(dynamic value) {
    if (value is! List || value.length != 9) return null;
    try {
      final grid = value
          .map(
            (row) =>
                (row as List).map((cell) => (cell as num).toInt()).toList(),
          )
          .toList();
      return _hasGridShape(grid) ? grid : null;
    } catch (_) {
      return null;
    }
  }

  bool _hasGridShape(SudokuGrid grid) =>
      grid.length == 9 &&
      grid.every(
        (row) =>
            row.length == 9 && row.every((value) => value >= 0 && value <= 9),
      );

  Future<void> _save() {
    _savedAt = DateTime.now().millisecondsSinceEpoch;
    final state = {
      'grid': _grid,
      'givens': _givens,
      'solution': _solution,
      'notes': _notes.map((values) => values.toList()).toList(),
      'seconds': _seconds,
      'selected': _selected,
      'difficulty': _difficulty,
      'theme': _palette.id,
      'rapidEntry': _rapidEntry,
      'dailyDate': _dailyDate,
      'hintsUsed': _hintsUsed,
      'usedSolve': _usedSolve,
      'savedAt': _savedAt,
    };
    final data = jsonEncode(state);
    _saveQueue = _saveQueue.then((_) => _prefs.setString(_storageKey, data));
    CloudService.instance.scheduleGameSync(state);
    return _saveQueue;
  }

  Future<void> _restoreCloudGame() async {
    try {
      final saved = await CloudService.instance.getSavedGame();
      if (!mounted || saved == null) return;
      final grid = _decodeGrid(saved['grid']);
      final givens = _decodeGrid(saved['givens']);
      final solution = _decodeGrid(saved['solution']);
      final savedAt = (saved['savedAt'] as num?)?.toInt() ?? 0;
      if (grid == null ||
          givens == null ||
          solution == null ||
          !isValidGrid(givens) ||
          !isValidGrid(solution) ||
          savedAt <= _savedAt ||
          solution.any((row) => row.contains(0))) {
        if (savedAt < _savedAt) unawaited(_save());
        return;
      }
      setState(() {
        _grid = grid;
        _givens = givens;
        _solution = solution;
        _seconds = (saved['seconds'] as num?)?.toInt() ?? 0;
        _selected =
            (saved['selected'] as num?)?.toInt().clamp(0, 80).toInt() ?? 40;
        _difficulty = saved['difficulty'] as String? ?? 'medium';
        _palette = SudokuPalette.byId(
          saved['theme'] as String? ?? 'midnight-garden',
        );
        _rapidEntry = saved['rapidEntry'] as bool? ?? true;
        _dailyDate = saved['dailyDate'] as String?;
        _hintsUsed = (saved['hintsUsed'] as num?)?.toInt() ?? 0;
        _usedSolve = saved['usedSolve'] as bool? ?? false;
        _savedAt = savedAt;
        final notes = saved['notes'];
        if (notes is List && notes.length == 81) {
          _notes = notes
              .map(
                (items) => (items as List)
                    .whereType<num>()
                    .map((value) => value.toInt())
                    .toSet(),
              )
              .toList();
        }
        _message = 'Your latest cloud game is ready.';
      });
      await _save();
    } catch (error) {
      if (mounted) {
        setState(() => _message = 'Could not restore cloud game: $error');
      }
    }
  }

  Future<void> _newGame() async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      final generated = await compute(generatePuzzleForIsolate, _difficulty);
      if (!mounted) return;
      setState(() {
        _grid = copyGrid(generated.puzzle);
        _givens = copyGrid(generated.puzzle);
        _solution = copyGrid(generated.solution);
        _notes = List.generate(81, (_) => <int>{});
        _history.clear();
        _seconds = 0;
        _selected = 40;
        _dailyDate = null;
        _hintsUsed = 0;
        _usedSolve = false;
        _armedDigit = null;
        _busy = false;
        _message = 'A fresh grid, just for you.';
      });
      await _save();
    } catch (error) {
      if (mounted) {
        setState(() {
          _busy = false;
          _message = 'Could not create a puzzle: $error';
        });
      }
    }
  }

  void _remember() {
    _history.add(
      _Snapshot(
        copyGrid(_grid),
        _notes.map((items) => Set<int>.of(items)).toList(),
      ),
    );
    if (_history.length > 80) _history.removeAt(0);
  }

  void _undo() {
    if (_history.isEmpty) return;
    final snapshot = _history.removeLast();
    setState(() {
      _grid = copyGrid(snapshot.grid);
      _notes = snapshot.notes;
      _message = 'Last move undone.';
    });
    unawaited(_save());
  }

  void _enter(int digit) {
    final row = _selected ~/ 9;
    final column = _selected % 9;
    if (_givens[row][column] != 0 || _isSolved) return;
    _remember();
    setState(() {
      if (_pencil) {
        final marks = _notes[_selected];
        if (!marks.add(digit)) marks.remove(digit);
      } else {
        _grid[row][column] = digit;
        _notes[_selected].clear();
      }
      _message =
          _grid[row][column] != 0 &&
              _grid[row][column] != _solution[row][column]
          ? 'That number conflicts with the solution.'
          : 'Nice move.';
    });
    unawaited(_save());
    if (!_pencil && _isSolved) unawaited(_submitDailyRun());
  }

  void _erase() {
    final row = _selected ~/ 9;
    final column = _selected % 9;
    if (_givens[row][column] != 0) return;
    _remember();
    setState(() {
      _grid[row][column] = 0;
      _notes[_selected].clear();
      _message = 'Cell cleared.';
    });
    unawaited(_save());
  }

  Future<void> _solve() async {
    if (_isSolved || _busy) return;
    _remember();
    setState(() {
      _busy = true;
      _message = 'A little clarity is on its way…';
    });
    if (_dailyDate != null) {
      _usedSolve = true;
      try {
        await CloudService.instance.recordDailySolutionReveal(_dailyDate!);
      } catch (_) {
        // The local reveal still disqualifies this run from ranking.
      }
    }
    for (var i = 0; i < 81; i++) {
      if (!mounted) return;
      final row = i ~/ 9;
      final column = i % 9;
      if (_givens[row][column] == 0) {
        setState(() {
          _grid[row][column] = _solution[row][column];
          _notes[i].clear();
        });
        await Future<void>.delayed(const Duration(milliseconds: 12));
      }
    }
    if (!mounted) return;
    setState(() {
      _busy = false;
      _message = 'Solved. Take a breath and enjoy the quiet.';
    });
    await _save();
  }

  Future<void> _hint() async {
    final row = _selected ~/ 9;
    final column = _selected % 9;
    if (_givens[row][column] != 0 ||
        _grid[row][column] == _solution[row][column]) {
      final empty = [for (var i = 0; i < 81; i++) i].where(
        (i) =>
            _givens[i ~/ 9][i % 9] == 0 &&
            _grid[i ~/ 9][i % 9] != _solution[i ~/ 9][i % 9],
      );
      if (empty.isNotEmpty) setState(() => _selected = empty.first);
    }
    if (_dailyDate != null) {
      try {
        final result = await CloudService.instance.recordDailyHint(_dailyDate!);
        _hintsUsed = (result['hintsUsed'] as num).toInt();
      } catch (error) {
        if (mounted) {
          setState(
            () => _message = 'Connect to keep daily hints ranked: $error',
          );
        }
        return;
      }
    }
    _enter(_solution[_selected ~/ 9][_selected % 9]);
    setState(() => _message = 'A small hint, right where you need it.');
  }

  Future<void> _submitDailyRun() async {
    if (_dailyDate == null || _user == null || _usedSolve || !_cloudReady) {
      return;
    }
    try {
      final result = await CloudService.instance.submitDailyRun(
        date: _dailyDate!,
        grid: _grid,
        elapsedSeconds: _seconds,
        hintsUsed: _hintsUsed,
        usedSolve: _usedSolve,
      );
      if (!mounted) return;
      setState(
        () => _message = result['improved'] == true
            ? 'Your daily time has been ranked, including hint penalties.'
            : 'Your best daily time is already on the board.',
      );
    } catch (error) {
      if (mounted) {
        setState(
          () => _message = 'Solved locally; ranking could not be saved: $error',
        );
      }
    }
  }

  Future<void> _startDailyChallenge() async {
    if (!_cloudReady) {
      setState(
        () => _message =
            _cloudError ?? 'Add Firebase settings to enable daily challenges.',
      );
      return;
    }
    if (_user == null) {
      await _showAccount();
      if (!mounted || _user == null) return;
    }
    setState(() {
      _busy = true;
      _message = 'Fetching today’s shared puzzle…';
    });
    try {
      final challenge = await CloudService.instance.getDailyChallenge();
      final puzzle = _decodeGrid(challenge['puzzle']);
      if (puzzle == null || !isValidGrid(puzzle)) {
        throw StateError('Invalid daily board.');
      }
      final solution = await compute(solveSudokuForIsolate, puzzle);
      if (solution == null || !mounted) {
        throw StateError('Daily board has no solution.');
      }
      setState(() {
        _grid = copyGrid(puzzle);
        _givens = copyGrid(puzzle);
        _solution = solution;
        _notes = List.generate(81, (_) => <int>{});
        _history.clear();
        _seconds = 0;
        _selected = 40;
        _difficulty = challenge['difficulty'] as String? ?? 'medium';
        _dailyDate = challenge['date'] as String?;
        _hintsUsed = 0;
        _usedSolve = false;
        _busy = false;
        _message = 'Today’s shared puzzle. Play fair, take your time.';
      });
      await _save();
    } catch (error) {
      if (mounted) {
        setState(() {
          _busy = false;
          _message = 'Daily challenge is unavailable: $error';
        });
      }
    }
  }

  Future<void> _showAccount() async {
    if (!_cloudReady) {
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Connect your Firebase project'),
          content: Text(
            _cloudError ??
                'Add Firebase app settings with dart-define values. See '
                    'flutter_app/README.md for the setup steps.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      );
      return;
    }
    if (_user != null) {
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Your Sudoku journey'),
          content: Text('Signed in as ${_user!.email ?? _user!.displayName}.'),
          actions: [
            TextButton(
              onPressed: () async {
                await CloudService.instance.signOut();
                if (context.mounted) Navigator.pop(context);
              },
              child: const Text('Sign out'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Done'),
            ),
          ],
        ),
      );
      return;
    }

    final email = TextEditingController();
    final password = TextEditingController();
    final displayName = TextEditingController();
    var registering = false;
    var busy = false;
    var errorMessage = '';
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, refresh) => AlertDialog(
          title: Text(registering ? 'Create your account' : 'Welcome back'),
          content: SizedBox(
            width: 380,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (registering)
                    TextField(
                      controller: displayName,
                      maxLength: 24,
                      decoration: const InputDecoration(
                        labelText: 'Display name',
                      ),
                    ),
                  TextField(
                    controller: email,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(labelText: 'Email'),
                  ),
                  TextField(
                    controller: password,
                    obscureText: true,
                    decoration: const InputDecoration(labelText: 'Password'),
                  ),
                  if (errorMessage.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: Text(
                        errorMessage,
                        style: TextStyle(color: _palette.error),
                      ),
                    ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: busy
                        ? null
                        : () async {
                            refresh(() {
                              busy = true;
                              errorMessage = '';
                            });
                            try {
                              await CloudService.instance.signInWithGoogle();
                              if (dialogContext.mounted) {
                                Navigator.pop(dialogContext);
                              }
                            } catch (error) {
                              refresh(() => errorMessage = error.toString());
                            } finally {
                              refresh(() => busy = false);
                            }
                          },
                    icon: const Icon(Icons.account_circle_outlined),
                    label: const Text('Continue with Google'),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: busy
                  ? null
                  : () => refresh(() => registering = !registering),
              child: Text(registering ? 'Sign in instead' : 'Create account'),
            ),
            FilledButton(
              onPressed: busy
                  ? null
                  : () async {
                      refresh(() {
                        busy = true;
                        errorMessage = '';
                      });
                      try {
                        if (registering) {
                          await CloudService.instance.register(
                            email.text.trim(),
                            password.text,
                            displayName.text.trim(),
                          );
                        } else {
                          await CloudService.instance.signIn(
                            email.text.trim(),
                            password.text,
                          );
                        }
                        if (dialogContext.mounted) Navigator.pop(dialogContext);
                      } catch (error) {
                        refresh(() => errorMessage = error.toString());
                      } finally {
                        refresh(() => busy = false);
                      }
                    },
              child: Text(registering ? 'Create account' : 'Sign in'),
            ),
          ],
        ),
      ),
    );
    email.dispose();
    password.dispose();
    displayName.dispose();
  }

  Future<void> _showLeaderboard() async {
    if (!_cloudReady || _user == null) {
      await _showAccount();
      if (!mounted || _user == null) return;
    }
    try {
      final data = await CloudService.instance.getLeaderboard();
      if (!mounted) return;
      final entries = (data['entries'] as List? ?? const [])
          .whereType<Map>()
          .map((entry) => Map<String, dynamic>.from(entry))
          .toList();
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('Daily leaderboard · ${data['date']}'),
          content: SizedBox(
            width: 420,
            child: entries.isEmpty
                ? const Text('No ranked times yet. Be the first.')
                : ListView.builder(
                    shrinkWrap: true,
                    itemCount: entries.length,
                    itemBuilder: (context, index) {
                      final entry = entries[index];
                      final seconds = (entry['score'] as num).toInt();
                      final time =
                          '${(seconds ~/ 60).toString().padLeft(2, '0')}:${(seconds % 60).toString().padLeft(2, '0')}';
                      return ListTile(
                        leading: CircleAvatar(child: Text('${entry['rank']}')),
                        title: Text(
                          entry['displayName'] as String? ?? 'Player',
                        ),
                        subtitle: Text('${entry['hintsUsed'] ?? 0} hints'),
                        trailing: Text(
                          time,
                          style: TextStyle(color: _palette.accent),
                        ),
                      );
                    },
                  ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    } catch (error) {
      if (mounted) setState(() => _message = 'Leaderboard unavailable: $error');
    }
  }

  void _onKey(KeyEvent event) {
    if (event is! KeyDownEvent || !_focusNode.hasFocus) return;
    final key = event.logicalKey;
    if (key == LogicalKeyboardKey.arrowLeft) {
      _move(-1, 0);
    } else if (key == LogicalKeyboardKey.arrowRight) {
      _move(1, 0);
    } else if (key == LogicalKeyboardKey.arrowUp) {
      _move(0, -1);
    } else if (key == LogicalKeyboardKey.arrowDown) {
      _move(0, 1);
    } else if (key == LogicalKeyboardKey.keyS) {
      unawaited(_solve());
    } else if (key == LogicalKeyboardKey.keyN) {
      setState(() => _pencil = !_pencil);
    } else if (key == LogicalKeyboardKey.keyZ &&
        HardwareKeyboard.instance.isControlPressed) {
      _undo();
    } else if (key == LogicalKeyboardKey.escape) {
      setState(() => _armedDigit = null);
    } else if (key == LogicalKeyboardKey.backspace ||
        key == LogicalKeyboardKey.delete ||
        key == LogicalKeyboardKey.digit0) {
      _erase();
    } else {
      for (var digit = 1; digit <= 9; digit++) {
        if (key.keyId == 0x30 + digit ||
            key.keyId == 0x100000000 + 0x300 + digit) {
          _enter(digit);
          break;
        }
      }
    }
  }

  void _move(int dx, int dy) {
    final row = (_selected ~/ 9 + dy).clamp(0, 8).toInt();
    final column = (_selected % 9 + dx).clamp(0, 8).toInt();
    setState(() => _selected = row * 9 + column);
  }

  String get _time =>
      '${(_seconds ~/ 60).toString().padLeft(2, '0')}:${(_seconds % 60).toString().padLeft(2, '0')}';

  @override
  Widget build(BuildContext context) {
    final palette = _palette;
    final dark = !palette.isLight;
    final theme = ThemeData(
      brightness: dark ? Brightness.dark : Brightness.light,
      scaffoldBackgroundColor: palette.background,
      colorScheme: ColorScheme.fromSeed(
        seedColor: palette.accent,
        brightness: dark ? Brightness.dark : Brightness.light,
        surface: palette.panel,
        primary: palette.accent,
        onPrimary: palette.accentInk,
      ),
      fontFamily: 'Georgia',
      useMaterial3: true,
    );
    return Theme(
      data: theme,
      child: Scaffold(
        body: SafeArea(
          child: KeyboardListener(
            focusNode: _focusNode,
            onKeyEvent: _onKey,
            child: GestureDetector(
              onTap: () => _focusNode.requestFocus(),
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final wide = constraints.maxWidth >= 980;
                  final content = wide
                      ? Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Expanded(child: _intro()),
                            const SizedBox(width: 52),
                            SizedBox(width: 550, child: _gamePanel()),
                          ],
                        )
                      : Column(
                          children: [
                            _brandBar(),
                            const SizedBox(height: 4),
                            _gamePanel(compact: true),
                          ],
                        );
                  return Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1320),
                      child: SingleChildScrollView(
                        padding: EdgeInsets.symmetric(
                          horizontal: wide ? 64 : 16,
                          vertical: wide ? 28 : 8,
                        ),
                        child: content,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ),
        floatingActionButton: null,
      ),
    );
  }

  Widget _brandBar() => Row(
    children: [
      Text(
        'STILL',
        style: TextStyle(
          color: _palette.accent,
          fontSize: 14,
          letterSpacing: 4,
          fontWeight: FontWeight.w800,
        ),
      ),
      const SizedBox(width: 12),
      Text(
        'SUDOKU  /  09',
        style: TextStyle(
          color: _palette.muted,
          fontSize: 11,
          letterSpacing: 2,
        ),
      ),
      const Spacer(),
      IconButton(
        onPressed: _showAccount,
        icon: Icon(_user == null ? Icons.person_outline : Icons.cloud_done),
        tooltip: _user?.email ?? 'Account and cloud sync',
      ),
      IconButton(
        onPressed: _showSettings,
        icon: const Icon(Icons.tune_rounded),
        tooltip: 'Settings',
      ),
    ],
  );

  Widget _intro({bool compact = false}) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        children: [
          Text(
            'STILL',
            style: TextStyle(
              color: _palette.accent,
              fontSize: 14,
              letterSpacing: 4,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(width: 12),
          Text(
            'SUDOKU  /  09',
            style: TextStyle(
              color: _palette.muted,
              fontSize: 11,
              letterSpacing: 2,
            ),
          ),
          const Spacer(),
          IconButton(
            onPressed: _showAccount,
            icon: Icon(_user == null ? Icons.person_outline : Icons.cloud_done),
            tooltip: _user?.email ?? 'Account and cloud sync',
          ),
          IconButton(
            onPressed: _showSettings,
            icon: const Icon(Icons.tune_rounded),
            tooltip: 'Settings',
          ),
        ],
      ),
      const SizedBox(height: 38),
      Text(
        'A little clarity.',
        style: TextStyle(
          color: _palette.text,
          fontSize: compact ? 38 : 58,
          height: 1.03,
          letterSpacing: -2,
        ),
      ),
      const SizedBox(height: 14),
      Text(
        'One quiet square at a time.',
        style: TextStyle(color: _palette.muted, fontSize: 18),
      ),
      const SizedBox(height: 28),
      Container(
        width: 52,
        height: 3,
        decoration: BoxDecoration(
          color: _palette.accent,
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      if (!compact) ...[
        const SizedBox(height: 28),
        Text(
          _message ?? 'A small pause for your mind.',
          style: TextStyle(color: _palette.muted, fontSize: 15, height: 1.5),
        ),
        const SizedBox(height: 24),
        _legend(),
      ],
    ],
  );

  Widget _legend() => Wrap(
    spacing: 18,
    runSpacing: 10,
    children: [
      _legendDot(_palette.given, 'Given'),
      _legendDot(_palette.entry, 'Your entries'),
      _legendDot(_palette.accent, 'Selected'),
    ],
  );
  Widget _legendDot(Color color, String label) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Container(
        width: 11,
        height: 11,
        decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      ),
      const SizedBox(width: 7),
      Text(label, style: TextStyle(color: _palette.muted, fontSize: 12)),
    ],
  );

  Widget _gamePanel({bool compact = false}) => Column(
    children: [
      Row(
        children: [
          Text(
            _difficulty.toUpperCase(),
            style: TextStyle(
              color: _palette.muted,
              fontSize: 11,
              letterSpacing: 2,
            ),
          ),
          const Spacer(),
          Icon(Icons.schedule_rounded, size: 15, color: _palette.muted),
          const SizedBox(width: 7),
          Text(
            _time,
            style: TextStyle(
              color: _palette.text,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ],
      ),
      SizedBox(height: compact ? 5 : 12),
      Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              onPressed: _busy ? null : _startDailyChallenge,
              icon: const Icon(Icons.today_rounded, size: 17),
              label: const Text('Daily challenge'),
            ),
          ),
          const SizedBox(width: 9),
          IconButton.outlined(
            onPressed: _showLeaderboard,
            icon: const Icon(Icons.leaderboard_outlined),
            tooltip: 'Daily leaderboard',
          ),
        ],
      ),
      SizedBox(height: compact ? 5 : 8),
      _board(),
      SizedBox(height: compact ? 7 : 16),
      _numberPad(compact: compact),
      SizedBox(height: compact ? 7 : 15),
      Wrap(
        alignment: WrapAlignment.center,
        spacing: compact ? 5 : 8,
        runSpacing: compact ? 5 : 8,
        children: [
          _actionButton(
            Icons.edit_note_rounded,
            'Notes',
            () => setState(() => _pencil = !_pencil),
            active: _pencil,
            compact: compact,
          ),
          _actionButton(
            Icons.lightbulb_outline_rounded,
            'Hint',
            () => unawaited(_hint()),
            compact: compact,
          ),
          _actionButton(
            Icons.backspace_outlined,
            'Erase',
            _erase,
            compact: compact,
          ),
          _actionButton(
            Icons.undo_rounded,
            'Undo',
            _undo,
            enabled: _history.isNotEmpty,
            compact: compact,
          ),
        ],
      ),
      SizedBox(height: compact ? 7 : 12),
      Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              onPressed: _busy ? null : _showDifficulty,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('New puzzle'),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: FilledButton.icon(
              onPressed: _busy ? null : _solve,
              icon: const Icon(Icons.auto_awesome_rounded),
              label: const Text('Solve'),
            ),
          ),
        ],
      ),
      if (_message != null) ...[
        const SizedBox(height: 12),
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 220),
          child: Text(
            _message!,
            key: ValueKey(_message),
            textAlign: TextAlign.center,
            style: TextStyle(color: _palette.muted, fontSize: 12),
          ),
        ),
      ],
    ],
  );

  Widget _board() => AspectRatio(
    aspectRatio: 1,
    child: DecoratedBox(
      decoration: BoxDecoration(
        color: _palette.panel,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: _palette.text.withValues(alpha: .08),
            blurRadius: 35,
            offset: const Offset(0, 14),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(18),
        child: GridView.builder(
          physics: const NeverScrollableScrollPhysics(),
          padding: EdgeInsets.zero,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 9,
          ),
          itemCount: 81,
          itemBuilder: (context, index) {
            final row = index ~/ 9;
            final col = index % 9;
            final value = _grid[row][col];
            final selected = index == _selected;
            final related =
                row == _selected ~/ 9 ||
                col == _selected % 9 ||
                (row ~/ 3 == _selected ~/ 9 ~/ 3 &&
                    col ~/ 3 == _selected % 9 ~/ 3);
            final same =
                value != 0 && value == _grid[_selected ~/ 9][_selected % 9];
            final conflict = value != 0 && value != _solution[row][col];
            final thickRight = col == 2 || col == 5;
            final thickBottom = row == 2 || row == 5;
            return GestureDetector(
              onTap: () {
                setState(() => _selected = index);
                if (_rapidEntry && _armedDigit != null) _enter(_armedDigit!);
                _focusNode.requestFocus();
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                curve: Curves.easeOut,
                decoration: BoxDecoration(
                  color: selected
                      ? _palette.accent
                      : conflict
                      ? _palette.errorBackground
                      : same
                      ? _palette.same
                      : related
                      ? _palette.related
                      : _palette.panel,
                  border: Border(
                    left: BorderSide(
                      color: selected ? Colors.white : _palette.line,
                      width: selected
                          ? 3
                          : col % 3 == 0
                          ? 1.4
                          : .45,
                    ),
                    top: BorderSide(
                      color: selected ? Colors.white : _palette.line,
                      width: selected
                          ? 3
                          : row % 3 == 0
                          ? 1.4
                          : .45,
                    ),
                    right: BorderSide(
                      color: selected ? Colors.white : _palette.line,
                      width: selected
                          ? 3
                          : thickRight
                          ? 1.5
                          : .45,
                    ),
                    bottom: BorderSide(
                      color: selected ? Colors.white : _palette.line,
                      width: selected
                          ? 3
                          : thickBottom
                          ? 1.5
                          : .45,
                    ),
                  ),
                  boxShadow: selected
                      ? [
                          BoxShadow(
                            color: _palette.accent.withValues(alpha: .75),
                            blurRadius: 13,
                            spreadRadius: 1,
                          ),
                        ]
                      : null,
                ),
                child: Center(
                  child: value != 0
                      ? AnimatedSwitcher(
                          duration: const Duration(milliseconds: 180),
                          transitionBuilder: (child, animation) =>
                              ScaleTransition(scale: animation, child: child),
                          child: Text(
                            '$value',
                            key: ValueKey('$index-$value'),
                            style: TextStyle(
                              color: selected
                                  ? _palette.accentInk
                                  : conflict
                                  ? _palette.error
                                  : _givens[row][col] != 0
                                  ? _palette.given
                                  : _palette.entry,
                              fontSize: 23,
                              fontWeight: _givens[row][col] != 0
                                  ? FontWeight.w800
                                  : FontWeight.w600,
                            ),
                          ),
                        )
                      : _noteView(index),
                ),
              ),
            );
          },
        ),
      ),
    ),
  );

  Widget _noteView(int index) => GridView.count(
    physics: const NeverScrollableScrollPhysics(),
    padding: const EdgeInsets.all(1),
    crossAxisCount: 3,
    children: [
      for (var digit = 1; digit <= 9; digit++)
        Center(
          child: Text(
            _notes[index].contains(digit) ? '$digit' : '',
            style: TextStyle(color: _palette.entry, fontSize: 8),
          ),
        ),
    ],
  );

  Widget _numberPad({bool compact = false}) => Row(
    children: [
      for (var digit = 1; digit <= 9; digit++)
        Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2),
            child: InkWell(
              onTap: () {
                if (_rapidEntry) {
                  setState(
                    () => _armedDigit = _armedDigit == digit ? null : digit,
                  );
                } else {
                  _enter(digit);
                }
              },
              borderRadius: BorderRadius.circular(10),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 160),
                height: compact ? 40 : 48,
                decoration: BoxDecoration(
                  color: _armedDigit == digit
                      ? _palette.accent
                      : _palette.panel,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: _armedDigit == digit
                        ? _palette.accent
                        : _palette.line,
                  ),
                ),
                child: Center(
                  child: Text(
                    '$digit',
                    style: TextStyle(
                      color: _armedDigit == digit
                          ? _palette.accentInk
                          : _palette.text,
                      fontSize: compact ? 16 : 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
    ],
  );

  Widget _actionButton(
    IconData icon,
    String label,
    VoidCallback action, {
    bool active = false,
    bool enabled = true,
    bool compact = false,
  }) => OutlinedButton.icon(
    onPressed: enabled ? action : null,
    icon: Icon(icon, size: compact ? 14 : 17),
    label: Text(label),
    style: OutlinedButton.styleFrom(
      foregroundColor: active ? _palette.accent : _palette.text,
      side: BorderSide(color: active ? _palette.accent : _palette.line),
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 6 : 12,
        vertical: compact ? 5 : 10,
      ),
      textStyle: TextStyle(fontSize: compact ? 11 : 14),
    ),
  );

  Future<void> _showDifficulty() async {
    final choice = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: _palette.panel,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Choose your pace',
                style: TextStyle(color: _palette.text, fontSize: 22),
              ),
              const SizedBox(height: 16),
              for (final level in ['easy', 'medium', 'hard', 'expert'])
                ListTile(
                  title: Text(
                    level[0].toUpperCase() + level.substring(1),
                    style: TextStyle(color: _palette.text),
                  ),
                  trailing: _difficulty == level
                      ? Icon(Icons.check_circle, color: _palette.accent)
                      : null,
                  onTap: () => Navigator.pop(context, level),
                ),
            ],
          ),
        ),
      ),
    );
    if (choice != null) {
      setState(() => _difficulty = choice);
      await _newGame();
    }
  }

  Future<void> _showSettings() async {
    final original = _palette;
    final originalRapid = _rapidEntry;
    var rapid = _rapidEntry;
    final confirmed = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, refresh) => AlertDialog(
          backgroundColor: _palette.panel,
          title: Text('Your space', style: TextStyle(color: _palette.text)),
          content: SizedBox(
            width: 520,
            height: MediaQuery.sizeOf(context).height * .55,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    activeThumbColor: _palette.accent,
                    title: Text(
                      'Quick entry',
                      style: TextStyle(color: _palette.text),
                    ),
                    subtitle: Text(
                      'Tap a number, then fill cells with one tap.',
                      style: TextStyle(color: _palette.muted),
                    ),
                    value: rapid,
                    onChanged: (value) {
                      rapid = value;
                      refresh(() {});
                      setState(() => _rapidEntry = value);
                    },
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'COLOR PALETTES',
                    style: TextStyle(
                      color: _palette.muted,
                      fontSize: 11,
                      letterSpacing: 1.8,
                    ),
                  ),
                  const SizedBox(height: 12),
                  GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: SudokuPalette.all.length,
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          childAspectRatio: 1.25,
                          crossAxisSpacing: 9,
                          mainAxisSpacing: 9,
                        ),
                    itemBuilder: (context, index) {
                      final palette = SudokuPalette.all[index];
                      final chosen = _palette.id == palette.id;
                      return InkWell(
                        onTap: () => setState(() {
                          _palette = palette;
                          refresh(() {});
                        }),
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          padding: const EdgeInsets.all(9),
                          decoration: BoxDecoration(
                            color: palette.panel,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: chosen ? palette.accent : palette.line,
                              width: chosen ? 2 : 1,
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  for (final swatch in [
                                    palette.background,
                                    palette.accent,
                                    palette.given,
                                    palette.entry,
                                  ])
                                    Container(
                                      width: 17,
                                      height: 17,
                                      margin: const EdgeInsets.only(right: 5),
                                      decoration: BoxDecoration(
                                        color: swatch,
                                        shape: BoxShape.circle,
                                        border: Border.all(color: palette.line),
                                      ),
                                    ),
                                ],
                              ),
                              const Spacer(),
                              Container(
                                height: 24,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 5,
                                ),
                                decoration: BoxDecoration(
                                  color: palette.panelRaised,
                                  borderRadius: BorderRadius.circular(5),
                                ),
                                child: Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceAround,
                                  children: [
                                    for (final value in ['1', '5', '9'])
                                      Text(
                                        value,
                                        style: TextStyle(
                                          color: palette.given,
                                          fontSize: 11,
                                          fontWeight: FontWeight.w800,
                                        ),
                                      ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 5),
                              Text(
                                palette.name,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  color: palette.text,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () {
                setState(() {
                  _palette = original;
                  _rapidEntry = originalRapid;
                });
                Navigator.pop(dialogContext, false);
              },
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(dialogContext, true),
              child: const Text('Keep changes'),
            ),
          ],
        ),
      ),
    );
    if (confirmed == true) {
      await _save();
    } else {
      setState(() {
        _palette = original;
        _rapidEntry = originalRapid;
      });
    }
  }
}
