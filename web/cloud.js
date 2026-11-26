'use strict';

const config = window.STILL_SUDOKU_FIREBASE_CONFIG || {};
const requiredConfig = ['apiKey', 'authDomain', 'projectId', 'appId'];
const configured = requiredConfig.every((key) => typeof config[key] === 'string' && config[key].length > 0);
let auth;
let functions;
let currentUser = null;
let syncTimer;
let pendingGame;
let pendingSignature;
let lastSyncSignature;
let lastSyncAt = 0;
let authApi;
let callable;
let accountMode = 'signin';

const accountDialog = document.querySelector('#account-dialog');
const accountStatus = document.querySelector('#account-status');
const accountButton = document.querySelector('#account-button');
const cloudStatus = document.querySelector('#cloud-status');
const leaderboardDialog = document.querySelector('#leaderboard-dialog');

function announceAuth(user) {
  currentUser = user;
  if (accountButton) accountButton.textContent = user ? `Hi, ${user.displayName || user.email?.split('@')[0] || 'Player'}` : 'Sign in';
  if (cloudStatus) cloudStatus.textContent = user ? `Signed in as ${user.displayName || user.email}` : (configured ? 'Playing as guest' : 'Cloud features need Firebase setup');
  window.dispatchEvent(new CustomEvent('sudoku:auth-change', {detail: {user: user ? {uid: user.uid, displayName: user.displayName, email: user.email} : null}}));
}

function setAccountMode(mode) {
  accountMode = mode;
  const register = mode === 'register';
  document.querySelector('#account-title').textContent = register ? 'Create your account' : 'Welcome back';
  document.querySelector('#account-submit').textContent = register ? 'Create account' : 'Sign in';
  document.querySelector('#account-mode-toggle').textContent = register ? 'I already have an account' : 'Create an account';
  document.querySelector('#display-name-field').hidden = !register;
  document.querySelector('#account-display-name').required = register;
}

async function initialize() {
  if (!configured) {
    accountButton?.addEventListener('click', () => {
      accountStatus.textContent = 'Add your Firebase web app settings to web/firebase-config.js to enable cloud accounts.';
      document.querySelector('#account-login-fields').hidden = true;
      accountDialog.showModal();
    });
    if (cloudStatus) cloudStatus.textContent = 'Guest mode · Firebase setup needed for online play';
    window.SudokuCloud = {configured: false, signedIn: () => false};
    return;
  }
  try {
    const version = '11.10.0';
    const [appApi, authModule, functionsModule] = await Promise.all([
      import(`https://www.gstatic.com/firebasejs/${version}/firebase-app.js`),
      import(`https://www.gstatic.com/firebasejs/${version}/firebase-auth.js`),
      import(`https://www.gstatic.com/firebasejs/${version}/firebase-functions.js`),
    ]);
    const app = appApi.initializeApp(config);
    authApi = authModule;
    auth = authApi.getAuth(app);
    functions = functionsModule.getFunctions(app, 'asia-east1');
    callable = (name, data = {}) => functionsModule.httpsCallable(functions, name)(data).then((result) => result.data);
    authApi.onAuthStateChanged(auth, async (user) => {
      announceAuth(user);
      if (user) {
        try {
          const [profile, saved] = await Promise.all([callable('getProfile'), callable('getSavedGame')]);
          if (profile?.displayName && !user.displayName) await authApi.updateProfile(user, {displayName: profile.displayName});
          if (saved?.game) window.dispatchEvent(new CustomEvent('sudoku:cloud-game', {detail: saved.game}));
          else window.dispatchEvent(new CustomEvent('sudoku:cloud-empty'));
        } catch (error) {
          if (cloudStatus) cloudStatus.textContent = `Cloud sync unavailable: ${error.message}`;
        }
      }
    });
    window.SudokuCloud = {
      configured: true,
      signedIn: () => Boolean(currentUser),
      user: () => currentUser,
      signIn: (email, password) => authApi.signInWithEmailAndPassword(auth, email, password),
      register: async (email, password, displayName) => {
        const result = await authApi.createUserWithEmailAndPassword(auth, email, password);
        await authApi.updateProfile(result.user, {displayName});
        await callable('updateProfile', {displayName});
        return result;
      },
      google: () => authApi.signInWithPopup(auth, new authApi.GoogleAuthProvider()),
      signOut: () => authApi.signOut(auth),
      dailyChallenge: () => callable('getDailyChallenge'),
      submitDaily: (result) => callable('submitDailyRun', result),
      recordDailyHint: (date) => callable('recordDailyHint', {date}),
      recordDailyReveal: (date) => callable('recordDailySolutionReveal', {date}),
      leaderboard: (date) => callable('getDailyLeaderboard', {date}),
      saveGame: (game) => {
        if (!currentUser) return;
        const comparable = {...game, dailyDate: game.dailyChallengeDate || null};
        delete comparable.dailyChallengeDate;
        delete comparable.seconds;
        delete comparable.savedAt;
        const signature = JSON.stringify(comparable);
        if (signature === lastSyncSignature) return;
        pendingGame = comparable;
        pendingSignature = signature;
        if (syncTimer) return;
        const delay = Math.max(1000, 30000 - (Date.now() - lastSyncAt));
        syncTimer = setTimeout(async () => {
          syncTimer = null;
          const gameToSave = pendingGame;
          const signatureToSave = pendingSignature;
          pendingGame = null;
          pendingSignature = null;
          if (!currentUser || !gameToSave) return;
          try {
            await callable('syncSavedGame', {game: gameToSave});
            lastSyncAt = Date.now();
            lastSyncSignature = signatureToSave;
            if (cloudStatus) cloudStatus.textContent = 'Cloud save up to date';
          } catch (error) {
            if (cloudStatus) cloudStatus.textContent = `Cloud save failed: ${error.message}`;
          }
        }, delay);
      },
    };
    if (cloudStatus) cloudStatus.textContent = currentUser ? `Signed in as ${currentUser.displayName || currentUser.email}` : 'Firebase connected · playing as guest';
    accountButton?.addEventListener('click', () => {
      document.querySelector('#account-login-fields').hidden = Boolean(currentUser);
      if (currentUser) {
        accountStatus.textContent = `Signed in as ${currentUser.displayName || currentUser.email}.`;
        document.querySelector('#account-signout').hidden = false;
      } else {
        accountStatus.textContent = '';
        document.querySelector('#account-signout').hidden = true;
      }
      accountDialog.showModal();
    });
  } catch (error) {
    if (cloudStatus) cloudStatus.textContent = `Firebase setup error: ${error.message}`;
    window.SudokuCloud = {configured: false, signedIn: () => false};
  }
}

