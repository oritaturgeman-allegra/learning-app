/**
 * english-game.js — English game logic functions.
 * Loaded after shared.js and english-data.js.
 * Expects globals: UNITS, SESSION_SLUG, SUBJECT, GAME_TYPE_MAP, REWARD_TIERS,
 *   state, API_BASE, and all shared.js functions.
 */

// Active subject and unit — set from URL route or defaults
const ACTIVE_UNIT = SESSION_SLUG && UNITS[SESSION_SLUG] ? UNITS[SESSION_SLUG] : UNITS['jet2-unit2'];
const vocabulary = ACTIVE_UNIT.vocabulary;
const scrambleSentences = ACTIVE_UNIT.scrambleSentences;
const trueFalseSentences = ACTIVE_UNIT.trueFalseSentences;

/* ==========================================================================
   TEXT-TO-SPEECH (Web Speech API)
   ========================================================================== */
function speak(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.85;
    utterance.pitch = 1.1;
    // Pick an American English female voice
    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(v => v.lang === 'en-US' && v.name.includes('Samantha'))
        || voices.find(v => v.lang === 'en-US' && v.name.includes('Female'))
        || voices.find(v => v.lang === 'en-US')
        || voices.find(v => v.lang.startsWith('en'));
    if (englishVoice) utterance.voice = englishVoice;
    window.speechSynthesis.speak(utterance);
}

// Pre-load voices
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

/* ==========================================================================
   UTILITY FUNCTIONS (English-specific)
   ========================================================================== */

/** Pick n random unique items from array, excluding a specific item */
function pickRandom(arr, n, exclude) {
    const filtered = exclude ? arr.filter(item => item !== exclude) : [...arr];
    shuffle(filtered);
    return filtered.slice(0, n);
}

/** Build coverage map: which vocab words appear in which sentences */
function buildCoverageMap() {
    const map = new Map();
    vocabulary.forEach(v => map.set(v.english.toLowerCase(), { g2: [], g4: [] }));

    function matchWords(sentence, gameKey) {
        const sentenceWords = sentence.english.toLowerCase().split(' ');
        vocabulary.forEach(v => {
            const word = v.english.toLowerCase();
            const matched = sentenceWords.includes(word) ||
                word.split(' ').every(part => sentenceWords.includes(part));
            if (matched) {
                map.get(word)[gameKey].push(sentence);
            }
        });
    }

    scrambleSentences.forEach(s => matchWords(s, 'g2'));
    trueFalseSentences.forEach(s => matchWords(s, 'g4'));
    return map;
}

/** Count how many uncovered words a sentence covers */
function sentenceCoverage(sentence, uncovered) {
    const sentenceWords = sentence.english.toLowerCase().split(' ');
    let count = 0;
    uncovered.forEach(word => {
        const matched = sentenceWords.includes(word) ||
            word.split(' ').every(part => sentenceWords.includes(part));
        if (matched) count++;
    });
    return count;
}

/** Get vocab words covered by a sentence */
function getWordsInSentence(sentence) {
    const sentenceWords = sentence.english.toLowerCase().split(' ');
    return vocabulary
        .filter(v => {
            const word = v.english.toLowerCase();
            return sentenceWords.includes(word) ||
                word.split(' ').every(part => sentenceWords.includes(part));
        })
        .map(v => v.english.toLowerCase());
}

