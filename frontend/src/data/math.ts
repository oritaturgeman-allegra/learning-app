/**
 * Math game data — problem generators, hints, categories, distractors.
 *
 * Ported from static/js/math-data.js + static/js/math-game.js.
 * All functions are pure (no side effects).
 */

import { shuffle } from "@/data/english";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface MathProblem {
  equation: string;
  answer: number;
  display: string;
  category: string;
  hint?: string;
  remainder?: number;
}

export interface TFProblem {
  display: string;
  isTrue: boolean;
  correctDisplay: string;
  hint?: string;
}

export interface BubbleItem {
  expression: string;
  value: number;
  isCorrect: boolean;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Map game number → API game_type string */
export const MATH_GAME_TYPE_MAP: Record<number, string> = {
  1: "quick_solve",
  2: "missing_number",
  3: "true_false_math",
  4: "bubble_pop",
};

/** Rounds per game */
export const ROUNDS_PER_GAME: Record<number, number> = {
  1: 10,
  2: 8,
  3: 10,
  4: 8,
};

/** Categories by session slug */
export const CATEGORIES_BY_SESSION: Record<string, string[]> = {
  "math-tens-hundreds": [
    "multiply_tens",
    "multiply_hundreds",
    "divide_single",
    "divide_tens",
    "properties_0_1",
    "order_of_operations",
  ],
  "math-two-digit": [
    "two_digit_x_one_digit",
    "two_digit_x_two_digit",
    "powers",
  ],
  "math-long-division": [
    "divide_remainder",
    "long_division",
    "division_verify",
  ],
  "math-primes": [
    "divisibility_rules",
    "prime_composite",
    "prime_factorization",
  ],
};

/** Bubble pop target numbers by session */
const BUBBLE_TARGETS: Record<string, number[]> = {
  "math-tens-hundreds": [10, 12, 15, 18, 20, 24, 30, 36, 40, 50, 60, 80, 90, 100],
  "math-two-digit": [44, 48, 56, 60, 72, 84, 90, 96, 108, 120, 132, 144, 150, 180],
  "math-long-division": [6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 21, 24],
  "math-primes": [6, 9, 10, 12, 15, 18, 20, 24, 25, 30, 36, 42, 45, 50],
};

// ---------------------------------------------------------------------------
// Hints — Hebrew, organized by category
// ---------------------------------------------------------------------------

function hintMultiplyTens(base: number, factor: number): string {
  return `נסי ככה: כמה זה ${base / 10} × ${factor}? עכשיו תוסיפי 0 בסוף`;
}
function hintMultiplyHundreds(factor: number): string {
  return `תחשבי רגע: כמה זה ${factor} × 1? תוסיפי שני אפסים בסוף`;
}
function hintDivideSingle(divisor: number, dividend: number): string {
  return `תשתמשי בלוח הכפל — מה כפול ${divisor} נותן ${dividend}?`;
}
function hintDivideTens(divisor: number, dividend: number): string {
  return divisor === 10
    ? `הטריק: תורידי את ה-0 מ-${dividend} ויש לך את התשובה`
    : `הטריק: תורידי שני אפסים מ-${dividend} ויש לך את התשובה`;
}
const HINT_PROPERTIES_ZERO = "זכרי: לא משנה מה המספר — כפול 0 זה תמיד 0!";
const HINT_PROPERTIES_ONE = "זכרי: כפול 1 — המספר נשאר בדיוק אותו דבר!";
const HINT_ORDER_NO_PARENS = "זכרי: קודם כפל, אחר כך חיבור!";
const HINT_ORDER_WITH_PARENS = "זכרי: קודם פותרים את מה שבתוך הסוגריים!";

function hintTwoDigitXOne(tens: number, ones: number, b: number): string {
  return `נסי לפרק: קודם ${tens} × ${b}, ואז ${ones} × ${b}, ותחברי`;
}
function hintTwoDigitXTwo(b: number): string {
  return `נסי לפרק את ${b} לעשרות ואחדות, ותכפלי כל חלק בנפרד`;
}
function hintPowers(base: number): string {
  return `חזקה זה כפל חוזר! ${base}² = ${base} × ${base}`;
}

function hintDivideRemainder(divisor: number, dividend: number): string {
  return `תשתמשי בלוח הכפל — מה הכי קרוב ל-${dividend} שמתחלק ב-${divisor}?`;
}
function hintLongDivision(divisor: number): string {
  return `תתחילי מהספרה השמאלית — כמה פעמים ${divisor} נכנס שם?`;
}
function hintDivisionVerifyQ(a: number, product: number): string {
  return `תחשבי: מה כפול ${a} שווה ${product}? נסי לחלק!`;
}
function hintDivisionVerifyD(b: number, product: number): string {
  return `תחשבי: ${b} כפול מה שווה ${product}?`;
}

function hintDivisibility3(digits: number[]): string {
  return `הטריק: תחברי את הספרות ${digits.join("+")} ותבדקי אם הסכום מתחלק ב-3`;
}
function hintDivisibility9(digits: number[]): string {
  return `הטריק: תחברי את הספרות ${digits.join("+")} ותבדקי אם הסכום מתחלק ב-9`;
}
const HINT_DIVISIBILITY_6 =
  "מתחלק ב-6? תבדקי שני דברים: שהמספר זוגי, ושסכום הספרות מתחלק ב-3";
function hintPrime(p: number): string {
  return `שימי לב: ${p} לא מתחלק באף מספר חוץ מ-1 ומעצמו — ראשוני!`;
}
function hintComposite(n: number, factor: number): string {
  return `נסי לחלק את ${n} ב-${factor} — כמה פעמים נכנס?`;
}
function hintCompositeTF(num: number, factor: number): string {
  return `שימי לב: ${num} מתחלק ב-${factor}, אז הוא לא ראשוני`;
}
function hintPrimeFactorization(firstFactor: number): string {
  return `תתחילי מהמספר הראשוני הכי קטן — נסי לחלק ב-${firstFactor}`;
}

// ---------------------------------------------------------------------------
// Problem generators — exact port from math-game.js
// ---------------------------------------------------------------------------

const TENS = [10, 20, 30, 40, 50, 60, 70, 80, 90];
const FRIENDLY_NUMS = [5, 8, 12, 17, 20, 25, 30, 42, 50, 64, 75, 88, 100];
const PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47];
const PRIMES_SET = new Set(PRIMES);
const COMPOSITES = [
  4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30,
  32, 33, 34, 35, 36, 38, 39, 40, 42, 44, 45, 46, 48, 49, 50,
];
const ALL_NUMS_2_50 = Array.from({ length: 49 }, (_, i) => i + 2);
const FACTORIZATIONS: { n: number; factors: number[] }[] = [
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

function randInt(min: number, max: number): number {
  return min + Math.floor(Math.random() * (max - min + 1));
}

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]!;
}

