'use strict';

const messages = {
  en: {
    pageTitle: 'Sudoku — A little clarity', description: 'A quiet, beautifully crafted Sudoku for a clearer mind.',
    home: 'Sudoku home', switchLanguage: 'Switch language', openSettings: 'Open settings', difficulty: 'Difficulty', numberColors: 'Number colors', board: 'Sudoku board',
    numberPad: 'Choose a number to place', timer: 'Elapsed time', closeSettings: 'Close settings',
    closeAccount: 'Close account', closeLeaderboard: 'Close leaderboard', previewBoard: 'Sample Sudoku board',
    leaderboardSignIn: 'Sign in to see today’s fastest solves.',
    cellPosition: 'Row {row}, column {column}', chooseNumber: 'Choose {n}',
    notesOn: 'Pencil notes on.', notesOff: 'Pencil notes off.', saveError: 'Could not save this game on this device.',
    rankedSaved: 'Ranked time saved · {time} including hint penalties.', fasterAlready: 'You already have a faster ranked time for today.',
    rankingSaveError: 'Solved locally; ranking could not be saved: {error}', solveMode: 'Solve', challengeMode: 'Challenge', signIn: 'Sign in',
    ritual: 'DAILY RITUAL · NO RUSH', solveTitle: 'A little<br><em>clarity.</em>',
    solveDescription: 'One quiet square at a time.', dailyChallenge: 'DAILY CHALLENGE',
    challengeTitle: 'A shared<br><em>moment.</em>', challengeDescription: 'One puzzle for everyone. Solve it, then see where you rank.',
    startChallenge: 'Start today’s challenge', leaderboard: 'Leaderboard',
    challengeLoginNote: 'Sign in to start today’s challenge and submit a ranked time.',
    easy: 'Easy', medium: 'Medium', hard: 'Hard', expert: 'Expert', newPuzzle: 'New puzzle',
    puzzle: 'PUZZLE', yours: 'YOURS', undo: 'Undo', notes: 'Notes', hint: 'Hint', erase: 'Erase', solve: 'Solve',
    revealTitle: 'Reveal the complete solution', footerMotto: 'MADE FOR A MOMENT OF CALM',
    footerKeys: 'ARROWS · 1–9 FILL · N NOTES · S SOLVES', settings: 'MAKE IT YOURS',
    settingsTitle: 'Your little corner.', palettes: 'Choose a palette · 20 colors', livePreview: 'Live preview',
    quickPlace: 'Quick place', quickPlaceHelp: 'Choose a number, then tap multiple squares to place it.',
    cancel: 'Cancel', confirm: 'Confirm', settingsCaption: 'Preview applies immediately. Cancel restores your saved palette.',
    accountEyebrow: 'YOUR SUDOKU JOURNEY', welcome: 'Welcome back', google: 'Continue with Google', orEmail: 'or email',
    displayName: 'Display name', email: 'Email', password: 'Password', createAccount: 'Create an account',
    cloudFootnote: 'Your puzzles and rankings sync across devices. Guest games stay on this device.',
    leaderboardEyebrow: 'TODAY’S CHALLENGE', leaderboardTitle: 'Daily leaderboard',
    leaderboardFootnote: 'Times include a two-minute penalty for each hint. Revealed solutions are not ranked.',
    signedInAs: 'Signed in as', playingGuest: 'Playing as guest',
    cloudSetupNeeded: 'Guest mode · Firebase setup needed for online play',
    firebaseConfigNeeded: 'Add Firebase settings in web/firebase-config.js to enable online accounts.',
    connecting: 'Connecting securely…', cloudUpToDate: 'Cloud save up to date',
    syncUnavailable: 'Cloud sync unavailable: {error}', cloudSaveFailed: 'Cloud save failed: {error}',
    firebaseSetupError: 'Firebase setup error: {error}', leaderboardLogin: 'Sign in to view the daily rankings.',
    leaderboardLoading: 'Loading today’s rankings…', leaderboardDescription: 'Daily board · {date} · best time plus 2 minutes per hint',
    leaderboardEmpty: 'No ranked runs yet. Be the first.', createYourAccount: 'Create your account',
    haveAccount: 'I already have an account', signOut: 'Sign out',
    quickArmed: 'Tap squares to place {n} · press Esc to clear.',
    quickHelp: 'Quick place: choose a number, then tap the squares to fill.', selectThenNumber: 'Select a square, then choose a number to place it.',
    filled: '{n} / 81 filled', fresh: 'A fresh page. Take your time.', conflict: 'That number conflicts with this row, column, or box.',
    complete: 'Beautifully done. You made space for clarity.', completeToast: 'Puzzle complete · beautifully done',
    nextStep: 'A good next step.', undone: 'Last move undone.', alreadySolved: 'This puzzle is already solved.',
    solutionRevealError: 'Could not record the solution reveal: {error}', solvedUndo: 'Solved. Use Undo to restore your board.',
    revealToast: 'Solution revealed', hintConnect: 'Connect to keep daily hints ranked: {error}',
    nudge: 'A little nudge, right where you needed it.', dailyLoadError: 'The daily puzzle could not be loaded.',
    dailyStatus: 'Today’s shared puzzle. Make your place on the board.', settingsSaved: 'Settings saved.',
    cloudReady: 'Your latest cloud game is ready.', dailyLabel: 'DAILY CHALLENGE · {date}', ritualLabel: 'DAILY RITUAL · NO RUSH',
    loginRanking: 'Sign in to submit a ranked time. You can preview the challenge as a guest.',
  },
  zh: {
    pageTitle: '數獨 — 留一點清晰', description: '一款精心打造的靜心數獨。',
    home: '數獨首頁', switchLanguage: '切換語言', openSettings: '開啟設定', difficulty: '難度', numberColors: '數字顏色說明', board: '數獨棋盤',
    numberPad: '選擇要填入的數字', timer: '經過時間', closeSettings: '關閉設定',
    closeAccount: '關閉帳號視窗', closeLeaderboard: '關閉排行榜', previewBoard: '數獨配色示意圖',
    leaderboardSignIn: '登入查看今日最快解題成績。',
    cellPosition: '第 {row} 列，第 {column} 欄', chooseNumber: '選擇 {n}',
    notesOn: '筆記模式已開啟。', notesOff: '筆記模式已關閉。', saveError: '無法將進度儲存在這部裝置。',
    rankedSaved: '排名已儲存 · {time}（含提示加罰）', fasterAlready: '你今天已有更快的排名紀錄。',
    rankingSaveError: '本機解題完成，但排名儲存失敗：{error}', solveMode: '解題', challengeMode: '挑戰', signIn: '登入',
    ritual: '每日靜心 · 慢慢來', solveTitle: '留一點<br><em>清晰。</em>',
    solveDescription: '一次，安靜地填好一格。', dailyChallenge: '每日挑戰',
    challengeTitle: '一起完成<br><em>今天。</em>', challengeDescription: '所有人挑戰同一題。解完看看你的排名。',
    startChallenge: '開始今日挑戰', leaderboard: '排行榜',
    challengeLoginNote: '登入後即可開始今日挑戰並提交排名。',
    easy: '簡單', medium: '中等', hard: '困難', expert: '專家', newPuzzle: '新題目',
    puzzle: '題目', yours: '填入', undo: '復原', notes: '筆記', hint: '提示', erase: '清除', solve: '解題',
    revealTitle: '顯示完整答案', footerMotto: '留一段安靜的時光',
    footerKeys: '方向鍵 · 1–9 填數字 · N 筆記 · S 顯示答案', settings: '打造你的風格',
    settingsTitle: '專屬於你的一角。', palettes: '選擇配色 · 共 20 種', livePreview: '即時預覽',
    quickPlace: '快速填數', quickPlaceHelp: '先選數字，再點選多個格子快速填入。',
    cancel: '取消', confirm: '確認', settingsCaption: '配色會立即預覽；取消即可還原。',
    accountEyebrow: '你的數獨旅程', welcome: '歡迎回來', google: '使用 Google 繼續', orEmail: '或使用電子郵件',
    displayName: '顯示名稱', email: '電子郵件', password: '密碼', createAccount: '建立帳號',
    cloudFootnote: '題目進度與排名會在裝置間同步；訪客紀錄只保存在本機。',
    leaderboardEyebrow: '今日挑戰', leaderboardTitle: '每日排行榜',
    leaderboardFootnote: '每次提示加罰兩分鐘；使用完整解答不列入排名。',
    signedInAs: '已登入：', playingGuest: '訪客遊玩',
    cloudSetupNeeded: '訪客模式 · 設定 Firebase 後即可使用線上功能',
    firebaseConfigNeeded: '請在 web/firebase-config.js 填入 Firebase 設定以啟用線上帳號。',
    connecting: '安全連線中…', cloudUpToDate: '雲端進度已同步',
    syncUnavailable: '雲端同步暫不可用：{error}', cloudSaveFailed: '雲端儲存失敗：{error}',
    firebaseSetupError: 'Firebase 設定錯誤：{error}', leaderboardLogin: '登入後即可查看每日排名。',
    leaderboardLoading: '正在載入今日排名…', leaderboardDescription: '每日排行榜 · {date} · 每次提示加罰兩分鐘',
    leaderboardEmpty: '目前還沒有人完成排名，來當第一位吧。', createYourAccount: '建立你的帳號',
    haveAccount: '我已經有帳號', signOut: '登出',
    quickArmed: '點選格子填入 {n} · 按 Esc 取消。',
    quickHelp: '快速填數：選擇數字，再點選要填入的格子。', selectThenNumber: '先選格子，再選擇要填入的數字。',
    filled: '已填 {n} / 81 格', fresh: '新的一局，慢慢來。', conflict: '這個數字與所在列、行或宮格重複。',
    complete: '完成得真好，留住這份清晰。', completeToast: '挑戰完成 · 做得真好',
    nextStep: '一步一步來。', undone: '已復原上一步。', alreadySolved: '這題已經解完了。',
    solutionRevealError: '無法記錄顯示答案：{error}', solvedUndo: '已解題。按「復原」可回到原本進度。',
    revealToast: '已顯示答案', hintConnect: '連線後才能保留挑戰排名提示：{error}',
    nudge: '給你一點剛剛好的提示。', dailyLoadError: '載入今日題目失敗。',
    dailyStatus: '今天的共同題目，開始留下你的紀錄吧。', settingsSaved: '設定已儲存。',
    cloudReady: '已載入最新雲端進度。', dailyLabel: '每日挑戰 · {date}', ritualLabel: '每日靜心 · 慢慢來',
    loginRanking: '登入後可提交排名；訪客也能先看看今日題目。',
  },
};
let language = localStorage.getItem('still-sudoku-language') || (navigator.language?.toLowerCase().startsWith('zh') ? 'zh' : 'en');
function t(key, values = {}) {
  let message = messages[language][key] || messages.en[key] || key;
  for (const [name, value] of Object.entries(values)) message = message.replaceAll(`{${name}}`, String(value));
  return message;
}
function applyLanguage() {
  document.documentElement.lang = language === 'zh' ? 'zh-Hant' : 'en';
  document.title = t('pageTitle');
  document.querySelector('meta[name="description"]')?.setAttribute('content', t('description'));
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    element.innerHTML = t(element.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-title]').forEach((element) => {
    element.title = t(element.dataset.i18nTitle);
  });
  document.querySelectorAll('[data-i18n-aria-label]').forEach((element) => {
    element.setAttribute('aria-label', t(element.dataset.i18nAriaLabel));
  });
  document.querySelectorAll('[data-i18n-aria]').forEach((element) => {
    element.setAttribute('aria-label', t(element.dataset.i18nAria));
  });
  const button = document.querySelector('#language-button');
  if (button) { button.textContent = language === 'zh' ? 'EN' : '中'; button.title = language === 'zh' ? 'Switch to English' : '切換為繁體中文'; }
  window.dispatchEvent(new CustomEvent('sudoku:language-change', {detail: language}));
}
window.t = t;
window.getSudokuLanguage = () => language;
window.setSudokuLanguage = (value) => {
  language = value === 'zh' ? 'zh' : 'en';
  localStorage.setItem('still-sudoku-language', language);
  applyLanguage();
};
document.querySelector('#language-button')?.addEventListener('click', () => window.setSudokuLanguage(language === 'zh' ? 'en' : 'zh'));
applyLanguage();
