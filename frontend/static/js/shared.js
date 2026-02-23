/**
 * shared.js — Functions shared between English and Math templates.
 * Loaded after inline Jinja2 variables (REWARD_TIERS, SUBJECT, SESSION_SLUG).
 */

/* ==========================================================================
   API INTEGRATION
   ========================================================================== */
const API_BASE = '/api/game';

/** Load progress from API, fallback to localStorage */
async function loadProgress() {
    try {
        const res = await fetch(`${API_BASE}/progress`);
        if (res.ok) {
            const data = await res.json();
            if (data.success) {
                state.totalStars = data.data.total_stars;
                localStorage.setItem('ariel_stars', state.totalStars.toString());
                // Sync earned rewards from API (handles localStorage cleared)
                if (data.data.earned_rewards) {
                    localStorage.setItem('ariel_earned_rewards', JSON.stringify(data.data.earned_rewards));
                }
                // Restore session completion checkmarks from DB (English only)
                if (data.data.completed_sessions && typeof restoreSessionCheckmarks === 'function') {
                    restoreSessionCheckmarks(data.data.completed_sessions);
                }
                updateStarDisplay();
                return;
            }
        }
    } catch (e) {
        // API unavailable — use localStorage fallback
    }
}

/** Save game result to API, always save to localStorage too */
async function saveGameResult(gameType, score, maxScore, wordResults) {
    // Always save to localStorage as fallback
    saveStars();

    try {
        await fetch(`${API_BASE}/result`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_type: gameType,
                score: score,
                max_score: maxScore,
                word_results: wordResults,
                session_slug: SESSION_SLUG || null,
            }),
        });
    } catch (e) {
        // API unavailable — localStorage already saved
    }
}

/* ==========================================================================
   AUDIO SYSTEM (AudioContext)
   ========================================================================== */
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

function playTone(freq, duration, type, startTime) {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type || 'sine';
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.3, startTime);
    gain.gain.exponentialRampToValueAtTime(0.01, startTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(startTime);
    osc.stop(startTime + duration);
}

/** Ascending C-E-G chime for correct answers */
function playCorrect() {
    initAudio();
    const now = audioCtx.currentTime;
    playTone(523.25, 0.15, 'sine', now);        // C5
    playTone(659.25, 0.15, 'sine', now + 0.1);  // E5
    playTone(783.99, 0.25, 'sine', now + 0.2);  // G5
}

/** Low sawtooth buzz for wrong answers */
function playWrong() {
    initAudio();
    const now = audioCtx.currentTime;
    playTone(150, 0.3, 'sawtooth', now);
}

/** 4-note celebration melody for milestones */
function playCelebration() {
    initAudio();
    const now = audioCtx.currentTime;
    playTone(523.25, 0.2, 'sine', now);          // C5
    playTone(659.25, 0.2, 'sine', now + 0.2);    // E5
    playTone(783.99, 0.2, 'sine', now + 0.4);    // G5
    playTone(1046.50, 0.4, 'sine', now + 0.6);   // C6
}

/* ==========================================================================
   UTILITY FUNCTIONS
   ========================================================================== */

/** Shuffle array in place (Fisher-Yates) */
function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

/** Save stars to localStorage */
function saveStars() {
    localStorage.setItem('ariel_stars', state.totalStars.toString());
}

/** Update all star counter displays */
function updateStarDisplay() {
    ['subject-star-count', 'star-count', 'menu-star-count', 'game-star-count'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = state.totalStars;
    });
    updateTrophyCount();
}

/** Update progress bar */
function updateProgress() {
    const pct = ((state.currentRound) / state.totalRounds) * 100;
    document.getElementById('progress-bar').style.width = pct + '%';
    document.getElementById('round-indicator').textContent =
        `${state.currentRound} / ${state.totalRounds}`;
}

/* ==========================================================================
   CONFETTI SYSTEM
   ========================================================================== */