/** Generate a math problem for the given session. */
export function generateProblem(sessionSlug: string): MathProblem {
  const categories =
    CATEGORIES_BY_SESSION[sessionSlug] ??
    CATEGORIES_BY_SESSION["math-tens-hundreds"]!;
  const cat = pick(categories);
  return generateProblemByCategory(cat);
}

/** Generate a problem for a specific category. */
export function generateProblemByCategory(category: string): MathProblem {
  switch (category) {
    case "multiply_tens": {
      const base = pick(TENS);
      const factor = randInt(2, 8);
      const answer = base * factor;
      return {
        equation: `${base} × ${factor}`,
        answer,
        display: `${base} × ${factor} = ?`,
        category,
        hint: hintMultiplyTens(base, factor),
      };
    }
    case "multiply_hundreds": {
      const factor = randInt(2, 9);
      const answer = factor * 100;
      return {
        equation: `${factor} × 100`,
        answer,
        display: `${factor} × 100 = ?`,
        category,
        hint: hintMultiplyHundreds(factor),
      };
    }
    case "divide_single": {
      const divisor = randInt(2, 9);
      const quotient = pick([10, 20, 30, 40, 50]);
      const dividend = divisor * quotient;
      return {
        equation: `${dividend} : ${divisor}`,
        answer: quotient,
        display: `${dividend} : ${divisor} = ?`,
        category,
        hint: hintDivideSingle(divisor, dividend),
      };
    }
    case "divide_tens": {
      const divisor = pick([10, 100]);
      const quotient = randInt(2, 8) * (divisor === 10 ? 10 : 1);
      const dividend = divisor * quotient;
      return {
        equation: `${dividend} : ${divisor}`,
        answer: quotient,
        display: `${dividend} : ${divisor} = ?`,
        category,
        hint: hintDivideTens(divisor, dividend),
      };
    }
    case "properties_0_1": {
      const n = pick(FRIENDLY_NUMS);
      const variant = randInt(0, 3);
      if (variant === 0)
        return {
          equation: `0 × ${n}`,
          answer: 0,
          display: `0 × ${n} = ?`,
          category,
          hint: HINT_PROPERTIES_ZERO,
        };
      if (variant === 1)
        return {
          equation: `${n} × 0`,
          answer: 0,
          display: `${n} × 0 = ?`,
          category,
          hint: HINT_PROPERTIES_ZERO,
        };
      if (variant === 2)
        return {
          equation: `1 × ${n}`,
          answer: n,
          display: `1 × ${n} = ?`,
          category,
          hint: HINT_PROPERTIES_ONE,
        };
      return {
        equation: `${n} × 1`,
        answer: n,
        display: `${n} × 1 = ?`,
        category,
        hint: HINT_PROPERTIES_ONE,
      };
    }
    case "order_of_operations": {
      const a = randInt(2, 7);
      const b = randInt(2, 7);
      const c = randInt(2, 5);
      if (Math.random() < 0.5) {
        const answer = a + b * c;
        return {
          equation: `${a} + ${b} × ${c}`,
          answer,
          display: `${a} + ${b} × ${c} = ?`,
          category,
          hint: HINT_ORDER_NO_PARENS,
        };
      }
      const answer = (a + b) * c;
      return {
        equation: `(${a} + ${b}) × ${c}`,
        answer,
        display: `(${a} + ${b}) × ${c} = ?`,
        category,
        hint: HINT_ORDER_WITH_PARENS,
      };
    }
    case "two_digit_x_one_digit": {
      const a = randInt(11, 99);
      const b = randInt(2, 9);
      if (a * b > 500) return generateProblemByCategory(category);
      const answer = a * b;
      const tens = Math.floor(a / 10) * 10;
      const ones = a % 10;
      return {
        equation: `${a} × ${b}`,
        answer,
        display: `${a} × ${b} = ?`,
        category,
        hint: hintTwoDigitXOne(tens, ones, b),
      };
    }
    case "two_digit_x_two_digit": {
      const a = randInt(11, 49);
      const b = randInt(11, 49);
      if (a * b > 2000) return generateProblemByCategory(category);
      const answer = a * b;
      return {
        equation: `${a} × ${b}`,
        answer,
        display: `${a} × ${b} = ?`,
        category,
        hint: hintTwoDigitXTwo(b),
      };
    }
    case "powers": {
      const base = randInt(2, 12);
      const answer = base * base;
      return {
        equation: `${base}²`,
        answer,
        display: `${base}² = ?`,
        category,
        hint: hintPowers(base),
      };
    }
    case "divide_remainder": {
      const divisor = randInt(2, 9);
      const quotient = randInt(3, 17);
      const remainder = randInt(1, divisor - 1);
      const dividend = divisor * quotient + remainder;
      if (dividend > 99) return generateProblemByCategory(category);
      return {
        equation: `${dividend} : ${divisor}`,
        answer: quotient,
        remainder,
        display: `${dividend} : ${divisor} = ?`,
        category,
        hint: hintDivideRemainder(divisor, dividend),
      };
    }
    case "long_division": {
      const divisor = randInt(2, 9);
      const quotient = randInt(11, 100);
      const dividend = divisor * quotient;
      if (dividend > 999) return generateProblemByCategory(category);
      return {
        equation: `${dividend} : ${divisor}`,
        answer: quotient,
        display: `${dividend} : ${divisor} = ?`,
        category,
        hint: hintLongDivision(divisor),
      };
    }
    case "division_verify": {
      const a = randInt(2, 9);
      const b = randInt(3, 17);
      const product = a * b;
      if (Math.random() < 0.5) {
        return {
          equation: `? × ${a} = ${product}`,
          answer: b,
          display: `? × ${a} = ${product}`,
          category,
          hint: hintDivisionVerifyQ(a, product),
        };
      }
      return {
        equation: `${product} : ? = ${b}`,
        answer: a,
        display: `${product} : ? = ${b}`,
        category,
        hint: hintDivisionVerifyD(b, product),
      };
    }
    case "divisibility_rules": {
      const divisor = pick([3, 6, 9]);
      const quotient = randInt(4, 33);
      const dividend = divisor * quotient;
      if (dividend > 200) return generateProblemByCategory(category);
      const digits = String(dividend).split("").map(Number);
      let hint: string;
      if (divisor === 3) hint = hintDivisibility3(digits);
      else if (divisor === 9) hint = hintDivisibility9(digits);
      else hint = HINT_DIVISIBILITY_6;
      return {
        equation: `${dividend} : ${divisor}`,
        answer: quotient,
        display: `${dividend} : ${divisor} = ?`,
        category,
        hint,
      };
    }
    case "prime_composite": {
      if (Math.random() < 0.4) {
        const p = pick(PRIMES);
        return {
          equation: `1 × ? = ${p}`,
          answer: p,
          display: `1 × ? = ${p}`,
          category,
          hint: hintPrime(p),
        };
      }
      const n = pick(COMPOSITES);
      let smallestFactor = 2;
      for (let f = 2; f <= n; f++) {
        if (n % f === 0) {
          smallestFactor = f;
          break;
        }
      }
      const other = n / smallestFactor;
      return {
        equation: `? × ${smallestFactor} = ${n}`,
        answer: other,
        display: `? × ${smallestFactor} = ${n}`,
        category,
        hint: hintComposite(n, smallestFactor),
      };
    }
    case "prime_factorization": {
      const entry = pick(FACTORIZATIONS);
      const blankIdx = Math.floor(Math.random() * entry.factors.length);
      const answer = entry.factors[blankIdx]!;
      const displayFactors = entry.factors.map((f, i) =>
        i === blankIdx ? "_" : String(f),
      );
      return {
        equation: `${entry.n} = ${entry.factors.join(" × ")}`,
        answer,
        display: `${entry.n} = ${displayFactors.join(" × ")}`,
        category,
        hint: hintPrimeFactorization(entry.factors[0]!),
      };
    }
    default:
      return generateProblemByCategory("multiply_tens");
  }
}

