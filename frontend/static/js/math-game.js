/**
 * math-game.js — Math game logic functions.
 * Loaded after shared.js and math-data.js.
 * Expects globals: CATEGORIES_BY_SESSION, MATH_HINTS, GAME_TYPE_MAP,
 *   STARS_PER_CORRECT, ROUNDS_PER_GAME, SESSION_SLUG, SUBJECT, REWARD_TIERS,
 *   state, API_BASE, and all shared.js functions.
 */

/* ==========================================================================
   PROBLEM GENERATORS
   ========================================================================== */

/** Generate a math problem for the current session.
 *  Returns { equation, answer, display, category }
 *  - equation: string like "7 × 100"
 *  - answer: number result
 *  - display: formatted string for display (uses Israeli notation)
 *  - category: topic tag for tracking
 */
function generateProblem() {
    const categories = CATEGORIES_BY_SESSION[SESSION_SLUG] || CATEGORIES_BY_SESSION['math-tens-hundreds'];
    const cat = categories[Math.floor(Math.random() * categories.length)];
    return generateProblemByCategory(cat);
}

function generateProblemByCategory(category) {
    switch (category) {
        case 'multiply_tens': {
            // e.g. 30 × 4, 60 × 7 — keep bases friendly (10-90)
            const base = [10, 20, 30, 40, 50, 60, 70, 80, 90][Math.floor(Math.random() * 9)];
            const factor = 2 + Math.floor(Math.random() * 7); // 2-8
            const answer = base * factor;
            return { equation: `${base} × ${factor}`, answer, display: `${base} × ${factor} = ?`, category,
                hint: MATH_HINTS.multiply_tens(base, factor),
            };
        }
        case 'multiply_hundreds': {
            // e.g. 7 × 100, 3 × 100 — keep to ×100 only (×1000 too big)
            const factor = 2 + Math.floor(Math.random() * 8); // 2-9
            const answer = factor * 100;
            return { equation: `${factor} × 100`, answer, display: `${factor} × 100 = ?`, category,
                hint: MATH_HINTS.multiply_hundreds(factor),
            };
        }
        case 'divide_single': {
            // e.g. 120 : 4 = 30 — keep quotients small (10-50)
            const divisor = 2 + Math.floor(Math.random() * 8); // 2-9
            const quotient = [10, 20, 30, 40, 50][Math.floor(Math.random() * 5)];
            const dividend = divisor * quotient;
            return { equation: `${dividend} : ${divisor}`, answer: quotient, display: `${dividend} : ${divisor} = ?`, category,
                hint: MATH_HINTS.divide_single(divisor, dividend),
            };
        }
        case 'divide_tens': {
            // e.g. 300 : 10, 500 : 100
            const divisor = [10, 100][Math.floor(Math.random() * 2)];
            const quotient = (2 + Math.floor(Math.random() * 7)) * (divisor === 10 ? 10 : 1);
            const dividend = divisor * quotient;
            return { equation: `${dividend} : ${divisor}`, answer: quotient, display: `${dividend} : ${divisor} = ?`, category,
                hint: MATH_HINTS.divide_tens(divisor, dividend),
            };
        }
        case 'properties_0_1': {
            // 0 × n = 0, 1 × n = n — keep n small and friendly (2-100)
            const n = [5, 8, 12, 17, 20, 25, 30, 42, 50, 64, 75, 88, 100][Math.floor(Math.random() * 13)];
            const variant = Math.floor(Math.random() * 4);
            if (variant === 0) return { equation: `0 × ${n}`, answer: 0, display: `0 × ${n} = ?`, category, hint: MATH_HINTS.properties_zero };
            if (variant === 1) return { equation: `${n} × 0`, answer: 0, display: `${n} × 0 = ?`, category, hint: MATH_HINTS.properties_zero };
            if (variant === 2) return { equation: `1 × ${n}`, answer: n, display: `1 × ${n} = ?`, category, hint: MATH_HINTS.properties_one };
            return { equation: `${n} × 1`, answer: n, display: `${n} × 1 = ?`, category, hint: MATH_HINTS.properties_one };
        }
        case 'order_of_operations': {
            // Simple: a + b × c or (a + b) × c — small numbers
            const a = 2 + Math.floor(Math.random() * 6); // 2-7
            const b = 2 + Math.floor(Math.random() * 6); // 2-7
            const c = 2 + Math.floor(Math.random() * 4); // 2-5
            if (Math.random() < 0.5) {
                const answer = a + b * c;
                return { equation: `${a} + ${b} × ${c}`, answer, display: `${a} + ${b} × ${c} = ?`, category,
                    hint: MATH_HINTS.order_no_parens,
                };
            } else {
                const answer = (a + b) * c;
                return { equation: `(${a} + ${b}) × ${c}`, answer, display: `(${a} + ${b}) × ${c} = ?`, category,
                    hint: MATH_HINTS.order_with_parens,
                };
            }
        }
        /* ------ Chapter B: Two-Digit Multiply ------ */
        case 'two_digit_x_one_digit': {
            // e.g. 23 × 4 = 92 — keep products ≤ 500
            const a = 11 + Math.floor(Math.random() * 89); // 11-99
            const b = 2 + Math.floor(Math.random() * 8);   // 2-9
            if (a * b > 500) return generateProblemByCategory(category); // retry
            const answer = a * b;
            const tens = Math.floor(a / 10) * 10;
            const ones = a % 10;
            return { equation: `${a} × ${b}`, answer, display: `${a} × ${b} = ?`, category,
                hint: MATH_HINTS.two_digit_x_one(tens, ones, b),
            };
        }
        case 'two_digit_x_two_digit': {
            // e.g. 15 × 12 = 180 — keep products ≤ 2000
            const a = 11 + Math.floor(Math.random() * 39); // 11-49
            const b = 11 + Math.floor(Math.random() * 39); // 11-49
            if (a * b > 2000) return generateProblemByCategory(category); // retry
            const answer = a * b;
            return { equation: `${a} × ${b}`, answer, display: `${a} × ${b} = ?`, category,
                hint: MATH_HINTS.two_digit_x_two(b),
            };
        }
        case 'powers': {
            // e.g. 5² = 25 — bases 2-12
            const base = 2 + Math.floor(Math.random() * 11); // 2-12
            const answer = base * base;
            return { equation: `${base}²`, answer, display: `${base}² = ?`, category,
                hint: MATH_HINTS.powers(base),
            };
        }
        /* ------ Chapter C: Long Division ------ */
        case 'divide_remainder': {
            // e.g. 47 : 5 = 9 remainder 2 — dividends 20-99, divisors 2-9
            const divisor = 2 + Math.floor(Math.random() * 8); // 2-9
            const quotient = 3 + Math.floor(Math.random() * 15); // 3-17
            const remainder = 1 + Math.floor(Math.random() * (divisor - 1)); // 1 to divisor-1
            const dividend = divisor * quotient + remainder;
            if (dividend > 99) return generateProblemByCategory(category); // retry
            return {
                equation: `${dividend} : ${divisor}`,
                answer: quotient,
                remainder,
                display: `${dividend} : ${divisor} = ?`,
                category,
                hint: MATH_HINTS.divide_remainder(divisor, dividend),
            };
        }
        case 'long_division': {
            // e.g. 156 : 12 = 13 — 3-digit ÷ 1-digit, clean result
            const divisor = 2 + Math.floor(Math.random() * 8); // 2-9
            const quotient = 11 + Math.floor(Math.random() * 90); // 11-100
            const dividend = divisor * quotient;
            if (dividend > 999) return generateProblemByCategory(category); // retry
            return {
                equation: `${dividend} : ${divisor}`,
                answer: quotient,
                display: `${dividend} : ${divisor} = ?`,
                category,
                hint: MATH_HINTS.long_division(divisor),
            };
        }
        case 'division_verify': {
            // e.g. ? × 7 = 63 — reverse: find the missing factor
            const a = 2 + Math.floor(Math.random() * 8); // 2-9
            const b = 3 + Math.floor(Math.random() * 15); // 3-17
            const product = a * b;
            if (Math.random() < 0.5) {
                return {
                    equation: `? × ${a} = ${product}`,
                    answer: b,
                    display: `? × ${a} = ${product}`,
                    category,
                    hint: MATH_HINTS.division_verify_q(a, product),
                };
            }
            return {
                equation: `${product} : ? = ${b}`,
                answer: a,
                display: `${product} : ? = ${b}`,
                category,
                hint: MATH_HINTS.division_verify_d(b, product),
            };
        }
        /* ------ Chapter D: Primes & Divisibility ------ */
        case 'divisibility_rules': {
            // e.g. 123 : 3 = 41 — division by 3, 6, or 9 (clean results only)
            const divisor = [3, 6, 9][Math.floor(Math.random() * 3)];
            const quotient = 4 + Math.floor(Math.random() * 30); // 4-33
            const dividend = divisor * quotient;
            if (dividend > 200) return generateProblemByCategory(category); // retry — keep friendly
            const digits = String(dividend).split('').map(Number);
            const digitSum = digits.reduce((a, b) => a + b, 0);
            let hint;
            if (divisor === 3) {
                hint = MATH_HINTS.divisibility_3(digits);
            } else if (divisor === 9) {
                hint = MATH_HINTS.divisibility_9(digits);
            } else {
                hint = MATH_HINTS.divisibility_6;
            }
            return { equation: `${dividend} : ${divisor}`, answer: quotient, display: `${dividend} : ${divisor} = ?`, category, hint };
        }
        case 'prime_composite': {
            // Identify prime vs composite via factorization — e.g. "_ × 3 = 21" (answer 7)
            // or for primes: "1 × _ = 13" (answer 13 — the number itself)
            const PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47];
            const COMPOSITES = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30, 32, 33, 34, 35, 36, 38, 39, 40, 42, 44, 45, 46, 48, 49, 50];
            if (Math.random() < 0.4) {
                // Prime — show as "1 × ? = p"
                const p = PRIMES[Math.floor(Math.random() * PRIMES.length)];
                return {
                    equation: `1 × ? = ${p}`,
                    answer: p,
                    display: `1 × ? = ${p}`,
                    category,
                    hint: MATH_HINTS.prime(p),
                };
            } else {
                // Composite — find smallest prime factor and use it
                const n = COMPOSITES[Math.floor(Math.random() * COMPOSITES.length)];
                let smallestFactor = 2;
                for (let f = 2; f <= n; f++) {
                    if (n % f === 0) { smallestFactor = f; break; }
                }
                const other = n / smallestFactor;
                return {
                    equation: `? × ${smallestFactor} = ${n}`,
                    answer: other,
                    display: `? × ${smallestFactor} = ${n}`,
                    category,
                    hint: MATH_HINTS.composite(n, smallestFactor),
                };
            }
        }
        case 'prime_factorization': {
            // e.g. "36 = 2 × 2 × 3 × _" — find the missing prime factor
            const FACTORIZATIONS = [
                { n: 12, factors: [2, 2, 3] },
                { n: 18, factors: [2, 3, 3] },
                { n: 20, factors: [2, 2, 5] },
                { n: 24, factors: [2, 2, 2, 3] },
                { n: 28, factors: [2, 2, 7] },
                { n: 30, factors: [2, 3, 5] },
                { n: 36, factors: [2, 2, 3, 3] },
                { n: 40, factors: [2, 2, 2, 5] },
                { n: 42, factors: [2, 3, 7] },
                { n: 45, factors: [3, 3, 5] },
                { n: 48, factors: [2, 2, 2, 2, 3] },
                { n: 50, factors: [2, 5, 5] },
                { n: 54, factors: [2, 3, 3, 3] },
                { n: 56, factors: [2, 2, 2, 7] },
                { n: 60, factors: [2, 2, 3, 5] },
                { n: 72, factors: [2, 2, 2, 3, 3] },
                { n: 75, factors: [3, 5, 5] },
                { n: 80, factors: [2, 2, 2, 2, 5] },
                { n: 90, factors: [2, 3, 3, 5] },
                { n: 100, factors: [2, 2, 5, 5] },
            ];
            const entry = FACTORIZATIONS[Math.floor(Math.random() * FACTORIZATIONS.length)];
            const blankIdx = Math.floor(Math.random() * entry.factors.length);
            const answer = entry.factors[blankIdx];
            const displayFactors = entry.factors.map((f, i) => i === blankIdx ? '_' : f);
            return {
                equation: `${entry.n} = ${entry.factors.join(' × ')}`,
                answer,
                display: `${entry.n} = ${displayFactors.join(' × ')}`,
                category,
                hint: MATH_HINTS.prime_factorization(entry.factors[0]),
            };
        }
        default:
            return generateProblemByCategory('multiply_tens');
    }
}