function spawnConfetti() {
    const container = document.getElementById('confetti-container');
    const colors = ['#a855f7', '#f97316', '#eab308', '#ec4899', '#22c55e', '#3b82f6', '#ef4444'];
    for (let i = 0; i < 30; i++) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        piece.style.left = Math.random() * 100 + '%';
        piece.style.background = colors[Math.floor(Math.random() * colors.length)];
        piece.style.animationDelay = Math.random() * 0.8 + 's';
        piece.style.animationDuration = (1.5 + Math.random() * 1.5) + 's';
        piece.style.width = (6 + Math.random() * 8) + 'px';
        piece.style.height = (6 + Math.random() * 8) + 'px';
        piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
        container.appendChild(piece);
    }
    setTimeout(() => { container.innerHTML = ''; }, 3000);
}

/* ==========================================================================
   MILESTONE CELEBRATIONS
   ========================================================================== */
let lastMilestoneStars = parseInt(localStorage.getItem('ariel_last_milestone') || '0');

function checkMilestone() {
    // Check every 5 stars
    const currentMilestone = Math.floor(state.totalStars / 5) * 5;
    if (currentMilestone > lastMilestoneStars && currentMilestone > 0) {
        lastMilestoneStars = currentMilestone;
        localStorage.setItem('ariel_last_milestone', lastMilestoneStars.toString());

        if (state.totalStars >= 10 && currentMilestone % 10 === 0) {
            showEmojiParade();
        } else {
            showMilestone();
        }
    }
    // Check for reward tier unlock (queued after milestone animation)
    checkRewardUnlock();
}

function showMilestone() {
    const overlay = document.getElementById('milestone-overlay');
    document.getElementById('milestone-emoji').textContent = '🎉';
    document.getElementById('milestone-text').textContent = 'כל הכבוד אריאל!';
    document.getElementById('milestone-sub').textContent = `⭐ ${state.totalStars} כוכבים!`;
    overlay.classList.add('active');
    playCelebration();
    spawnConfetti();

    // Wiggle mascot
    const mascot = document.getElementById('mascot');
    mascot.classList.add('wiggle');
    setTimeout(() => mascot.classList.remove('wiggle'), 600);

    setTimeout(() => { overlay.classList.remove('active'); }, 2500);
}

function showEmojiParade() {
    const overlay = document.getElementById('milestone-overlay');
    document.getElementById('milestone-emoji').textContent = '🏆';
    document.getElementById('milestone-text').textContent = 'כל הכבוד אריאל!';
    document.getElementById('milestone-sub').textContent = `🌟 ${state.totalStars} כוכבים — מדהים!`;
    overlay.classList.add('active');
    playCelebration();

    // Spawn parade emojis
    const emojis = ['🎊', '🎉', '🏆', '🎉', '🎊', '⭐', '🌟', '💫'];
    emojis.forEach((emoji, i) => {
        setTimeout(() => {
            const el = document.createElement('div');
            el.className = 'parade-emoji';
            el.textContent = emoji;
            el.style.left = (10 + Math.random() * 80) + '%';
            el.style.animationDelay = (Math.random() * 0.5) + 's';
            document.body.appendChild(el);
            setTimeout(() => el.remove(), 3000);
        }, i * 200);
    });

    setTimeout(() => { overlay.classList.remove('active'); }, 3000);
}

/* ==========================================================================
   REWARD COLLECTION SYSTEM
   ========================================================================== */

/** Get earned reward IDs from localStorage */
function getEarnedRewards() {
    return JSON.parse(localStorage.getItem('ariel_earned_rewards') || '[]');
}

/** Save earned reward IDs to localStorage */
function saveEarnedRewards(earned) {
    localStorage.setItem('ariel_earned_rewards', JSON.stringify(earned));
}

/** Update trophy count badges in header */
function updateTrophyCount() {
    const earned = getEarnedRewards();
    const text = `${earned.length}/${REWARD_TIERS.length}`;
    ['subject-trophy-count', 'trophy-count', 'menu-trophy-count', 'game-trophy-count'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    });
}