// ---------------------------------------------------------------------------
// Distractors
// ---------------------------------------------------------------------------

/** Generate plausible wrong answers close to the correct one. */
export function generateDistractors(
  correctAnswer: number,
  count: number,
): number[] {
  const distractors = new Set<number>();
  const small = correctAnswer <= 20;
  const offsets = small
    ? [1, -1, 2, -2, 3, -3, 5, -5]
    : [5, -5, 10, -10, 20, -20, 50, -50];

  // Shuffle offsets
  for (let i = offsets.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [offsets[i], offsets[j]] = [offsets[j]!, offsets[i]!];
  }

  for (const offset of offsets) {
    if (distractors.size >= count) break;
    const d = correctAnswer + offset;
    if (d !== correctAnswer && d > 0) distractors.add(d);
  }

  // Fill remaining
  const range = small ? 5 : 30;
  while (distractors.size < count) {
    const d =
      correctAnswer + Math.floor(Math.random() * range * 2) - range;
    if (d !== correctAnswer && d > 0) distractors.add(d);
  }

  return [...distractors].slice(0, count);
}

// ---------------------------------------------------------------------------
// True/False problem generator
// ---------------------------------------------------------------------------

/** Generate a True/False math problem. */
export function generateTFProblem(sessionSlug: string): TFProblem {
  const problem = generateProblem(sessionSlug);
  const isTrue = Math.random() < 0.5;

  // Special: prime_composite — "13 — מספר ראשוני"
  if (problem.category === "prime_composite") {
    const num = pick(ALL_NUMS_2_50);
    const actuallyPrime = PRIMES_SET.has(num);
    if (isTrue) {
      const label = actuallyPrime ? "מספר ראשוני" : "מספר פריק";
      const str = `${num} — ${label}`;
      return { display: str, isTrue: true, correctDisplay: str, hint: problem.hint };
    }
    const wrongLabel = actuallyPrime ? "מספר פריק" : "מספר ראשוני";
    const correctLabel = actuallyPrime ? "מספר ראשוני" : "מספר פריק";
    return {
      display: `${num} — ${wrongLabel}`,
      isTrue: false,
      correctDisplay: `${num} — ${correctLabel}`,
      hint: actuallyPrime
        ? hintPrime(num)
        : hintCompositeTF(num, [2, 3, 5, 7].find((f) => num % f === 0) ?? 2),
    };
  }

  // Special: prime_factorization — "36 = 2 × 2 × 3 × 3"
  if (problem.category === "prime_factorization") {
    const correctStr = problem.equation;
    if (isTrue) {
      return { display: correctStr, isTrue: true, correctDisplay: correctStr, hint: problem.hint };
    }
    const parts = correctStr.split(" = ");
    const factors = parts[1]!.split(" × ").map(Number);
    const swapIdx = Math.floor(Math.random() * factors.length);
    const orig = factors[swapIdx]!;
    factors[swapIdx] =
      orig === 2 ? 3 : orig === 3 ? 2 : orig === 5 ? 3 : orig === 7 ? 5 : 2;
    const wrongStr = `${parts[0]} = ${factors.join(" × ")}`;
    return { display: wrongStr, isTrue: false, correctDisplay: correctStr, hint: problem.hint };
  }

  // Standard: equation = answer (correct or wrong)
  const hasRemainder = problem.remainder !== undefined;
  const correctStr = hasRemainder
    ? `${problem.equation} = ${problem.answer} שארית ${problem.remainder}`
    : `${problem.equation} = ${problem.answer}`;

  if (isTrue) {
    return { display: correctStr, isTrue: true, correctDisplay: correctStr, hint: problem.hint };
  }

  if (hasRemainder) {
    const wrongR = problem.remainder! + (Math.random() < 0.5 ? 1 : -1);
    const wrongQ = problem.answer + (Math.random() < 0.5 ? 1 : -1);
    const wrongStr =
      Math.random() < 0.5
        ? `${problem.equation} = ${problem.answer} שארית ${Math.max(0, wrongR)}`
        : `${problem.equation} = ${wrongQ} שארית ${problem.remainder}`;
    return { display: wrongStr, isTrue: false, correctDisplay: correctStr, hint: problem.hint };
  }

  const wrongAnswer = generateDistractors(problem.answer, 1)[0]!;
  return {
    display: `${problem.equation} = ${wrongAnswer}`,
    isTrue: false,
    correctDisplay: correctStr,
    hint: problem.hint,
  };
}