/** Generate distractors (wrong answers close to the correct one) */
function generateDistractors(correctAnswer, count) {
    const distractors = new Set();
    // Near-miss offsets that feel plausible — scale with answer size
    const small = correctAnswer <= 20;
    const offsets = small
        ? [1, -1, 2, -2, 3, -3, 5, -5]
        : [5, -5, 10, -10, 20, -20, 50, -50];
    // Shuffle for variety
    for (let i = offsets.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [offsets[i], offsets[j]] = [offsets[j], offsets[i]];
    }
    for (const offset of offsets) {
        if (distractors.size >= count) break;
        const d = correctAnswer + offset;
        if (d !== correctAnswer && d > 0) {
            distractors.add(d);
        }
    }
    // Fill remaining if needed
    while (distractors.size < count) {
        const range = small ? 5 : 30;
        const d = correctAnswer + Math.floor(Math.random() * range * 2) - range;
        if (d !== correctAnswer && d > 0) distractors.add(d);
    }
    return [...distractors].slice(0, count);
}

/** Generate a True/False problem — returns { display, isTrue, correctDisplay } */
function generateTFProblem() {
    const problem = generateProblem();
    const isTrue = Math.random() < 0.5;
    const hasRemainder = problem.remainder !== undefined;

    /* --- Chapter D: prime_composite — "13 — מספר ראשוני" true/false --- */
    if (problem.category === 'prime_composite') {
        const PRIMES_SET = new Set([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]);
        const ALL_NUMS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50];
        const num = ALL_NUMS[Math.floor(Math.random() * ALL_NUMS.length)];
        const actuallyPrime = PRIMES_SET.has(num);
        if (isTrue) {
            const label = actuallyPrime ? 'מספר ראשוני' : 'מספר פריק';
            const correctStr = `${num} — ${label}`;
            return { display: correctStr, isTrue: true, correctDisplay: correctStr, hint: problem.hint };
        } else {
            const wrongLabel = actuallyPrime ? 'מספר פריק' : 'מספר ראשוני';
            const correctLabel = actuallyPrime ? 'מספר ראשוני' : 'מספר פריק';
            return {
                display: `${num} — ${wrongLabel}`,
                isTrue: false,
                correctDisplay: `${num} — ${correctLabel}`,
                hint: actuallyPrime
                    ? MATH_HINTS.prime(num)
                    : MATH_HINTS.composite_tf(num, [2,3,5,7].find(f => num % f === 0)),
            };
        }
    }

    /* --- Chapter D: prime_factorization — "36 = 2 × 2 × 3 × 3" true/false --- */
    if (problem.category === 'prime_factorization') {
        // equation holds the full correct factorization like "36 = 2 × 2 × 3 × 3"
        const correctStr = problem.equation;
        if (isTrue) {
            return { display: correctStr, isTrue: true, correctDisplay: correctStr, hint: problem.hint };
        } else {
            // Swap one factor to make it wrong
            const parts = correctStr.split(' = ');
            const factors = parts[1].split(' × ').map(Number);
            const swapIdx = Math.floor(Math.random() * factors.length);
            const origFactor = factors[swapIdx];
            const wrongFactor = origFactor === 2 ? 3 : origFactor === 3 ? 2 : origFactor === 5 ? 3 : origFactor === 7 ? 5 : 2;
            factors[swapIdx] = wrongFactor;
            const wrongStr = `${parts[0]} = ${factors.join(' × ')}`;
            return { display: wrongStr, isTrue: false, correctDisplay: correctStr, hint: problem.hint };
        }
    }

    // Format answer with remainder if applicable
    const correctStr = hasRemainder
        ? `${problem.equation} = ${problem.answer} שארית ${problem.remainder}`
        : `${problem.equation} = ${problem.answer}`;

    if (isTrue) {
        return {
            display: correctStr,
            isTrue: true,
            correctDisplay: correctStr,
            hint: problem.hint,
        };
    } else {
        if (hasRemainder) {
            // Swap remainder or quotient to make it wrong
            const wrongR = problem.remainder + (Math.random() < 0.5 ? 1 : -1);
            const wrongQ = problem.answer + (Math.random() < 0.5 ? 1 : -1);
            const wrongStr = Math.random() < 0.5
                ? `${problem.equation} = ${problem.answer} שארית ${Math.max(0, wrongR)}`
                : `${problem.equation} = ${wrongQ} שארית ${problem.remainder}`;
            return { display: wrongStr, isTrue: false, correctDisplay: correctStr, hint: problem.hint };
        }
        const wrongAnswer = generateDistractors(problem.answer, 1)[0];
        return {
            display: `${problem.equation} = ${wrongAnswer}`,
            isTrue: false,
            correctDisplay: correctStr,
            hint: problem.hint,
        };
    }
}

