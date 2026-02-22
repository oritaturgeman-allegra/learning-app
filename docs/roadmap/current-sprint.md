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

### Chapter A: Tens & Hundreds (`math-tens-hundreds`) — DONE

All 8 tasks completed (v2.8.0–v2.9.0). See `docs/roadmap/completed/feature-sprints/sprint-1.md` for details.

- [x] Math architecture setup (4 session cards, routing, backend)
- [x] Math template + game engine (`math-fun.html`)
- [x] Problem generator — Chapter A (6 categories)
- [x] Game 1 — Quick Solve
- [x] Game 2 — Missing Number
- [x] Game 3 — True or False
- [x] Game 4 — Bubble Pop
- [x] Integration + polish

### Chapter B: Two-Digit Multiply (`math-two-digit`) — DONE

- [x] Problem generator for Chapter B topics:
  - 2-digit × 1-digit (e.g., `23 × 4 = ?`)
  - 2-digit × 2-digit (e.g., `15 × 12 = ?`)
  - Powers of numbers (e.g., `5² = ?`)
- [x] Unlock session card (removed `locked: True`)
- [x] Route `/learning/math/math-two-digit` serves math template with Chapter B problems
- [x] All 4 games work with Chapter B content (session-aware generator)
- [x] Tests pass + version bump (v2.10.0)

### Chapter C: Long Division (`math-long-division`) — DONE

- [x] Problem generator for Chapter C topics:
  - Division by single digit with remainder (dual-input: quotient + remainder)
  - Long division (3-digit ÷ 1-digit, clean results)
  - Division verification (reverse multiplication: `? × 7 = 63`)
- [x] Unlock session card (removed `locked: True`)
- [x] Route + template integration (session-aware generator)
- [x] All 4 games work with Chapter C content
- [x] Hint system — 💡 tooltip with solving clues per problem
- [x] Tests pass + version bump (v2.11.0)

### Chapter D: Primes & Divisibility (`math-primes`) — TODO

- [ ] Problem generator for Chapter D topics:
  - Divisibility rules for 3, 6, 9
  - Prime vs composite identification
  - Prime factorization
- [ ] Unlock session card
- [ ] Route + template integration
- [ ] All 4 games work with Chapter D content
- [ ] Tests + version bump

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
- [x] Chapter B (`math-two-digit`) unlocked and playable
- [x] Chapter C (`math-long-division`) unlocked and playable
- [ ] Chapter D (`math-primes`) unlocked and playable

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