// ---------------------------------------------------------------------------
// Missing number helpers
// ---------------------------------------------------------------------------

export interface MissingNumberProblem {
  displayEquation: string;
  missingValue: number;
  hint?: string;
  originalProblem: MathProblem;
}

/** Generate a missing-number variant from a math problem. */
export function generateMissingNumberProblem(
  sessionSlug: string,
): MissingNumberProblem {
  const problem = generateProblem(sessionSlug);

  // Categories that already have ? or _
  if (
    problem.category === "division_verify" ||
    problem.category === "prime_composite"
  ) {
    return {
      displayEquation: problem.display,
      missingValue: problem.answer,
      hint: problem.hint,
      originalProblem: problem,
    };
  }

  if (problem.category === "prime_factorization") {
    return {
      displayEquation: problem.display,
      missingValue: problem.answer,
      hint: problem.hint,
      originalProblem: problem,
    };
  }

  if (problem.category === "divide_remainder") {
    const parts = problem.equation.split(" ");
    const dividend = parseInt(parts[0]!);
    return {
      displayEquation: `___ : ${parts[2]} = ${problem.answer} שארית ${problem.remainder}`,
      missingValue: dividend,
      hint: problem.hint,
      originalProblem: problem,
    };
  }

  // Default: blank a random number
  const parts = problem.equation.split(" ");
  const numberIndices: number[] = [];
  parts.forEach((p, i) => {
    if (/^\d+$/.test(p) || /^\(\d+/.test(p)) numberIndices.push(i);
  });
  const blankIdx = numberIndices.length > 0
    ? pick(numberIndices)
    : 0;
  const missingValue = parseInt(parts[blankIdx]!.replace(/[()]/g, ""));
  const displayParts = [...parts];
  const hasOpenParen = parts[blankIdx]!.startsWith("(");
  const hasCloseParen = parts[blankIdx]!.endsWith(")");
  displayParts[blankIdx] =
    (hasOpenParen ? "(" : "") + "___" + (hasCloseParen ? ")" : "");
  const displayEquation = displayParts.join(" ") + " = " + problem.answer;

  return {
    displayEquation,
    missingValue,
    hint: problem.hint,
    originalProblem: problem,
  };
}

// ---------------------------------------------------------------------------
// Bubble Pop expression generators
// ---------------------------------------------------------------------------

/** Generate correct expressions that equal the target. */
export function generateExpressionsForTarget(
  target: number,
  count: number,
  sessionSlug: string,
): { expression: string; value: number }[] {
  const expressions = new Set<string>();
  const results: { expression: string; value: number }[] = [];
  const isChapterB = sessionSlug === "math-two-digit";

  // Multiplication: a × b = target
  const maxA = isChapterB ? Math.min(target, 50) : Math.min(target, 20);
  for (let a = 2; a <= maxA; a++) {
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

  // Powers: perfect square
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

  // Division: a : b = target
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

  return shuffle(results).slice(0, count);
}

/** Generate wrong expressions (close but not equal to target). */
export function generateWrongExpressions(
  target: number,
  count: number,
  sessionSlug: string,
): { expression: string; value: number }[] {
  const results: { expression: string; value: number }[] = [];
  const isChapterB = sessionSlug === "math-two-digit";
  const offsets = isChapterB
    ? [2, -2, 4, -4, 6, -6, 10, -10, 12, -12]
    : [1, -1, 2, -2, 5, -5, 10, -10];

  for (let i = 0; i < count; i++) {
    const wrongTarget = target + offsets[i % offsets.length]!;
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

  // Fill with divisions
  const maxDividend = isChapterB ? 2000 : 500;
  while (results.length < count) {
    const range = isChapterB ? 15 : 5;
    const wrongTarget =
      target + Math.floor(Math.random() * range * 2) - range;
    if (wrongTarget > 0 && wrongTarget !== target) {
      const b = randInt(2, 8);
      const a = wrongTarget * b;
      if (a <= maxDividend) {
        results.push({ expression: `${a} : ${b}`, value: wrongTarget });
      }
    }
  }

  return results.slice(0, count);
}

/** Generate all bubbles for a round (correct + wrong, shuffled). */
export function generateBubbles(sessionSlug: string): {
  target: number;
  bubbles: BubbleItem[];
  correctCount: number;
} {
  const targets =
    BUBBLE_TARGETS[sessionSlug] ?? BUBBLE_TARGETS["math-tens-hundreds"]!;
  const target = pick(targets);

  const correctCount = randInt(2, 3);
  const correctExpressions = generateExpressionsForTarget(
    target,
    correctCount,
    sessionSlug,
  );
  const wrongCount = 6 - correctExpressions.length;
  const wrongExpressions = generateWrongExpressions(
    target,
    wrongCount,
    sessionSlug,
  );

  const bubbles = shuffle([
    ...correctExpressions.map((e) => ({ ...e, isCorrect: true })),
    ...wrongExpressions.map((e) => ({ ...e, isCorrect: false })),
  ]);

  return { target, bubbles, correctCount: correctExpressions.length };
}
