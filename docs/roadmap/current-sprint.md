# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
**Smart Practice Sessions** — Guarantee full vocabulary coverage in one session + add reset button for fresh practice rounds.

## Sprint Theme
Learning Completeness — Every session should practice all 55 words, and Ariel can start fresh anytime while keeping her lifetime stars.

---

## Tasks

### 1. Full Vocabulary Coverage in One Session 📚
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
- [x] Audit which vocab words appear in which sentences (Games 2 & 4)
- [x] Create coverage map: word → which sentences contain it
- [x] Build `planSession()` function that allocates words across games
- [x] Update `initGame1()` to use planned word set instead of random pick
- [x] Update `initGame2()` to use planned sentence set
- [x] Update `initGame3()` to use planned word set
- [x] Update `initGame4()` to use planned sentence set
- [x] Add more sentences if needed to cover all 55 words (added 12: 6 scramble + 6 T/F)
- [ ] Verify: after all 4 games, word tracker shows 0 remaining
- [ ] Test with full playthrough

**Estimated Effort:** 1 day

---

## Dependencies

| Task | Depends On | Blocks |
|------|------------|--------|
| Full Coverage | None | None |

---

## Success Criteria

Sprint is successful if:
- [x] Reset button works — word tracker resets, stars stay, history preserved
- [ ] After playing all 4 games, all 55 words are practiced (0 remaining)
- [x] Tests pass for both features (54 tests, 81% coverage)
- [x] Version bumped and README updated (v1.8.0)

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
**Next Sprint Planning:** March 6, 2026