/** Plan a session: allocate all 55 words across 4 games for full coverage */
function planSession() {
    const uncovered = new Set(vocabulary.map(v => v.english.toLowerCase()));

    // Greedy pick 6 scramble sentences maximizing coverage
    const g2Available = [...scrambleSentences];
    const g2Selected = [];
    for (let i = 0; i < 6; i++) {
        // Score each available sentence by uncovered words it covers
        let bestIdx = 0;
        let bestScore = -1;
        g2Available.forEach((s, idx) => {
            const score = sentenceCoverage(s, uncovered);
            if (score > bestScore) {
                bestScore = score;
                bestIdx = idx;
            }
        });
        const picked = g2Available.splice(bestIdx, 1)[0];
        g2Selected.push(picked);
        getWordsInSentence(picked).forEach(w => uncovered.delete(w));
    }

    // Greedy pick 8 true/false sentences maximizing remaining coverage
    const g4Available = [...trueFalseSentences];
    const g4Selected = [];
    for (let i = 0; i < 8; i++) {
        let bestIdx = 0;
        let bestScore = -1;
        g4Available.forEach((s, idx) => {
            const score = sentenceCoverage(s, uncovered);
            if (score > bestScore) {
                bestScore = score;
                bestIdx = idx;
            }
        });
        const picked = g4Available.splice(bestIdx, 1)[0];
        g4Selected.push(picked);
        getWordsInSentence(picked).forEach(w => uncovered.delete(w));
    }

    // Remaining uncovered words go to Games 1 & 3 as direct vocabulary
    const remainingVocab = [...uncovered]
        .map(w => vocabulary.find(v => v.english.toLowerCase() === w))
        .filter(Boolean);
    shuffle(remainingVocab);

    // Split evenly between Game 1 and Game 3
    const half = Math.ceil(remainingVocab.length / 2);
    const g1Words = remainingVocab.slice(0, half);
    const g3Words = remainingVocab.slice(half);

    shuffle(g1Words);
    shuffle(g2Selected);
    shuffle(g3Words);
    shuffle(g4Selected);

    const plan = {
        game1Words: g1Words,
        game2Sentences: g2Selected,
        game3Words: g3Words,
        game4Sentences: g4Selected,
    };

    validateSessionPlan(plan);
    state.sessionPlan = plan;
}

/** Validate that a session plan covers all 55 vocabulary words */
function validateSessionPlan(plan) {
    const covered = new Set();

    // Games 1 & 3: direct vocabulary
    plan.game1Words.forEach(v => covered.add(v.english.toLowerCase()));
    plan.game3Words.forEach(v => covered.add(v.english.toLowerCase()));

    // Games 2 & 4: extract vocab from sentences
    [...plan.game2Sentences, ...plan.game4Sentences].forEach(s => {
        getWordsInSentence(s).forEach(w => covered.add(w));
    });

    const allWords = vocabulary.map(v => v.english.toLowerCase());
    const missing = allWords.filter(w => !covered.has(w));

    if (missing.length > 0) {
        console.warn('Session plan missing words:', missing);
    } else {
        console.log('Session plan: all 55 words covered!');
    }
    return missing;
}

/** Show reset confirmation dialog */
function confirmReset() {
    document.getElementById('reset-dialog').classList.add('active');
}

/** Close reset confirmation dialog */
function closeResetDialog() {
    document.getElementById('reset-dialog').classList.remove('active');
}

/** Execute reset — call API, clear session, reload word tracker */
async function executeReset() {
    const btn = document.querySelector('.reset-btn');
    btn.classList.add('spinning');
    closeResetDialog();

    try {
        await fetch(`${API_BASE}/reset`, { method: 'POST' });
    } catch (e) {
        // Reset still works client-side even if API fails
    }

    // Clear session checkmarks
    state.sessionGames = new Set();
    localStorage.removeItem('ariel_session_games');
    state.sessionStars = 0;
    // Re-enable all game cards
    for (let i = 1; i <= 4; i++) {
        const card = document.getElementById(`game-card-${i}`);
        if (card) card.classList.remove('completed');
    }
    // Reset word tracker
    state.practicedWords = new Set();
    buildWordTracker();
    // Re-plan session for fresh coverage
    state.sessionPlan = null;
    planSession();

    setTimeout(() => btn.classList.remove('spinning'), 600);
}

/* ==========================================================================
   SCREEN NAVIGATION (English-specific)
   ========================================================================== */