/* ==========================================================================
   SCREEN NAVIGATION (Math-specific)
   ========================================================================== */

// Handle browser back/forward button
window.addEventListener('popstate', () => {
    const path = window.location.pathname;
    const parts = path.split('/').filter(Boolean);
    if (parts.length >= 3 && parts[0] === 'learning') {
        showScreen('menu-screen');
    } else {
        window.location.href = '/learning/math/';
    }
});

function goToMenu(animate = true) {
    showScreen('menu-screen');
    const menuPath = '/learning/math/' + SESSION_SLUG;
    if (window.location.pathname !== menuPath) {
        history.pushState(null, '', menuPath);
    }
    updateStarDisplay();
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
}

function showSessionPopup() {
    document.getElementById('session-score').textContent = `${state.sessionStars} ⭐`;
    const overlay = document.getElementById('session-overlay');
    overlay.classList.add('active', 'fireworks-phase');
    spawnFireworks();
    playCelebration();
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
    goToMenu(false);
}

// Welcome screen: wait for button click (not used in math template but kept for consistency)
function welcomeClick() {
    initAudio();
    showScreen('menu-screen');
    goToMenu();
}

/* ==========================================================================
   HINT SYSTEM — 💡 tooltip for solving clues
   ========================================================================== */

/** Render a hint button HTML string. Returns empty string if no hint. */
function renderHintBtn(hint) {
    if (!hint) return '';
    return `<button class="hint-btn" onclick="toggleHint(this)" aria-label="רמז">💡<div class="hint-tooltip">${hint}</div></button>`;
}

