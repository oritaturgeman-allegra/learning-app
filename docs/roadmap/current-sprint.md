# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
**Math Section Launch** — Build the math game engine and ship Chapter A (כפל וחילוק בעשרות ובמאות) as the first playable math session.

## Sprint Theme
Subject Expansion — Transform the app from English-only to a multi-subject learning platform with math games tailored to Ariel's 4th-grade syllabus.

---

## Math Section Architecture

### Session Cards (4 chapters → 4 session cards under Math)

Based on Ariel's math textbook table of contents:

| # | Session Card | Hebrew Name | Slug | Topics Covered |
|---|-------------|-------------|------|----------------|
| 1 | **Tens & Hundreds** | כפל וחילוק בעשרות ובמאות | `math-tens-hundreds` | ×10/100/1000, ÷ by single digit, order of operations, properties of 0 and 1 |
| 2 | **Two-Digit Multiply** | כפל דו-ספרתי | `math-two-digit` | Multiply by 2-digit numbers, vertical multiplication, powers |
| 3 | **Long Division** | חילוק ארוך | `math-long-division` | Division by single digit, long division |
| 4 | **Primes & Divisibility** | מספרים ראשוניים | `math-primes` | Divisibility rules (3, 6, 9), prime/composite numbers, prime factorization |

**Build order:** Card 1 first (foundational) → unlock cards 2-4 progressively.
Cards 2-4 launch as locked (coming soon) like the old multiply-divide card.

### 4 Math Game Types (per session)

Each session card has 4 mini-games, same pattern as English:

| # | Game | Hebrew Name | How It Works | Stars |
|---|------|-------------|-------------|-------|
| 1 | **Quick Solve** | פתרי מהר! | Multiple choice — equation + 4 answers, pick the right one | 1/correct, 10 rounds |
| 2 | **Missing Number** | !מצאי את המספר | Fill-in-the-blank — equation with `_`, pick the missing number | 1/correct, 8 rounds |
| 3 | **True or False** | ?נכון או לא | Verify — complete equation shown, is it correct? | 1/correct, 10 rounds |
| 4 | **Bubble Pop** | !פוצצי בועות | Pop bubbles — target number shown, pop expressions that equal it | 1/bubble, 8 rounds |

### Key Design Decisions

**Problem generation:** Math problems are generated algorithmically per session (not a static word bank like English). Each session has a `generateProblem(type, difficulty)` function.

**Israeli math notation:**
- Multiplication: `×` (not `*`)
- Division: `:` (not `/`) — Israeli standard (e.g., `42 : 6 = 7`)
- Parentheses for order of operations: `(4 + 5) × 3`

**Difficulty within a session:** Problems get progressively harder within each game (easier facts first, harder ones later in the round). No explicit difficulty picker — adaptive based on the session's topic scope.

**Progress tracking:** Same `game_results` table with `session_slug`. Each math session card tracks its own stars. `word_results` repurposed as `problem_results`: `{word: "30×4", correct: true, category: "multiply_tens"}`.

**No word tracker for math:** Replace with a "topics mastered" or "accuracy by category" display in the future. Not in Sprint 2.

### Template Architecture

Math games need a **separate template** (`math-fun.html`) or a **shared game engine** in the existing template with subject-conditional rendering. Decision: **separate template** — math game UI is fundamentally different (no word tracker, different game screens, algorithmic problems vs static vocabulary).

---

## Sprint 1 Tasks

### 1. Math Architecture Setup
**Priority:** High | **Effort:** Small

- [x] Replace single `multiply-divide` session with 4 chapter-based sessions in `defaults.py`
- [x] Cards 2-4 marked as `locked: True`
- [x] Card 1 (`math-tens-hundreds`) is unlocked and clickable
- [x] Update `VALID_SESSION_SLUGS` to include new slugs
- [x] Session picker at `/learning/math` shows all 4 cards

### 2. Math Template + Game Engine
**Priority:** High | **Effort:** Large

- [ ] Create `frontend/templates/math-fun.html` (or extend existing template with math mode)
- [ ] Math game menu screen with 4 game cards (Quick Solve, Missing Number, T/F, Bubble Pop)
- [ ] Shared header (stars + trophy) consistent with English template
- [ ] Subject tabs for switching between English and Math
- [ ] Route `/learning/math/math-tens-hundreds` serves the math template