// Handle browser back/forward button
window.addEventListener('popstate', () => {
    const path = window.location.pathname;
    const parts = path.split('/').filter(Boolean); // e.g. ['learning', 'english', 'jet2-unit2']
    if (parts.length >= 3 && parts[0] === 'learning') {
        showScreen('menu-screen');
    } else if (parts.length === 2 && parts[0] === 'learning') {
        // /learning/english — session picker for a subject
        showScreen('session-picker-screen');
        loadSessionPickerProgress();
    } else if (path === '/learning') {
        showScreen('subject-picker-screen');
    } else {
        showScreen('welcome-screen');
    }
});

/** Navigate to subject picker screen */
function goToSubjectPicker() {
    showScreen('subject-picker-screen');
    if (window.location.pathname !== '/learning') {
        history.pushState(null, '', '/learning');
    }
}

/** Navigate to session picker screen for the current subject */
function goToSessionPicker() {
    const subjectPath = '/learning/' + SUBJECT;
    showScreen('session-picker-screen');
    if (window.location.pathname !== subjectPath) {
        history.pushState(null, '', subjectPath);
    }
    loadSessionPickerProgress();
}

/** Select a session and navigate to its game menu */
function selectSession(slug) {
    // Navigate to the session's game menu via full page load
    // This ensures SESSION_SLUG is set correctly from the server
    window.location.href = '/learning/' + SUBJECT + '/' + slug;
}

/** Load per-session star counts onto session picker cards */
async function loadSessionPickerProgress() {
    try {
        const res = await fetch(`${API_BASE}/progress`);
        if (res.ok) {
            const data = await res.json();
            if (data.success) {
                const starsBySession = data.data.stars_by_session || {};
                document.querySelectorAll('.session-card').forEach(card => {
                    const slugMatch = card.className.match(/session-card-(\S+)/);
                    if (slugMatch) {
                        const slug = slugMatch[1];
                        const count = starsBySession[slug] || 0;
                        const el = card.querySelector('.session-star-count');
                        if (el) el.textContent = count;
                    }
                });
            }
        }
    } catch (e) {
        // API unavailable — leave at 0
    }
}

function goToMenu(animate = true) {
    showScreen('menu-screen');
    const menuPath = '/learning/' + SUBJECT + '/' + (SESSION_SLUG || 'jet2-unit2');
    if (window.location.pathname !== menuPath) {
        history.pushState(null, '', menuPath);
    }
    updateStarDisplay();
    buildWordTracker();
    loadPracticedWords();
    // Plan session for full vocabulary coverage (only once per session)
    if (!state.sessionPlan) planSession();
    // Restore session checkmarks from localStorage
    state.sessionGames.forEach(gameNum => {
        const card = document.getElementById(`game-card-${gameNum}`);
        if (card) card.classList.add('completed');
    });
    // Animate cards only when navigating (not on page refresh)
    if (animate) {
        document.querySelectorAll('.game-card').forEach((card, i) => {
            card.style.animation = 'none';
            card.offsetHeight;
            card.style.animation = `slideUp 0.5s ease-out ${0.1 + i * 0.1}s forwards`;
        });
    }
    positionWordTracker();
}

function showSessionPopup() {
    document.getElementById('session-score').textContent = `${state.sessionStars} ⭐`;
    // Fireworks burst first, then popup fades in
    const overlay = document.getElementById('session-overlay');
    overlay.classList.add('active', 'fireworks-phase');
    spawnFireworks();
    playCelebration();
    // After fireworks, reveal the popup card
    setTimeout(() => {
        overlay.classList.remove('fireworks-phase');
        spawnConfetti();
    }, 1200);
}

function spawnFireworks() {
    const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#a855f7', '#ec4899', '#f43f5e', '#14b8a6'];
    const overlay = document.getElementById('session-overlay');
    for (let burst = 0; burst < 12; burst++) {
        setTimeout(() => {
            const cx = 5 + Math.random() * 90;
            const cy = 5 + Math.random() * 90;
            const sparkCount = 16 + Math.floor(Math.random() * 8);
            for (let i = 0; i < sparkCount; i++) {
                const angle = (i * (360 / sparkCount) + Math.random() * 15) * Math.PI / 180;
                const dist = 80 + Math.random() * 120;
                const spark = document.createElement('div');
                spark.className = 'firework-spark';
                spark.style.left = cx + '%';
                spark.style.top = cy + '%';
                spark.style.background = colors[Math.floor(Math.random() * colors.length)];
                spark.style.setProperty('--dx', Math.cos(angle) * dist + 'px');
                spark.style.setProperty('--dy', Math.sin(angle) * dist + 'px');
                overlay.appendChild(spark);
                setTimeout(() => spark.remove(), 1000);
            }
        }, burst * 150);
    }
}