function toggleHint(btn) {
    btn.classList.toggle('active');
    // Auto-close after 4 seconds
    if (btn.classList.contains('active')) {
        setTimeout(() => btn.classList.remove('active'), 4000);
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
    state.totalRounds = ROUNDS_PER_GAME[gameNum];

    switch (gameNum) {
        case 1: initQuickSolve(); break;
        case 2: initMissingNumber(); break;
        case 3: initTrueFalseMath(); break;
        case 4: initBubblePop(); break;
    }

    showScreen('game-screen');
    updateStarDisplay();
    updateProgress();
}

/* ==========================================================================
   GAME 1: QUICK SOLVE — פתרי מהר!
   ========================================================================== */
function initQuickSolve() {
    document.getElementById('game-title').textContent = 'פתרי מהר! ⚡';
    showQuickSolveRound();
}

function showQuickSolveRound() {
    if (state.currentRound >= state.totalRounds) { finishGame(); return; }
    state.answering = false;

    const problem = generateProblem();
    state._currentProblem = problem;
    const content = document.getElementById('game-content');

    // Remainder problems get dual-input UI
    if (problem.remainder !== undefined) {
        content.innerHTML = `
            <div class="question-area pop-in">
                <div class="equation-display">${problem.display}</div>
                ${renderHintBtn(problem.hint)}
            </div>
            <div class="remainder-inputs pop-in">
                <div class="input-group">
                    <label>מנה</label>
                    <input type="number" id="quotient-input" inputmode="numeric" autofocus>
                </div>
                <div class="input-group">
                    <label>שארית</label>
                    <input type="number" id="remainder-input" inputmode="numeric">
                </div>
            </div>
            <button class="remainder-submit" onclick="checkQuickSolveRemainder()">בדקי ←</button>
            <div id="remainder-feedback" style="margin-top: var(--space-md); text-align: center;"></div>
        `;
        document.getElementById('quotient-input').focus();
        // Submit on Enter from either input
        content.querySelectorAll('input').forEach(inp => {
            inp.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') checkQuickSolveRemainder();
            });
        });
    } else {
        // Standard multiple-choice
        const distractors = generateDistractors(problem.answer, 3);
        const options = shuffle([problem.answer, ...distractors]);
        content.innerHTML = `
            <div class="question-area pop-in">
                <div class="equation-display">${problem.display}</div>
                ${renderHintBtn(problem.hint)}
            </div>
            <div class="answer-grid">
                ${options.map((opt, i) => `
                    <button class="answer-btn" onclick="checkQuickSolve(this, ${opt}, ${problem.answer})" style="animation: popIn 0.3s ease-out ${i * 0.08}s both">
                        ${opt}
                    </button>
                `).join('')}
            </div>
        `;
    }
    updateProgress();
}