### 3. Problem Generator — Chapter A
**Priority:** High | **Effort:** Medium

- [ ] `generateProblem()` function for Chapter A topics:
  - Multiply by 10, 100, 1,000 (e.g., `7 × 100 = ?`)
  - Multiply by whole tens/hundreds (e.g., `30 × 4 = ?`, `200 × 5 = ?`)
  - Divide by single digit (e.g., `450 : 9 = ?`)
  - Divide by 10, 100, 1,000 (e.g., `3000 : 100 = ?`)
  - Connection multiply↔divide (e.g., `If 6 × 8 = 48, then 48 : 6 = ?`)
  - Order of operations (e.g., `3 + 4 × 5 = ?`, `(3 + 4) × 5 = ?`)
  - Properties of 0 and 1 (e.g., `0 × 847 = ?`, `1 × 56 = ?`)
- [ ] Distractor generator (near-miss wrong answers for multiple choice)
- [ ] Round planner — mix of topic categories per game session

### 4. Game 1 — Quick Solve (פתרי מהר!)
**Priority:** High | **Effort:** Medium

- [ ] Game screen: equation display + 4 answer buttons
- [ ] 10 rounds, 1 star per correct answer
- [ ] Correct/wrong animations + sound feedback (reuse existing)
- [ ] Save result to API with `session_slug: "math-tens-hundreds"`
- [ ] Hebrew game card on menu: פתרי מהר! with ⚡ emoji

### 5. Game 2 — Missing Number (מצאי את המספר!)
**Priority:** High | **Effort:** Medium

- [ ] Game screen: equation with blank `_` + number pad (4-6 options)
- [ ] 8 rounds, 1 star per correct answer
- [ ] Blank position varies: missing product, missing factor, missing divisor
- [ ] Show complete equation after answering for reinforcement
- [ ] Hebrew game card on menu

### 6. Game 3 — True or False (נכון או לא?)
**Priority:** High | **Effort:** Small

- [ ] Game screen: complete equation + two buttons (נכון / לא נכון)
- [ ] 10 rounds, 1 star per correct judgment
- [ ] ~50% true, ~50% false with near-miss errors
- [ ] If wrong: briefly show the correct answer
- [ ] Hebrew game card on menu

### 7. Game 4 — Bubble Pop (פוצצי בועות!)
**Priority:** Medium | **Effort:** Large

- [ ] Game screen: target number at top + 6 floating bubbles with expressions
- [ ] 8 rounds, 1 star per correct bubble popped
- [ ] 2-3 correct bubbles per round, 3-4 wrong ones
- [ ] CSS floating animation for bubbles
- [ ] Pop animation on tap/click
- [ ] Hebrew game card on menu

### 8. Integration + Polish
**Priority:** High | **Effort:** Medium

- [ ] Backend: math sessions save/load progress correctly
- [ ] Per-session stars work for math cards
- [ ] Session celebration after completing all 4 math games
- [ ] Tests for math game result saving
- [ ] Version bump + changelog + README

---

## Dependencies

| Task | Depends On | Blocks |
|------|------------|--------|
| Math Architecture Setup | None | All other tasks |
| Math Template | Architecture Setup | Games 1-4 |
| Problem Generator | Architecture Setup | Games 1-4 |
| Game 1 (Quick Solve) | Template + Generator | Integration |
| Game 2 (Missing Number) | Template + Generator | Integration |
| Game 3 (True or False) | Template + Generator | Integration |
| Game 4 (Bubble Pop) | Template + Generator | Integration |
| Integration + Polish | Games 1-4 | None |

---

## Success Criteria

Sprint is successful if:
- [ ] `/learning/math` shows 4 session cards (1 playable, 3 locked)
- [ ] `/learning/math/math-tens-hundreds` opens math game menu with 4 games
- [ ] All 4 math games are playable with Chapter A content
- [ ] Stars earned in math show on the math session card (not on English)
- [ ] Problems use Israeli notation (× and :)
- [ ] Tests pass for math game saving/progress
- [ ] Version bumped and docs updated

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