function closeSessionPopup() {
    document.getElementById('session-overlay').classList.remove('active');
    // Just go back to menu — user can manually reset via 🔄 when ready
    goToMenu(false);
}

// Welcome screen: wait for button click
function welcomeClick() {
    initAudio(); // First user gesture — unlock AudioContext
    goToSubjectPicker();
}

/* ==========================================================================
   WORD TRACKER — vocabulary progress sidebar
   ========================================================================== */

/** Build the word tracker list and align to game cards */
function buildWordTracker() {
    const list = document.getElementById('word-tracker-list');
    const tracker = document.getElementById('word-tracker');
    if (!list || !tracker) return;

    const sorted = [...vocabulary].sort((a, b) => a.english.localeCompare(b.english));
    list.innerHTML = sorted.map(w =>
        `<span class="word-chip-tracker" data-word="${w.english}">${w.english}</span>`
    ).join('');

    // Re-apply practiced state
    document.querySelectorAll('.word-chip-tracker').forEach(el => {
        if (state.practicedWords.has(el.dataset.word.toLowerCase())) {
            el.classList.add('practiced');
        }
    });

    updateWordTrackerCount();

    // Position tracker aligned with game cards
    positionWordTracker();
}

/** Position word tracker aligned with game cards */
function positionWordTracker() {
    const tracker = document.getElementById('word-tracker');
    const firstCard = document.getElementById('game-card-1');
    const lastCard = document.getElementById('game-card-4');
    if (!tracker || !firstCard || !lastCard) return;

    const topY = firstCard.getBoundingClientRect().top - 56;
    const bottomY = lastCard.getBoundingClientRect().bottom;
    const height = bottomY - topY;

    tracker.style.top = topY + 'px';
    // Let height grow naturally to fit all words — remove any forced height
    tracker.style.height = 'auto';
    tracker.style.minHeight = height + 'px';
}

/** Mark words as practiced after a game finishes */
function markPracticedWords() {
    const game = state.currentGame;
    let words = [];

    if (game === 1 || game === 3) {
        // Games 1 & 3 use vocabulary items directly
        words = state.gameData.map(item => item.english.toLowerCase());
    } else if (game === 2) {
        // Game 2 uses sentences — match words from vocabulary that appear in the sentences
        const sentenceWords = state.gameData
            .flatMap(s => s.english.toLowerCase().split(' '));
        words = vocabulary
            .filter(v => sentenceWords.includes(v.english.toLowerCase()) ||
                         v.english.toLowerCase().split(' ').every(part => sentenceWords.includes(part)))
            .map(v => v.english.toLowerCase());
    } else if (game === 4) {
        // Game 4 uses true/false sentences — same approach
        const sentenceWords = state.gameData
            .flatMap(s => s.english.toLowerCase().split(' '));
        words = vocabulary
            .filter(v => sentenceWords.includes(v.english.toLowerCase()) ||
                         v.english.toLowerCase().split(' ').every(part => sentenceWords.includes(part)))
            .map(v => v.english.toLowerCase());
    }

    // Add to practiced set
    words.forEach(w => state.practicedWords.add(w));

    // Update UI
    document.querySelectorAll('.word-chip-tracker').forEach(el => {
        if (state.practicedWords.has(el.dataset.word.toLowerCase())) {
            el.classList.add('practiced');
        }
    });

    updateWordTrackerCount();
}

