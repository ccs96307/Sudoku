'use strict';

const {initializeApp} = require('firebase-admin/app');
const {FieldValue, getFirestore} = require('firebase-admin/firestore');
const {HttpsError, onCall} = require('firebase-functions/v2/https');
const {countSolutions, hasGridShape, isValidGrid, makeDailyPuzzle} = require('./sudoku');

initializeApp();
const db = getFirestore();
const REGION = 'asia-east1';
const LIMITS = {maxInstances: 10, memory: '256MiB', region: REGION, timeoutSeconds: 30};

function requireUser(request) {
  if (!request.auth) throw new HttpsError('unauthenticated', 'Sign in to use cloud features.');
  return request.auth.uid;
}

function taipeiDate(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    day: '2-digit', month: '2-digit', timeZone: 'Asia/Taipei', year: 'numeric',
  }).formatToParts(now);
  const fields = Object.fromEntries(parts.map(({type, value}) => [type, value]));
  return `${fields.year}-${fields.month}-${fields.day}`;
}

function validDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value;
}

function cleanName(value, fallback) {
  const name = typeof value === 'string' ? value.trim().replace(/[<>\u0000-\u001f]/g, '') : '';
  return (name || fallback || 'Still Player').slice(0, 24);
}

function validSavedGame(game) {
  if (!game || typeof game !== 'object' || Buffer.byteLength(JSON.stringify(game)) > 18000) return false;
  const {grid, givens, solution} = game;
  if (!hasGridShape(grid) || !hasGridShape(givens) || !hasGridShape(solution) ||
      !isValidGrid(givens) || !isValidGrid(solution) || countSolutions(givens) !== 1 ||
      solution.some((row) => row.includes(0))) return false;
  for (let row = 0; row < 9; row++) {
    for (let column = 0; column < 9; column++) {
      if (givens[row][column] && givens[row][column] !== solution[row][column]) return false;
    }
  }
  return true;
}

exports.getDailyChallenge = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const date = taipeiDate();
  const publicRef = db.doc(`dailyChallenges/${date}`);
  const privateRef = db.doc(`dailyChallengeSolutions/${date}`);
  const current = await publicRef.get();
  if (!current.exists) {
    const generated = makeDailyPuzzle(date);
    await db.runTransaction(async (transaction) => {
      const existing = await transaction.get(publicRef);
      if (existing.exists) return;
      transaction.create(publicRef, {
        date,
        difficulty: generated.difficulty,
        clueCount: generated.clueCount,
        puzzle: generated.puzzle,
        createdAt: FieldValue.serverTimestamp(),
      });
      transaction.create(privateRef, {solution: generated.solution});
    });
  }
  const challenge = await publicRef.get();
  if (!challenge.exists) throw new HttpsError('internal', 'Daily puzzle could not be created.');
  const runRef = privateRef.collection('sessions').doc(uid);
  await db.runTransaction(async (transaction) => {
    const run = await transaction.get(runRef);
    if (!run.exists) {
      transaction.create(runRef, {
        startedAt: FieldValue.serverTimestamp(),
        hintsUsed: 0,
        usedSolve: false,
      });
    }
  });
  const profile = await db.doc(`profiles/${uid}`).get();
  const data = challenge.data();
  return {
    date: data.date,
    difficulty: data.difficulty,
    clueCount: data.clueCount,
    puzzle: data.puzzle,
    displayName: profile.data()?.displayName || 'Still Player',
  };
});

exports.recordDailyHint = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const {date = taipeiDate()} = request.data || {};
  if (!validDate(date) || date > taipeiDate()) throw new HttpsError('invalid-argument', 'Invalid challenge date.');
  const runRef = db.doc(`dailyChallengeSolutions/${date}/sessions/${uid}`);
  const count = await db.runTransaction(async (transaction) => {
    const run = await transaction.get(runRef);
    if (!run.exists) throw new HttpsError('failed-precondition', 'Start the daily challenge first.');
    if (run.get('usedSolve') === true) throw new HttpsError('failed-precondition', 'This run is not ranked.');
    const hintsUsed = (run.get('hintsUsed') || 0) + 1;
    if (hintsUsed > 81) throw new HttpsError('resource-exhausted', 'No more hints are available.');
    transaction.update(runRef, {hintsUsed});
    return hintsUsed;
  });
  return {hintsUsed: count};
});

exports.recordDailySolutionReveal = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const {date = taipeiDate()} = request.data || {};
  if (!validDate(date) || date > taipeiDate()) throw new HttpsError('invalid-argument', 'Invalid challenge date.');
  const runRef = db.doc(`dailyChallengeSolutions/${date}/sessions/${uid}`);
  await db.runTransaction(async (transaction) => {
    const run = await transaction.get(runRef);
    if (!run.exists) throw new HttpsError('failed-precondition', 'Start the daily challenge first.');
    transaction.update(runRef, {usedSolve: true});
  });
  return {ranked: false};
});