function checkQuickSolve(btn, selected, correct) {
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
            if (parseInt(b.textContent) === correct) b.classList.add('show-correct');
        });
    }

    state.wordResults.push({
        word: state._currentProblem.equation,
        correct: selected === correct,
        category: state._currentProblem.category,
    });

    state.currentRound++;
    setTimeout(() => showQuickSolveRound(), 1500);
}

function checkQuickSolveRemainder() {
    if (state.answering) return;
    state.answering = true;

    const qInput = document.getElementById('quotient-input');
    const rInput = document.getElementById('remainder-input');
    const qVal = parseInt(qInput.value);
    const rVal = parseInt(rInput.value);
    const problem = state._currentProblem;
    const isCorrect = qVal === problem.answer && rVal === problem.remainder;
    const feedback = document.getElementById('remainder-feedback');

    document.querySelector('.remainder-submit').classList.add('disabled');
    document.querySelector('.remainder-submit').style.pointerEvents = 'none';

    if (isCorrect) {
        qInput.style.borderColor = 'var(--green)';
        rInput.style.borderColor = 'var(--green)';
        qInput.style.background = '#dcfce7';
        rInput.style.background = '#dcfce7';
        playCorrect();
        spawnConfetti();
        awardStar(1);
        document.getElementById('mascot').classList.add('wiggle');
        setTimeout(() => document.getElementById('mascot').classList.remove('wiggle'), 600);
    } else {
        qInput.style.borderColor = 'var(--red)';
        rInput.style.borderColor = 'var(--red)';
        qInput.style.background = '#fee2e2';
        rInput.style.background = '#fee2e2';
        playWrong();
        feedback.innerHTML = `<div style="font-family: var(--font-display); color: var(--green-dark); background: #dcfce7; padding: var(--space-md); border-radius: var(--radius-md); direction: ltr;">${problem.equation} = ${problem.answer} שארית ${problem.remainder}</div>`;
    }

    state.wordResults.push({
        word: problem.equation,
        correct: isCorrect,
        category: problem.category,
    });

    state.currentRound++;
    setTimeout(() => showQuickSolveRound(), 2000);
}