/** Update the remaining word count display */
function updateWordTrackerCount() {
    const countEl = document.getElementById('word-tracker-count');
    if (!countEl) return;
    const remaining = vocabulary.length - state.practicedWords.size;
    countEl.textContent = `${remaining}/${vocabulary.length} נשארו`;
}

/** Reset word tracker UI for a new session (keeps DB data) */
function resetWordTracker() {
    state.practicedWords = new Set();
    document.querySelectorAll('.word-chip-tracker').forEach(el => {
        el.classList.remove('practiced');
    });
    updateWordTrackerCount();
    // Re-load from DB so all-time progress is shown
    loadPracticedWords();
}

/** Load practiced words from the database */
async function loadPracticedWords() {
    try {
        const res = await fetch(`${API_BASE}/practiced-words`);
        if (!res.ok) return;
        const data = await res.json();
        if (data.success && data.data.practiced_words) {
            data.data.practiced_words.forEach(w => state.practicedWords.add(w));
            // Update chip UI
            document.querySelectorAll('.word-chip-tracker').forEach(el => {
                if (state.practicedWords.has(el.dataset.word.toLowerCase())) {
                    el.classList.add('practiced');
                }
            });
            updateWordTrackerCount();
        }
    } catch (e) {
        // Silently fail — word tracker still works with session data
    }
}

/* ==========================================================================
   GAME LAUNCHER
   ========================================================================== */
function startGame(gameNum) {
    initAudio();
    state.currentGame = gameNum;
    state.currentRound = 0;
    state.gameScore = 0;
    state.answering = false;
    state.wordResults = [];

    switch (gameNum) {
        case 1: initGame1(); break;
        case 2: initGame2(); break;
        case 3: initGame3(); break;
        case 4: initGame4(); break;
    }

    showScreen('game-screen');
    updateStarDisplay();
    updateProgress();
}

/* ==========================================================================
   GAME 1: WORD MATCH — מה המילה?
   ========================================================================== */
function initGame1() {
    document.getElementById('game-title').textContent = 'מה המילה? 🔤';
    state.gameData = shuffle([...state.sessionPlan.game1Words]);
    state.totalRounds = state.gameData.length;
    showGame1Round();
}

function showGame1Round() {
    if (state.currentRound >= state.totalRounds) {
        finishGame();
        return;
    }

    state.answering = false;
    const word = state.gameData[state.currentRound];
    const distractors = pickRandom(vocabulary, 3, word);
    const options = shuffle([word, ...distractors]);

    const content = document.getElementById('game-content');
    content.innerHTML = `
        <div class="question-area pop-in">
            <div class="question-emoji">${word.emoji}</div>
            <div class="question-text">${word.hebrew}</div>
            <button class="speaker-btn" onclick="speak('${word.english}')" title="שמעי">🔊</button>
        </div>
        <div class="answer-grid">
            ${options.map((opt, i) => `
                <button class="answer-btn" onclick="checkGame1Answer(this, '${opt.english}', '${word.english}')" style="animation: popIn 0.3s ease-out ${i * 0.08}s both">
                    <span class="btn-emoji">${opt.emoji}</span>
                    <span class="ltr">${opt.english}</span>
                </button>
            `).join('')}
        </div>
    `;
    updateProgress();
}

function checkGame1Answer(btn, selected, correct) {
    if (state.answering) return;
    state.answering = true;

    const buttons = document.querySelectorAll('.answer-btn');
    buttons.forEach(b => b.classList.add('disabled'));

    if (selected === correct) {
        btn.classList.add('correct');
        playCorrect();
        spawnConfetti();
        awardStar(1);
        // Wiggle mascot
        document.getElementById('mascot').classList.add('wiggle');
        setTimeout(() => document.getElementById('mascot').classList.remove('wiggle'), 600);
    } else {
        btn.classList.add('wrong');
        playWrong();
        // Show correct answer
        buttons.forEach(b => {
            if (b.querySelector('.ltr').textContent === correct) {
                b.classList.add('show-correct');
            }
        });
    }

    // Track word result
    const word = state.gameData[state.currentRound];
    state.wordResults.push({
        word: correct,
        correct: selected === correct,
        category: word ? word.category : '',
    });

    speak(correct);
    state.currentRound++;

    setTimeout(() => {
        showGame1Round();
    }, 1500);
}