accountDialog?.querySelector('#account-mode-toggle').addEventListener('click', () => {
  setAccountMode(accountMode === 'signin' ? 'register' : 'signin');
});
accountDialog?.querySelector('#account-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!window.SudokuCloud?.configured) return;
  const email = document.querySelector('#account-email').value.trim();
  const password = document.querySelector('#account-password').value;
  const displayName = document.querySelector('#account-display-name').value.trim();
  const button = document.querySelector('#account-submit');
  button.disabled = true;
  accountStatus.textContent = 'Connecting securely…';
  try {
    if (accountMode === 'register') await window.SudokuCloud.register(email, password, displayName);
    else await window.SudokuCloud.signIn(email, password);
    accountDialog.close();
  } catch (error) {
    accountStatus.textContent = error.message.replace('Firebase: ', '');
  } finally {
    button.disabled = false;
  }
});
document.querySelector('#google-signin')?.addEventListener('click', async () => {
  try {
    await window.SudokuCloud.google();
    accountDialog.close();
  } catch (error) {
    accountStatus.textContent = error.message.replace('Firebase: ', '');
  }
});
document.querySelector('#account-signout')?.addEventListener('click', async () => {
  await window.SudokuCloud?.signOut();
  accountDialog.close();
});
document.querySelector('#daily-challenge')?.addEventListener('click', async () => {
  if (!window.SudokuCloud?.configured) {
    accountStatus.textContent = 'Connect Firebase and sign in to join the shared daily challenge.';
    accountDialog.showModal();
    return;
  }
  if (!window.SudokuCloud.signedIn()) {
    accountStatus.textContent = 'Sign in to play the shared daily challenge and appear on its leaderboard.';
    accountDialog.showModal();
    return;
  }
  const button = document.querySelector('#daily-challenge');
  button.disabled = true;
  try {
    const challenge = await window.SudokuCloud.dailyChallenge();
    window.dispatchEvent(new CustomEvent('sudoku:daily-start', {detail: challenge}));
  } catch (error) {
    accountStatus.textContent = error.message;
    accountDialog.showModal();
  } finally {
    button.disabled = false;
  }
});
document.querySelector('#leaderboard-button')?.addEventListener('click', async () => {
  const list = document.querySelector('#leaderboard-list');
  list.replaceChildren();
  if (!window.SudokuCloud?.configured || !window.SudokuCloud.signedIn()) {
    document.querySelector('#leaderboard-note').textContent = 'Sign in to view the daily rankings.';
    leaderboardDialog.showModal();
    return;
  }
  document.querySelector('#leaderboard-note').textContent = 'Loading today’s rankings…';
  leaderboardDialog.showModal();
  try {
    const data = await window.SudokuCloud.leaderboard();
    document.querySelector('#leaderboard-note').textContent = `Daily board · ${data.date} · best time plus 2 minutes per hint`;
    for (const entry of data.entries) {
      const item = document.createElement('li');
      const name = document.createElement('span'); name.textContent = `${entry.rank}. ${entry.displayName}`;
      const score = document.createElement('strong'); score.textContent = `${Math.floor(entry.score / 60).toString().padStart(2, '0')}:${(entry.score % 60).toString().padStart(2, '0')}`;
      item.append(name, score); list.append(item);
    }
    if (!data.entries.length) document.querySelector('#leaderboard-note').textContent = 'No ranked runs yet. Be the first.';
  } catch (error) {
    document.querySelector('#leaderboard-note').textContent = error.message;
  }
});

initialize();