/* ==========================================================================
   GAME 2: MISSING NUMBER — מצאי את המספר!
   ========================================================================== */
function initMissingNumber() {
    document.getElementById('game-title').textContent = 'מצאי את המספר! 🔍';
    showMissingNumberRound();
}

function showMissingNumberRound() {
    if (state.currentRound >= state.totalRounds) { finishGame(); return; }
    state.answering = false;

    const problem = generateProblem();
    let displayEquation, missingValue;

    if (problem.category === 'division_verify' || problem.category === 'prime_composite') {
        // Already has ? — use the answer directly
        displayEquation = problem.display;
        missingValue = problem.answer;
    } else if (problem.category === 'prime_factorization') {
        // Already has _ — use the display and answer directly
        displayEquation = problem.display;
        missingValue = problem.answer;
    } else if (problem.category === 'divide_remainder') {
        // Show dividend as blank: ___ : 5 = 9 שארית 2
        const parts = problem.equation.split(' ');
        const dividend = parseInt(parts[0]);
        missingValue = dividend;
        displayEquation = `___ : ${parts[2]} = ${problem.answer} שארית ${problem.remainder}`;
    } else {
        // Standard blanking — pick a random number to hide
        const parts = problem.equation.split(' ');
        const numberIndices = [];
        parts.forEach((p, i) => { if (/^\d+$/.test(p) || /^\(\d+/.test(p)) numberIndices.push(i); });
        const blankIdx = numberIndices[Math.floor(Math.random() * numberIndices.length)] || 0;
        missingValue = parseInt(parts[blankIdx].replace(/[()]/g, ''));
        const displayParts = [...parts];
        const hasOpenParen = parts[blankIdx].startsWith('(');
        const hasCloseParen = parts[blankIdx].endsWith(')');
        displayParts[blankIdx] = (hasOpenParen ? '(' : '') + '___' + (hasCloseParen ? ')' : '');
        displayEquation = displayParts.join(' ') + ' = ' + problem.answer;
    }

    const distractors = generateDistractors(missingValue, 3);
    const options = shuffle([missingValue, ...distractors]);

    const content = document.getElementById('game-content');
    content.innerHTML = `
        <div class="question-area pop-in">
            <div class="equation-display">${displayEquation}</div>
            ${renderHintBtn(problem.hint)}
        </div>
        <div class="answer-grid">
            ${options.map((opt, i) => `
                <button class="answer-btn" onclick="checkMissingNumber(this, ${opt}, ${missingValue})" style="animation: popIn 0.3s ease-out ${i * 0.08}s both">
                    ${opt}
                </button>
            `).join('')}
        </div>
    `;
    state._currentProblem = problem;
    state._missingValue = missingValue;
    updateProgress();
}

function checkMissingNumber(btn, selected, correct) {
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
            if (parseInt(b.textContent) === correct) b.classList.add('show-correct');
        });
    }

    state.wordResults.push({
        word: state._currentProblem.equation,
        correct: selected === correct,
        category: state._currentProblem.category,
    });

    state.currentRound++;
    setTimeout(() => showMissingNumberRound(), 1500);
}

/* ==========================================================================
   GAME 3: TRUE OR FALSE MATH — נכון או לא?
   ========================================================================== */
function initTrueFalseMath() {
    document.getElementById('game-title').textContent = 'נכון או לא? ✅';
    showTrueFalseMathRound();
}

function showTrueFalseMathRound() {
    if (state.currentRound >= state.totalRounds) { finishGame(); return; }
    state.answering = false;

    const problem = generateTFProblem();

    const content = document.getElementById('game-content');
    content.innerHTML = `
        <div class="question-area pop-in">
            <div class="tf-card">
                <div class="equation-display">${problem.display}</div>
            </div>
            ${renderHintBtn(problem.hint)}
        </div>
        <div class="tf-buttons">
            <button class="tf-btn yes" onclick="checkTrueFalseMath(this, true, ${problem.isTrue})">✅ נכון</button>
            <button class="tf-btn no" onclick="checkTrueFalseMath(this, false, ${problem.isTrue})">❌ לא נכון</button>
        </div>
        <div id="tf-feedback" style="margin-top: var(--space-md); text-align: center;"></div>
    `;
    state._currentTFProblem = problem;
    updateProgress();
}