/* ==========================================================================
   GAME 2: SENTENCE SCRAMBLE — תרגמי את המשפט
   ========================================================================== */
function initGame2() {
    document.getElementById('game-title').textContent = 'תרגמי את המשפט 📝';
    state.totalRounds = 6;
    state.gameData = shuffle([...state.sessionPlan.game2Sentences]);
    showGame2Round();
}

function showGame2Round() {
    if (state.currentRound >= state.totalRounds) {
        finishGame();
        return;
    }

    state.answering = false;
    state.scrambleWords = [];
    const sentence = state.gameData[state.currentRound];
    const words = sentence.english.split(' ');
    const shuffledWords = shuffle([...words]);

    const content = document.getElementById('game-content');
    content.innerHTML = `
        <div class="question-area pop-in">
            <div class="sentence-display">${sentence.hebrew}</div>
            <button class="speaker-btn" onclick="speak('${sentence.english}')" title="שמעי">🔊</button>
        </div>
        <div class="drop-zone" id="drop-zone">
            <span class="drop-zone-placeholder" id="dz-placeholder">...לחצי על מילים כדי לבנות משפט</span>
        </div>
        <div class="word-chips" id="word-chips">
            ${shuffledWords.map((w, i) => `
                <button class="word-chip" data-word="${w}" data-index="${i}"
                    onclick="addWordToZone(this)" style="animation: popIn 0.3s ease-out ${i * 0.06}s both">
                    ${w}
                </button>
            `).join('')}
        </div>
        <button class="check-btn" id="check-sentence-btn" onclick="checkGame2Answer()" disabled>בדקי ✓</button>
        <div id="sentence-feedback"></div>
    `;
    updateProgress();
}

function addWordToZone(chip) {
    if (state.answering) return;
    const word = chip.dataset.word;

    if (chip.classList.contains('placed')) {
        // Remove from drop zone
        chip.classList.remove('placed');
        state.scrambleWords = state.scrambleWords.filter(w => w.el !== chip);
        renderDropZone();
    } else {
        // Add to drop zone
        chip.classList.add('placed');
        state.scrambleWords.push({ word, el: chip });
        renderDropZone();
    }

    // Enable/disable check button
    const checkBtn = document.getElementById('check-sentence-btn');
    checkBtn.disabled = state.scrambleWords.length === 0;
}

function removeWordFromZone(index) {
    if (state.answering) return;
    const removed = state.scrambleWords.splice(index, 1)[0];
    if (removed && removed.el) {
        removed.el.classList.remove('placed');
    }
    renderDropZone();
    document.getElementById('check-sentence-btn').disabled = state.scrambleWords.length === 0;
}

function renderDropZone() {
    const zone = document.getElementById('drop-zone');
    const placeholder = document.getElementById('dz-placeholder');

    if (state.scrambleWords.length === 0) {
        placeholder.style.display = 'inline';
        zone.classList.remove('has-words');
        // Remove any word elements in zone
        zone.querySelectorAll('.word-chip.in-zone').forEach(el => el.remove());
        return;
    }

    placeholder.style.display = 'none';
    zone.classList.add('has-words');

    // Clear old zone words
    zone.querySelectorAll('.word-chip.in-zone').forEach(el => el.remove());

    // Render placed words in zone
    state.scrambleWords.forEach((item, i) => {
        const wordEl = document.createElement('button');
        wordEl.className = 'word-chip in-zone';
        wordEl.textContent = item.word;
        wordEl.onclick = () => removeWordFromZone(i);
        zone.appendChild(wordEl);
    });
}

