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

All tasks completed — see `docs/roadmap/completed/feature-sprints/sprint-1.md` for details.

---

## Success Criteria

Sprint is successful if:
- [x] `/learning/math` shows 4 session cards (1 playable, 3 locked)
- [x] `/learning/math/math-tens-hundreds` opens math game menu with 4 games
- [x] All 4 math games are playable with Chapter A content
- [x] Stars earned in math show on the math session card (not on English)
- [x] Problems use Israeli notation (× and :)
- [x] Tests pass for math game saving/progress
- [x] Version bumped and docs updated

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
