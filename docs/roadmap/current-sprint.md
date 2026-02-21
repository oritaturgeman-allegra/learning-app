# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
**Smart Practice Sessions** — Guarantee full vocabulary coverage in one session + add reset button for fresh practice rounds.

## Sprint Theme
Learning Completeness — Every session should practice all 55 words, and Ariel can start fresh anytime while keeping her lifetime stars.

---

## Tasks

### 1. Reset Button — Fresh Practice Round 🔄
**Priority:** High
**Why:** After Ariel finishes practicing, she needs a way to start a new round the next day without losing her lifetime stars and history.

**Behavior:**
- Adds a `reset_at` timestamp (new `app_state` table or column)
- `get_practiced_words()` only returns words from games played AFTER `reset_at`
- Word tracker resets to all 55 purple/unpracticed chips
- Session checkmarks clear (localStorage)
- Stars keep accumulating (lifetime achievement — never goes down)
- All game_results stay in DB for historical analysis

**What resets:**
- Word tracker (all chips back to purple)
- Session checkmarks (4 unchecked game cards)

**What stays:**
- Total stars (lifetime)
- All game history (accuracy trends, weak words)

**Implementation:**
- [x] Create `app_state` table with `reset_at` timestamp column
- [x] Add `reset_practiced_words()` method to GameService — sets `reset_at` to now
- [x] Update `get_practiced_words()` to filter `game_results.played_at > reset_at`
- [x] Add `POST /api/game/reset` endpoint
- [x] Replace shuffle button with reset button in UI (Hebrew: "התחלה מחדש")
- [x] Add confirmation dialog before reset ("?להתחיל מחדש")
- [x] Clear session checkmarks (localStorage) on reset
- [x] Reload word tracker after reset
- [x] Add unit tests for reset behavior
- [x] Add test: stars unchanged after reset
- [x] Add test: practiced words empty after reset
- [x] Add test: old game results still in DB after reset

**Estimated Effort:** Half day

---

### 2. Full Vocabulary Coverage in One Session 📚
**Priority:** High
**Why:** After completing all 4 games, ALL 55 words should be practiced. Currently games pick random subsets and can overlap, leaving words unpracticed.

**Current problem:**
- Game 1 (Word Match): picks 10 random words from 55
- Game 2 (Sentence Scramble): picks 6 random sentences from 14
- Game 3 (Listen & Choose): picks 10 random words from 55
- Game 4 (True/False): picks 8 random sentences from 16
- Games pick independently → words overlap → not all 55 get covered

**Solution — Session Word Planner:**
- On session start, divide all 55 words across the 4 games
- Each game gets a guaranteed set of words to cover
- Games 1 & 3 use words directly (10 + 10 = 20 words)
- Games 2 & 4 use sentences — each sentence covers multiple vocab words (~15-20 words each)
- Planner ensures remaining ~15 words are covered by sentence selection in Games 2 & 4
- May need to add more sentences to ensure full coverage

**Implementation:**
- [ ] Audit which vocab words appear in which sentences (Games 2 & 4)
- [ ] Create coverage map: word → which sentences contain it
- [ ] Build `planSession()` function that allocates words across games
- [ ] Update `initGame1()` to use planned word set instead of random pick
- [ ] Update `initGame2()` to use planned sentence set
- [ ] Update `initGame3()` to use planned word set
- [ ] Update `initGame4()` to use planned sentence set
- [ ] Add more sentences if needed to cover all 55 words
- [ ] Verify: after all 4 games, word tracker shows 0 remaining
- [ ] Test with full playthrough

**Estimated Effort:** 1 day

---

## Dependencies

| Task | Depends On | Blocks |
|------|------------|--------|
| Reset Button | None | None |
| Full Coverage | None (but easier to test with Reset) | None |

---

## Success Criteria

Sprint is successful if:
- [x] Reset button works — word tracker resets, stars stay, history preserved
- [ ] After playing all 4 games, all 55 words are practiced (0 remaining)
- [ ] Tests pass for both features
- [ ] Version bumped and README updated

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
**Next Sprint Planning:** March 6, 2026