function checkGame2Answer() {
    if (state.answering) return;
    state.answering = true;

    const sentence = state.gameData[state.currentRound];
    const correctWords = sentence.english.split(' ');
    const userWords = state.scrambleWords.map(w => w.word);
    const isCorrect = userWords.join(' ').toLowerCase() === correctWords.join(' ').toLowerCase();

    const feedback = document.getElementById('sentence-feedback');
    document.getElementById('check-sentence-btn').disabled = true;

    if (isCorrect) {
        playCorrect();
        spawnConfetti();
        awardStar(2);
        feedback.innerHTML = `<div class="correct-sentence">✅ !מצוין</div>`;
        document.getElementById('mascot').classList.add('wiggle');
        setTimeout(() => document.getElementById('mascot').classList.remove('wiggle'), 600);
    } else {
        playWrong();
        feedback.innerHTML = `<div class="correct-sentence">❌ התשובה הנכונה: ${sentence.english}</div>`;
    }

    // Track individual vocabulary words from this sentence
    getWordsInSentence(sentence).forEach(w => {
        state.wordResults.push({
            word: w,
            correct: isCorrect,
            category: 'sentence',
        });
    });

    speak(sentence.english);
    state.currentRound++;

    setTimeout(() => {
        showGame2Round();
    }, 2500);
}

/* ==========================================================================
   GAME 3: LISTEN & CHOOSE — האזיני ובחרי
   ========================================================================== */
function initGame3() {
    document.getElementById('game-title').textContent = 'האזיני ובחרי 🔊';
    state.gameData = shuffle([...state.sessionPlan.game3Words]);
    state.totalRounds = state.gameData.length;
    showGame3Round();
}

function showGame3Round() {
    if (state.currentRound >= state.totalRounds) {
        finishGame();
        return;
    }

    state.answering = false;
    const word = state.gameData[state.currentRound];
    const distractors = pickRandom(vocabulary, 3, word);
    const options = shuffle([word, ...distractors]);

    const content = document.getElementById('game-content');
    content.innerHTML = `
        <div class="question-area pop-in">
            <div class="question-text">מה המילה ששמעת?</div>
            <button class="speaker-btn large" onclick="speak('${word.english}')" title="שמעי שוב">🔊</button>
        </div>
        <div class="answer-grid">
            ${options.map((opt, i) => `
                <button class="answer-btn" onclick="checkGame3Answer(this, '${opt.english}', '${word.english}')" style="animation: popIn 0.3s ease-out ${i * 0.08}s both">
                    <span class="btn-emoji">${opt.emoji}</span>
                    <span class="ltr">${opt.english}</span>
                    <span class="btn-hebrew">${opt.hebrew}</span>
                </button>
            `).join('')}
        </div>
    `;
    updateProgress();

    // Auto-speak the word after a brief delay
    setTimeout(() => speak(word.english), 500);
}

function checkGame3Answer(btn, selected, correct) {
    if (state.answering) return;
    state.answering = true;

    const buttons = document.querySelectorAll('.answer-btn');
    buttons.forEach(b => b.classList.add('disabled'));

    if (selected === correct) {
        btn.classList.add('correct');
        playCorrect();
        spawnConfetti();
        awardStar(1);
        document.getElementById('mascot').classList.add('wiggle');
        setTimeout(() => document.getElementById('mascot').classList.remove('wiggle'), 600);
    } else {
        btn.classList.add('wrong');
        playWrong();
        buttons.forEach(b => {
            if (b.querySelector('.ltr').textContent === correct) {
                b.classList.add('show-correct');
            }
        });
    }

    // Track word result
    const word3 = state.gameData[state.currentRound];
    state.wordResults.push({
        word: correct,
        correct: selected === correct,
        category: word3 ? word3.category : '',
    });

    speak(correct);
    state.currentRound++;

    setTimeout(() => {
        showGame3Round();
    }, 1500);
}

/* ==========================================================================
   GAME 4: TRUE OR FALSE — כן או לא?
   ========================================================================== */
function initGame4() {
    document.getElementById('game-title').textContent = 'כן או לא? 🤔';
    state.totalRounds = 8;
    state.gameData = shuffle([...state.sessionPlan.game4Sentences]);
    showGame4Round();
}