function checkTrueFalseMath(btn, selected, correct) {
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
        buttons.forEach(b => {
            const isYes = b.classList.contains('yes');
            if ((correct && isYes) || (!correct && !isYes)) b.classList.add('correct');
        });
        // Show the correct equation
        const feedback = document.getElementById('tf-feedback');
        feedback.innerHTML = `<div style="font-family: var(--font-display); color: var(--green-dark); background: #dcfce7; padding: var(--space-md); border-radius: var(--radius-md); direction: ltr;">${state._currentTFProblem.correctDisplay}</div>`;
    }

    state.wordResults.push({
        word: state._currentTFProblem.display,
        correct: selected === correct,
        category: 'true_false_math',
    });

    state.currentRound++;
    setTimeout(() => showTrueFalseMathRound(), 1500);
}

/* ==========================================================================
   GAME 4: BUBBLE POP — פוצצי בועות!
   ========================================================================== */
function initBubblePop() {
    document.getElementById('game-title').textContent = 'פוצצי בועות! 🫧';
    showBubblePopRound();
}

function showBubblePopRound() {
    if (state.currentRound >= state.totalRounds) { finishGame(); return; }
    state.answering = false;

    // Generate a target number — session-aware, keep friendly for 4th grade
    const BUBBLE_TARGETS = {
        'math-tens-hundreds': [10, 12, 15, 18, 20, 24, 30, 36, 40, 50, 60, 80, 90, 100],
        'math-two-digit': [44, 48, 56, 60, 72, 84, 90, 96, 108, 120, 132, 144, 150, 180],
        'math-long-division': [6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 21, 24],
        'math-primes': [6, 9, 10, 12, 15, 18, 20, 24, 25, 30, 36, 42, 45, 50],
    };
    const targets = BUBBLE_TARGETS[SESSION_SLUG] || BUBBLE_TARGETS['math-tens-hundreds'];
    const target = targets[Math.floor(Math.random() * targets.length)];

    // Generate 2-3 correct expressions
    const correctCount = 2 + Math.floor(Math.random() * 2); // 2 or 3
    const correctExpressions = generateExpressionsForTarget(target, correctCount);

    // Generate 3-4 wrong expressions
    const wrongCount = 6 - correctExpressions.length;
    const wrongExpressions = generateWrongExpressions(target, wrongCount);

    const allBubbles = shuffle([
        ...correctExpressions.map(e => ({ ...e, isCorrect: true })),
        ...wrongExpressions.map(e => ({ ...e, isCorrect: false })),
    ]);

    state.bubblesCorrectThisRound = 0;
    state.bubblesTargetThisRound = correctExpressions.length;

    const content = document.getElementById('game-content');
    content.innerHTML = `
        <div class="question-area pop-in">
            <div class="bubble-target">מצאי את התרגילים ששווים</div>
            <div class="bubble-target-number">${target}</div>
        </div>
        <div class="bubble-container">
            ${allBubbles.map((b, i) => `
                <button class="bubble bubble-${(i % 6) + 1}" data-correct="${b.isCorrect}" data-expr="${b.expression}" onclick="popBubble(this)" style="animation-delay: ${i * 0.15}s; animation: popIn 0.4s ease-out ${i * 0.1}s both, float 3s ease-in-out ${i * 0.3}s infinite;">
                    ${b.expression}
                </button>
            `).join('')}
        </div>
        <div class="bubble-round-info" id="bubble-info">0 / ${correctExpressions.length} נמצאו</div>
    `;
    updateProgress();
}

function generateExpressionsForTarget(target, count) {
    const expressions = new Set();
    const results = [];
    const isChapterB = SESSION_SLUG === 'math-two-digit';

    // Multiplication: a × b = target — for Chapter B prefer 2-digit factors
    const maxA = isChapterB ? Math.min(target, 50) : Math.min(target, 20);
    const minA = isChapterB ? 2 : 2;
    for (let a = minA; a <= maxA; a++) {
        if (target % a === 0) {
            const b = target / a;
            if (b >= 2 && b <= 100) {
                const expr = `${a} × ${b}`;
                if (!expressions.has(expr)) {
                    expressions.add(expr);
                    results.push({ expression: expr, value: target });
                }
            }
        }
        if (results.length >= count * 3) break;
    }

    // Powers: if target is a perfect square, add base² expression
    if (isChapterB) {
        const sqrt = Math.round(Math.sqrt(target));
        if (sqrt * sqrt === target && sqrt >= 2 && sqrt <= 12) {
            const expr = `${sqrt}²`;
            if (!expressions.has(expr)) {
                expressions.add(expr);
                results.push({ expression: expr, value: target });
            }
        }
    }

    // Division: a : b = target → a = target × b
    const maxDividend = isChapterB ? 2000 : 500;
    for (let b = 2; b <= 9; b++) {
        const a = target * b;
        if (a <= maxDividend) {
            const expr = `${a} : ${b}`;
            if (!expressions.has(expr)) {
                expressions.add(expr);
                results.push({ expression: expr, value: target });
            }
        }
        if (results.length >= count * 3) break;
    }

    shuffle(results);
    return results.slice(0, count);
}