exports.submitDailyRun = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const {date, grid, elapsedSeconds, displayName} = request.data || {};
  if (!validDate(date) || date > taipeiDate()) throw new HttpsError('invalid-argument', 'Invalid challenge date.');
  if (!Number.isInteger(elapsedSeconds) || elapsedSeconds < 0 || elapsedSeconds > 86400) {
    throw new HttpsError('invalid-argument', 'Completion time is outside the allowed range.');
  }
  if (!hasGridShape(grid) || !isValidGrid(grid) || grid.some((row) => row.includes(0))) {
    throw new HttpsError('invalid-argument', 'The submitted board is incomplete or invalid.');
  }
  const solutionSnapshot = await db.doc(`dailyChallengeSolutions/${date}`).get();
  if (!solutionSnapshot.exists) throw new HttpsError('not-found', 'Daily challenge was not found.');
  const solution = solutionSnapshot.get('solution');
  if (JSON.stringify(grid) !== JSON.stringify(solution)) {
    throw new HttpsError('failed-precondition', 'The submitted board does not solve this challenge.');
  }

  const profileRef = db.doc(`profiles/${uid}`);
  const entryRef = db.doc(`dailyLeaderboards/${date}/entries/${uid}`);
  const runRef = db.doc(`dailyChallengeSolutions/${date}/sessions/${uid}`);
  const profileSnapshot = await profileRef.get();
  const profileName = profileSnapshot.data()?.displayName;
  const name = cleanName(displayName, profileName || 'Still Player');
  const result = await db.runTransaction(async (transaction) => {
    const run = await transaction.get(runRef);
    const previous = await transaction.get(entryRef);
    if (!run.exists) throw new HttpsError('failed-precondition', 'Start the daily challenge first.');
    if (run.get('usedSolve') === true) throw new HttpsError('failed-precondition', 'Solution reveal runs are not ranked.');
    const startedAt = run.get('startedAt')?.toMillis();
    const serverElapsed = Math.floor((Date.now() - startedAt) / 1000);
    if (!Number.isFinite(serverElapsed) || serverElapsed < 20 || serverElapsed > 86400) {
      throw new HttpsError('failed-precondition', 'The daily run duration is outside the ranked window.');
    }
    const hintsUsed = run.get('hintsUsed') || 0;
    const score = serverElapsed + hintsUsed * 120;
    if (previous.exists && previous.get('score') <= score) {
      return {
        improved: false,
        score: previous.get('score'),
        previousTime: previous.get('elapsedSeconds'),
        hintsUsed: previous.get('hintsUsed'),
      };
    }
    transaction.set(entryRef, {
      uid,
      displayName: name,
      elapsedSeconds: serverElapsed,
      hintsUsed,
      score,
      completedAt: FieldValue.serverTimestamp(),
    });
    return {
      improved: true,
      score,
      elapsedSeconds: serverElapsed,
      hintsUsed,
      previousTime: previous.data()?.elapsedSeconds || null,
    };
  });
  return result;
});

exports.getDailyLeaderboard = onCall(LIMITS, async (request) => {
  requireUser(request);
  const {date = taipeiDate(), limit = 50} = request.data || {};
  if (!validDate(date) || date > taipeiDate()) throw new HttpsError('invalid-argument', 'Invalid challenge date.');
  const safeLimit = Math.max(1, Math.min(Number.isInteger(limit) ? limit : 50, 100));
  const snapshot = await db.collection(`dailyLeaderboards/${date}/entries`)
    .orderBy('score', 'asc').orderBy('completedAt', 'asc').limit(safeLimit).get();
  return {
    date,
    entries: snapshot.docs.map((doc, index) => ({
      rank: index + 1,
      displayName: doc.get('displayName'),
      elapsedSeconds: doc.get('elapsedSeconds'),
      hintsUsed: doc.get('hintsUsed'),
      score: doc.get('score'),
    })),
  };
});

exports.getProfile = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const ref = db.doc(`profiles/${uid}`);
  const snapshot = await ref.get();
  if (snapshot.exists) return {displayName: snapshot.get('displayName')};
  const displayName = cleanName(request.auth.token.name, `Player ${uid.slice(0, 6)}`);
  const profile = {displayName, createdAt: FieldValue.serverTimestamp()};
  await ref.set(profile, {merge: true});
  return {displayName};
});

exports.updateProfile = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const displayName = cleanName(request.data?.displayName, '');
  if (displayName.length < 3) throw new HttpsError('invalid-argument', 'Display name must be at least 3 characters.');
  await db.doc(`profiles/${uid}`).set({displayName, updatedAt: FieldValue.serverTimestamp()}, {merge: true});
  return {displayName};
});

exports.getSavedGame = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const snapshot = await db.doc(`userGames/${uid}`).get();
  return snapshot.exists ? {game: snapshot.get('game'), updatedAt: snapshot.get('updatedAt')?.toDate().toISOString()} : {game: null};
});

exports.syncSavedGame = onCall(LIMITS, async (request) => {
  const uid = requireUser(request);
  const game = request.data?.game;
  if (!validSavedGame(game)) throw new HttpsError('invalid-argument', 'Saved game data is invalid.');
  await db.doc(`userGames/${uid}`).set({game, updatedAt: FieldValue.serverTimestamp()});
  return {synced: true};
});