function showGame4Round() {
    if (state.currentRound >= state.totalRounds) {
        finishGame();
        return;
    }

    state.answering = false;
    const item = state.gameData[state.currentRound];

    const content = document.getElementById('game-content');
    content.innerHTML = `
        <div class="question-area pop-in">
            <div class="tf-card">
                <div class="tf-english">${item.english}</div>
                <div class="tf-hebrew">${item.hebrew}</div>
                <button class="speaker-btn" onclick="speak('${item.english}')" title="שמעי">🔊</button>
            </div>
        </div>
        <div class="tf-buttons">
            <button class="tf-btn yes" onclick="checkGame4Answer(this, true, ${item.answer})">✅ כן</button>
            <button class="tf-btn no" onclick="checkGame4Answer(this, false, ${item.answer})">❌ לא</button>
        </div>
    `;
    updateProgress();
}

function checkGame4Answer(btn, selected, correct) {
    if (state.answering) return;
    state.answering = true;

    const buttons = document.querySelectorAll('.tf-btn');
    buttons.forEach(b => b.classList.add('disabled'));

    if (selected === correct) {
        btn.classList.add('correct');
        playCorrect();
        spawnConfetti();
        awardStar(1);
        document.getElementById('mascot').classList.add('wiggle');
        setTimeout(() => document.getElementById('mascot').classList.remove('wiggle'), 600);
    } else {
        btn.classList.add('wrong');
        playWrong();
        // Highlight the correct one
        buttons.forEach(b => {
            const isYes = b.classList.contains('yes');
            if ((correct && isYes) || (!correct && !isYes)) {
                b.classList.add('correct');
            }
        });
    }

    // Track individual vocabulary words from this sentence
    const item4 = state.gameData[state.currentRound];
    if (item4) {
        getWordsInSentence(item4).forEach(w => {
            state.wordResults.push({
                word: w,
                correct: selected === correct,
                category: 'true_false',
            });
        });
    }

    state.currentRound++;

    setTimeout(() => {
        showGame4Round();
    }, 1500);
}

/* ==========================================================================
   AWARD STARS & FINISH GAME
   ========================================================================== */
function awardStar(count) {
    state.gameScore += count;
    state.totalStars += count;
    saveStars();
    updateStarDisplay();
    checkMilestone();
}

function finishGame() {
    const starsPerCorrect = { 1: 1, 2: 2, 3: 1, 4: 1 };
    const max = state.totalRounds * (starsPerCorrect[state.currentGame] || 1);

    // Track session progress + mark card as completed
    state.sessionGames.add(state.currentGame);
    localStorage.setItem('ariel_session_games', JSON.stringify([...state.sessionGames]));
    state.sessionStars += state.gameScore;
    markPracticedWords();
    const completedCard = document.getElementById(`game-card-${state.currentGame}`);
    if (completedCard) completedCard.classList.add('completed');

    document.getElementById('complete-score').textContent =
        `${state.gameScore} / ${max} ⭐ הרווחת`;
    document.getElementById('complete-total-stars').textContent =
        `⭐ ${state.totalStars} :סה"כ כוכבים`;

    // Save to API
    const gameType = GAME_TYPE_MAP[state.currentGame];
    if (gameType) {
        saveGameResult(gameType, state.gameScore, max, state.wordResults);
    }

    // Set replay button
    const replayBtn = document.getElementById('replay-btn');
    const gameNum = state.currentGame;
    replayBtn.onclick = () => startGame(gameNum);

    showScreen('complete-screen');
    spawnConfetti();
    playCelebration();

    // If all 4 games completed — show session celebration after a moment
    if (state.sessionGames.size === 4) {
        setTimeout(() => showSessionPopup(), 2500);
    }
}

/** Restore checkmarks on session picker cards (data from API) */
function restoreSessionCheckmarks(completedSlugs) {
    (completedSlugs || []).forEach(slug => {
        const card = document.querySelector(`.session-card-${slug}`);
        if (card) card.classList.add('session-completed');
    });
}