function generateWrongExpressions(target, count) {
    const results = [];
    const isChapterB = SESSION_SLUG === 'math-two-digit';
    const offsets = isChapterB
        ? [2, -2, 4, -4, 6, -6, 10, -10, 12, -12]
        : [1, -1, 2, -2, 5, -5, 10, -10];

    for (let i = 0; i < count; i++) {
        const wrongTarget = target + offsets[i % offsets.length];
        if (wrongTarget <= 0) continue;
        const maxA = isChapterB ? 50 : 15;
        for (let a = 2; a <= maxA; a++) {
            if (wrongTarget % a === 0) {
                const b = wrongTarget / a;
                if (b >= 2 && b <= 100) {
                    results.push({ expression: `${a} × ${b}`, value: wrongTarget });
                    break;
                }
            }
        }
    }

    // Fill if needed with divisions
    const maxDividend = isChapterB ? 2000 : 500;
    while (results.length < count) {
        const range = isChapterB ? 15 : 5;
        const wrongTarget = target + (Math.floor(Math.random() * range * 2) - range);
        if (wrongTarget > 0 && wrongTarget !== target) {
            const b = 2 + Math.floor(Math.random() * 7);
            const a = wrongTarget * b;
            if (a <= maxDividend) {
                results.push({ expression: `${a} : ${b}`, value: wrongTarget });
            }
        }
    }

    return results.slice(0, count);
}

function popBubble(bubble) {
    if (state.answering || bubble.classList.contains('popped')) return;

    const isCorrect = bubble.dataset.correct === 'true';

    if (isCorrect) {
        bubble.classList.add('correct');
        playCorrect();
        state.bubblesCorrectThisRound++;
        awardStar(1);
        document.getElementById('mascot').classList.add('wiggle');
        setTimeout(() => document.getElementById('mascot').classList.remove('wiggle'), 600);

        setTimeout(() => bubble.classList.add('popped'), 400);

        // Update info
        document.getElementById('bubble-info').textContent = `${state.bubblesCorrectThisRound} / ${state.bubblesTargetThisRound} נמצאו`;

        state.wordResults.push({
            word: bubble.dataset.expr,
            correct: true,
            category: 'bubble_pop',
        });

        // Check if all correct bubbles found
        if (state.bubblesCorrectThisRound >= state.bubblesTargetThisRound) {
            state.answering = true;
            document.querySelectorAll('.bubble').forEach(b => b.classList.add('disabled'));
            spawnConfetti();
            state.currentRound++;
            setTimeout(() => showBubblePopRound(), 1500);
        }
    } else {
        bubble.classList.add('wrong');
        playWrong();
        state.wordResults.push({
            word: bubble.dataset.expr,
            correct: false,
            category: 'bubble_pop',
        });
        setTimeout(() => bubble.classList.remove('wrong'), 500);
    }
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
    const max = state.totalRounds * STARS_PER_CORRECT[state.currentGame];

    state.sessionGames.add(state.currentGame);
    localStorage.setItem('ariel_math_session_games', JSON.stringify([...state.sessionGames]));
    state.sessionStars += state.gameScore;
    const completedCard = document.getElementById(`game-card-${state.currentGame}`);
    if (completedCard) completedCard.classList.add('completed');

    document.getElementById('complete-score').textContent = `${state.gameScore} / ${max} ⭐ הרווחת`;
    document.getElementById('complete-total-stars').textContent = `⭐ ${state.totalStars} :סה"כ כוכבים`;

    const gameType = GAME_TYPE_MAP[state.currentGame];
    if (gameType) {
        saveGameResult(gameType, state.gameScore, max, state.wordResults);
    }

    const replayBtn = document.getElementById('replay-btn');
    const gameNum = state.currentGame;
    replayBtn.onclick = () => startGame(gameNum);

    showScreen('complete-screen');
    spawnConfetti();
    playCelebration();

    if (state.sessionGames.size === 4) {
        setTimeout(() => showSessionPopup(), 2500);
    }
}
