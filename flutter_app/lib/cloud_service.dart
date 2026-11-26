import 'dart:async';
import 'dart:convert';

import 'package:cloud_functions/cloud_functions.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';

/// Optional Firebase account, synchronization, and competition services.
class CloudService {
  CloudService._();

  static final CloudService instance = CloudService._();
  static const _apiKey = String.fromEnvironment('FIREBASE_API_KEY');
  static const _projectId = String.fromEnvironment('FIREBASE_PROJECT_ID');
  static const _messagingSenderId = String.fromEnvironment(
    'FIREBASE_MESSAGING_SENDER_ID',
  );
  static const _authDomain = String.fromEnvironment('FIREBASE_AUTH_DOMAIN');
  static const _webAppId = String.fromEnvironment('FIREBASE_WEB_APP_ID');
  static const _androidAppId = String.fromEnvironment(
    'FIREBASE_ANDROID_APP_ID',
  );
  static const _iosAppId = String.fromEnvironment('FIREBASE_IOS_APP_ID');

  final _authChanges = StreamController<User?>.broadcast();
  FirebaseAuth? _auth;
  FirebaseFunctions? _functions;
  StreamSubscription<User?>? _authSubscription;
  Timer? _syncTimer;
  Map<String, dynamic>? _pendingGame;
  String? _pendingSignature;
  DateTime _lastSync = DateTime.fromMillisecondsSinceEpoch(0);
  String? _lastSyncSignature;
  bool _ready = false;
  String? _setupError;

  bool get configured =>
      _apiKey.isNotEmpty &&
      _projectId.isNotEmpty &&
      _messagingSenderId.isNotEmpty &&
      _appId.isNotEmpty &&
      (!kIsWeb || _authDomain.isNotEmpty);

  bool get ready => _ready;
  String? get setupError => _setupError;
  User? get currentUser => _auth?.currentUser;
  Stream<User?> get authChanges => _authChanges.stream;

  String get _appId {
    if (kIsWeb) return _webAppId;
    return switch (defaultTargetPlatform) {
      TargetPlatform.android => _androidAppId,
      TargetPlatform.iOS => _iosAppId,
      _ => '',
    };
  }

  Future<void> initialize() async {
    if (!configured) return;
    try {
      final options = FirebaseOptions(
        apiKey: _apiKey,
        appId: _appId,
        messagingSenderId: _messagingSenderId,
        projectId: _projectId,
        authDomain: kIsWeb ? _authDomain : null,
      );
      await Firebase.initializeApp(options: options);
      _auth = FirebaseAuth.instance;
      _functions = FirebaseFunctions.instanceFor(region: 'asia-east1');
      _ready = true;
      _authSubscription = _auth!.authStateChanges().listen(_authChanges.add);
      _authChanges.add(_auth!.currentUser);
    } catch (error) {
      _setupError = error.toString();
    }
  }

  Future<UserCredential> register(
    String email,
    String password,
    String displayName,
  ) async {
    final normalizedName = displayName.trim();
    if (normalizedName.length < 3) {
      throw ArgumentError('Display name must be at least 3 characters.');
    }
    final credential = await _auth!.createUserWithEmailAndPassword(
      email: email,
      password: password,
    );
    await _call('updateProfile', {'displayName': normalizedName});
    return credential;
  }

  Future<UserCredential> signIn(String email, String password) =>
      _auth!.signInWithEmailAndPassword(email: email, password: password);

  Future<UserCredential> signInWithGoogle() async {
    final provider = GoogleAuthProvider();
    if (kIsWeb) return _auth!.signInWithPopup(provider);
    return _auth!.signInWithProvider(provider);
  }

  Future<void> signOut() => _auth!.signOut();

  Future<Map<String, dynamic>> _call(
    String name, [
    Map<String, dynamic> data = const {},
  ]) async {
    final result = await _functions!.httpsCallable(name).call<Object?>(data);
    return Map<String, dynamic>.from(result.data! as Map);
  }

  Future<Map<String, dynamic>> getDailyChallenge() =>
      _call('getDailyChallenge');

  Future<Map<String, dynamic>> submitDailyRun({
    required String date,
    required List<List<int>> grid,
    required int elapsedSeconds,
    required int hintsUsed,
    required bool usedSolve,
  }) => _call('submitDailyRun', {
    'date': date,
    'grid': grid,
    'elapsedSeconds': elapsedSeconds,
    'hintsUsed': hintsUsed,
    'usedSolve': usedSolve,
  });

  Future<Map<String, dynamic>> getLeaderboard() => _call('getDailyLeaderboard');

  Future<Map<String, dynamic>> recordDailyHint(String date) =>
      _call('recordDailyHint', {'date': date});

  Future<void> recordDailySolutionReveal(String date) async {
    await _call('recordDailySolutionReveal', {'date': date});
  }

  Future<Map<String, dynamic>> getProfile() => _call('getProfile');

  Future<Map<String, dynamic>?> getSavedGame() async {
    final response = await _call('getSavedGame');
    final game = response['game'];
    return game is Map ? Map<String, dynamic>.from(game) : null;
  }

  void scheduleGameSync(Map<String, dynamic> game) {
    if (!_ready || currentUser == null) return;
    final comparable = Map<String, dynamic>.of(game)
      ..remove('seconds')
      ..remove('savedAt');
    final signature = jsonEncode(comparable);
    if (signature == _lastSyncSignature) return;
    _pendingGame = game;
    _pendingSignature = signature;
    if (_syncTimer != null) return;
    final remaining =
        const Duration(seconds: 30) - DateTime.now().difference(_lastSync);
    final delay = remaining.isNegative || remaining < const Duration(seconds: 1)
        ? const Duration(seconds: 1)
        : remaining;
    _syncTimer = Timer(delay, () async {
      _syncTimer = null;
      final pending = _pendingGame;
      final pendingSignature = _pendingSignature;
      _pendingGame = null;
      _pendingSignature = null;
      if (pending == null || currentUser == null) return;
      try {
        await _call('syncSavedGame', {'game': pending});
        _lastSync = DateTime.now();
        _lastSyncSignature = pendingSignature;
      } catch (_) {
        // Local saves remain available if the device is offline.
      }
    });
  }

  Future<void> dispose() async {
    _syncTimer?.cancel();
    await _authSubscription?.cancel();
    await _authChanges.close();
  }
}
