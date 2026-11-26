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
const tr = (key, values) => window.t ? window.t(key, values) : key;

const accountDialog = document.querySelector('#account-dialog');
const accountStatus = document.querySelector('#account-status');
const accountButton = document.querySelector('#account-button');
const cloudStatus = document.querySelector('#cloud-status');
const leaderboardDialog = document.querySelector('#leaderboard-dialog');

function announceAuth(user) {
  currentUser = user;
  if (accountButton) accountButton.textContent = user ? `Hi, ${user.displayName || user.email?.split('@')[0] || 'Player'}` : tr('signIn');
  if (cloudStatus) cloudStatus.textContent = user ? `${tr('signedInAs')} ${user.displayName || user.email}` : (configured ? tr('playingGuest') : tr('cloudSetupNeeded'));
  window.dispatchEvent(new CustomEvent('sudoku:auth-change', {detail: {user: user ? {uid: user.uid, displayName: user.displayName, email: user.email} : null}}));
}

function setAccountMode(mode) {
  accountMode = mode;
  const register = mode === 'register';
  document.querySelector('#account-title').textContent = register ? tr('createYourAccount') : tr('welcome');
  document.querySelector('#account-submit').textContent = register ? tr('createAccount') : tr('signIn');
  document.querySelector('#account-mode-toggle').textContent = register ? tr('haveAccount') : tr('createAccount');
  document.querySelector('#display-name-field').hidden = !register;
  document.querySelector('#account-display-name').required = register;
}
window.addEventListener('sudoku:language-change', () => {
  if (accountDialog) setAccountMode(accountMode);
  if (window.SudokuCloud?.configured) announceAuth(currentUser);
  else if (cloudStatus) cloudStatus.textContent = tr('cloudSetupNeeded');
});

async function initialize() {
  if (!configured) {
    accountButton?.addEventListener('click', () => {
      accountStatus.textContent = tr('firebaseConfigNeeded');
      document.querySelector('#account-login-fields').hidden = true;
      accountDialog.showModal();
    });
    if (cloudStatus) cloudStatus.textContent = tr('cloudSetupNeeded');
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
          if (cloudStatus) cloudStatus.textContent = tr('syncUnavailable', {error: error.message});
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
            if (cloudStatus) cloudStatus.textContent = tr('cloudUpToDate');
          } catch (error) {
            if (cloudStatus) cloudStatus.textContent = tr('cloudSaveFailed', {error: error.message});
          }
        }, delay);
      },
    };
    if (cloudStatus) cloudStatus.textContent = currentUser ? `${tr('signedInAs')} ${currentUser.displayName || currentUser.email}` : tr('playingGuest');
    accountButton?.addEventListener('click', () => {
      document.querySelector('#account-login-fields').hidden = Boolean(currentUser);
      if (currentUser) {
        accountStatus.textContent = `${tr('signedInAs')} ${currentUser.displayName || currentUser.email}.`;
        document.querySelector('#account-signout').hidden = false;
      } else {
        accountStatus.textContent = '';
        document.querySelector('#account-signout').hidden = true;
      }
      accountDialog.showModal();
    });
  } catch (error) {
    if (cloudStatus) cloudStatus.textContent = tr('firebaseSetupError', {error: error.message});
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
  accountStatus.textContent = tr('connecting');
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
    accountStatus.textContent = tr('firebaseConfigNeeded');
    accountDialog.showModal();
    return;
  }
  if (!window.SudokuCloud.signedIn()) {
    accountStatus.textContent = tr('loginRanking');
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
    document.querySelector('#leaderboard-note').textContent = tr('leaderboardLogin');
    leaderboardDialog.showModal();
    return;
  }
  document.querySelector('#leaderboard-note').textContent = tr('leaderboardLoading');
  leaderboardDialog.showModal();
  try {
    const data = await window.SudokuCloud.leaderboard();
    document.querySelector('#leaderboard-note').textContent = tr('leaderboardDescription', {date: data.date});
    for (const entry of data.entries) {
      const item = document.createElement('li');
      const name = document.createElement('span'); name.textContent = `${entry.rank}. ${entry.displayName}`;
      const score = document.createElement('strong'); score.textContent = `${Math.floor(entry.score / 60).toString().padStart(2, '0')}:${(entry.score % 60).toString().padStart(2, '0')}`;
      item.append(name, score); list.append(item);
    }
    if (!data.entries.length) document.querySelector('#leaderboard-note').textContent = tr('leaderboardEmpty');
  } catch (error) {
    document.querySelector('#leaderboard-note').textContent = error.message;
  }
});

initialize();