/** Check if a new reward tier was unlocked */
function checkRewardUnlock() {
    const earned = getEarnedRewards();
    const newTier = REWARD_TIERS.find(t => t.stars <= state.totalStars && !earned.includes(t.id));
    if (newTier) {
        earned.push(newTier.id);
        saveEarnedRewards(earned);
        updateTrophyCount();
        // Queue popup after milestone animation (3s delay)
        setTimeout(() => showRewardPopup(newTier), 3000);
    }
}

let rewardAutoCloseTimer = null;

/** Show reward unlock popup */
function showRewardPopup(tier) {
    document.getElementById('reward-emoji').textContent = tier.emoji;
    document.getElementById('reward-name').textContent = tier.name_en;
    document.getElementById('reward-name-he').textContent = tier.name_he;
    document.getElementById('reward-desc').textContent = tier.description_he;
    document.getElementById('reward-stars').textContent = `⭐ ${tier.stars}`;

    // Reset animation by re-inserting the card
    const card = document.querySelector('.reward-card');
    card.style.animation = 'none';
    card.offsetHeight;
    card.style.animation = 'rewardReveal 0.8s ease-out both';

    const overlay = document.getElementById('reward-overlay');
    overlay.classList.add('active');
    playCelebration();
    spawnConfetti();

    // Auto-close after 5 seconds so it doesn't block gameplay
    clearTimeout(rewardAutoCloseTimer);
    rewardAutoCloseTimer = setTimeout(closeRewardPopup, 5000);
}

/** Close reward popup */
function closeRewardPopup() {
    clearTimeout(rewardAutoCloseTimer);
    document.getElementById('reward-overlay').classList.remove('active');
}

/** Open the collection gallery */
function openCollection() {
    const earned = getEarnedRewards();
    const grid = document.getElementById('collection-grid');
    grid.innerHTML = '';

    REWARD_TIERS.forEach((tier, i) => {
        const isEarned = earned.includes(tier.id);
        const card = document.createElement('div');
        card.className = `collection-card ${isEarned ? 'earned' : 'locked'}`;
        card.style.animation = `popIn 0.3s ease-out ${i * 0.08}s both`;

        if (isEarned) {
            card.innerHTML = `
                <div class="collection-card-emoji">${tier.emoji}</div>
                <div class="collection-card-name">${tier.name_en}</div>
                <div class="collection-card-name-he">${tier.name_he}</div>
                <div class="collection-card-stars">⭐ ${tier.stars}</div>
            `;
        } else {
            card.innerHTML = `
                <div class="collection-card-emoji">${tier.emoji}</div>
                <div class="collection-card-lock">⭐ ${tier.stars}</div>
            `;
        }
        grid.appendChild(card);
    });

    // Progress bar
    const progressEl = document.getElementById('collection-progress');
    const nextTier = REWARD_TIERS.find(t => !earned.includes(t.id));
    if (nextTier) {
        const progress = Math.min((state.totalStars / nextTier.stars) * 100, 100);
        progressEl.innerHTML = `
            <div class="collection-progress-text">⭐ הפרס הבא ב: ${nextTier.stars}</div>
            <div class="collection-progress-bar">
                <div class="collection-progress-fill" style="width: ${progress}%"></div>
            </div>
        `;
    } else {
        progressEl.innerHTML = `<div class="collection-progress-text">🎉 אספת את כל הפרסים!</div>`;
    }

    document.getElementById('collection-overlay').classList.add('active');
}

/** Close collection gallery */
function closeCollection() {
    document.getElementById('collection-overlay').classList.remove('active');
}

/* ==========================================================================
   SCREEN NAVIGATION
   ========================================================================== */
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

function switchSubject(subject) {
    // Navigate to the subject's session picker
    window.location.href = '/learning/' + subject + '/';
}
