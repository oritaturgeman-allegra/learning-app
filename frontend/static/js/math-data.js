/**
 * math-data.js — Math config constants and hint data.
 * Loaded after shared.js; before math-game.js.
 */

/** Map game number → API game_type string */
const GAME_TYPE_MAP = {
    1: 'quick_solve',
    2: 'missing_number',
    3: 'true_false_math',
    4: 'bubble_pop',
};

/** Stars per correct answer by game */
const STARS_PER_CORRECT = { 1: 1, 2: 1, 3: 1, 4: 1 };

/** Rounds per game */
const ROUNDS_PER_GAME = { 1: 10, 2: 8, 3: 10, 4: 8 };

/* ==========================================================================
   PROBLEM GENERATOR — session-aware (picks categories by SESSION_SLUG)
   ========================================================================== */

const CATEGORIES_BY_SESSION = {
    'math-tens-hundreds': [
        'multiply_tens', 'multiply_hundreds', 'divide_single',
        'divide_tens', 'properties_0_1', 'order_of_operations',
    ],
    'math-two-digit': [
        'two_digit_x_one_digit', 'two_digit_x_two_digit', 'powers',
    ],
    'math-long-division': [
        'divide_remainder', 'long_division', 'division_verify',
    ],
    'math-primes': [
        'divisibility_rules', 'prime_composite', 'prime_factorization',
    ],
};

/* ---------- MATH HINTS — natural Hebrew, organized by category ---------- */
const MATH_HINTS = {
    /* Chapter A: Tens & Hundreds */
    multiply_tens:      (base, factor) => `נסי ככה: כמה זה ${base / 10} × ${factor}? עכשיו תוסיפי 0 בסוף`,
    multiply_hundreds:  (factor) => `תחשבי רגע: כמה זה ${factor} × 1? תוסיפי שני אפסים בסוף`,
    divide_single:      (divisor, dividend) => `תשתמשי בלוח הכפל — מה כפול ${divisor} נותן ${dividend}?`,
    divide_tens:        (divisor, dividend) => divisor === 10
        ? `הטריק: תורידי את ה-0 מ-${dividend} ויש לך את התשובה`
        : `הטריק: תורידי שני אפסים מ-${dividend} ויש לך את התשובה`,
    properties_zero:    'זכרי: לא משנה מה המספר — כפול 0 זה תמיד 0!',
    properties_one:     'זכרי: כפול 1 — המספר נשאר בדיוק אותו דבר!',
    order_no_parens:    'זכרי: קודם כפל, אחר כך חיבור!',
    order_with_parens:  'זכרי: קודם פותרים את מה שבתוך הסוגריים!',

    /* Chapter B: Two-Digit Multiply */
    two_digit_x_one:    (tens, ones, b) => `נסי לפרק: קודם ${tens} × ${b}, ואז ${ones} × ${b}, ותחברי`,
    two_digit_x_two:    (b) => `נסי לפרק את ${b} לעשרות ואחדות, ותכפלי כל חלק בנפרד`,
    powers:             (base) => `חזקה זה כפל חוזר! ${base}² = ${base} × ${base}`,

    /* Chapter C: Long Division */
    divide_remainder:   (divisor, dividend) => `תשתמשי בלוח הכפל — מה הכי קרוב ל-${dividend} שמתחלק ב-${divisor}?`,
    long_division:      (divisor) => `תתחילי מהספרה השמאלית — כמה פעמים ${divisor} נכנס שם?`,
    division_verify_q:  (a, product) => `תחשבי: מה כפול ${a} שווה ${product}? נסי לחלק!`,
    division_verify_d:  (b, product) => `תחשבי: ${b} כפול מה שווה ${product}?`,

    /* Chapter D: Primes & Divisibility */
    divisibility_3:     (digits) => `הטריק: תחברי את הספרות ${digits.join('+')} ותבדקי אם הסכום מתחלק ב-3`,
    divisibility_9:     (digits) => `הטריק: תחברי את הספרות ${digits.join('+')} ותבדקי אם הסכום מתחלק ב-9`,
    divisibility_6:     'מתחלק ב-6? תבדקי שני דברים: שהמספר זוגי, ושסכום הספרות מתחלק ב-3',
    prime:              (p) => `שימי לב: ${p} לא מתחלק באף מספר חוץ מ-1 ומעצמו — ראשוני!`,
    composite:          (n, factor) => `נסי לחלק את ${n} ב-${factor} — כמה פעמים נכנס?`,
    prime_factorization:(firstFactor) => `תתחילי מהמספר הראשוני הכי קטן — נסי לחלק ב-${firstFactor}`,
    composite_tf:       (num, factor) => `שימי לב: ${num} מתחלק ב-${factor}, אז הוא לא ראשוני`,
};
