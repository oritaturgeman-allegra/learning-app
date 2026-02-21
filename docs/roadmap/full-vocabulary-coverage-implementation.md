# Implementation Plan: Full Vocabulary Coverage in One Session

## Task Analysis
- **Type**: Feature
- **Complexity**: Medium (half day to 1 day)
- **Priority**: High — Sprint 1 goal; directly impacts learning outcomes
- **Version**: v1.8.0 (MINOR — new feature)

## Overview

After completing all 4 games, ALL 55 vocabulary words should be practiced (word tracker shows 0 remaining). Currently games pick independently using `freshShuffle()`, causing word overlap across games and leaving words unpracticed.

## Core Objective

**Every session guarantees 100% vocabulary coverage across 4 games.**

## Success Criteria
- [ ] After playing all 4 games, all 55 words are practiced (0 remaining in tracker)
- [ ] Each game receives a pre-planned word/sentence set — no random overlap
- [ ] New sentences cover previously "orphan" vocabulary words
- [ ] Existing game mechanics unchanged (stars, rounds, UI)
- [ ] Tests pass

---

## Coverage Audit (Pre-Implementation)

### Current Word Coverage Gap

**17 vocabulary words appear in ZERO sentences** (can ONLY be covered by Games 1 & 3):

| Category | Orphan Words |
|----------|-------------|
| clothes | shirt, pants, shoes |
| seasons | spring, autumn |
| nature | pool |
| actions | eat, sleep, climb, stand, read a book, play football |
| people | father |
| body | mouth |
| descriptions | okay, good for you, too |

**38 vocabulary words appear in at least one sentence** (coverable by Games 2/4 or 1/3).

### The Math Problem

- Games 1 & 3: 10 + 10 = **20 direct word slots**
- Games 2 & 4: 6 + 8 = **14 sentence slots** (each sentence covers 1-4 vocab words)
- 17 orphan words MUST go in Games 1/3 → only **3 flexible slots** remain
- 14 sentences at ~2 words each ≈ 25-28 unique vocab words
- **Gap: ~7-10 words would remain uncovered**

### Solution: Add New Sentences

Add ~6 scramble + ~6 true/false sentences containing orphan words. This:
1. Reduces orphan count from 17 → ~0-3
2. Gives the planner maximum flexibility to achieve 100% coverage
3. Keeps round counts unchanged (10, 6, 10, 8)

---

## Implementation Phases

### Phase 1: Sentence Expansion (Content)

**Goal:** Add new sentences so every vocab word appears in at least one sentence.

- [ ] Add ~6 new `scrambleSentences` entries covering orphan words
- [ ] Add ~6 new `trueFalseSentences` entries covering orphan words
- [ ] Validate: every vocab word now appears in ≥1 sentence
- [ ] Sentences should be age-appropriate (Gen Alpha, Jet 2 textbook level)

**Draft new scramble sentences:**
```
"Father has a new shirt" → father, shirt
"I like to eat in spring" → eat, spring
"Children climb and stand on the wall" → climb, stand, wall
"I play football too" → play football, too
"My shoes and pants are okay" → shoes, pants, okay
"The pool is good for you" → pool, good for you
```

**Draft new true/false sentences:**
```
"You read a book with your eyes" → read a book, eyes (true)
"We sleep in autumn" → sleep, autumn (true)
"A mouth is on your hand" → mouth (false)
"Shoes go on your feet" → shoes (true)
"Pants go on your head" → pants (false)
"Father is a person" → father (true)
```

> Note: Final sentence wording will be refined during implementation for naturalness and pedagogical value.

### Phase 2: Coverage Map & Session Planner (Core Logic)

**Goal:** Build `planSession()` that allocates all 55 words across 4 games.

- [ ] Create `buildCoverageMap()` — maps each vocab word → which sentences contain it
- [ ] Create `planSession()` — allocates words to games using greedy set-cover
- [ ] Store session plan in `state.sessionPlan`
- [ ] Call `planSession()` on session start (after welcome screen)
- [ ] Re-plan on `executeReset()`

**Algorithm:**
```
planSession():
  1. Build coverageMap: word → { g2: [sentences], g4: [sentences] }
  2. uncovered = Set(all 55 words)
  3. Greedy pick 6 scrambleSentences maximizing uncovered word coverage
     → mark covered words
  4. Greedy pick 8 trueFalseSentences maximizing remaining uncovered coverage
     → mark covered words
  5. Remaining uncovered → split into Game 1 set + Game 3 set (≤10 each)
  6. If Game 1/3 have < 10 words, pad with already-covered vocab words
  7. Shuffle each game's set for variety
  8. Return { game1Words, game2Sentences, game3Words, game4Sentences }
```

### Phase 3: Wire Games to Planner (Integration)

**Goal:** Each `initGameN()` reads from `state.sessionPlan` instead of calling `freshShuffle()`.

- [ ] Modify `initGame1()` — use `state.sessionPlan.game1Words` instead of `freshShuffle(vocabulary, 10, 'game1')`
- [ ] Modify `initGame2()` — use `state.sessionPlan.game2Sentences` instead of `freshShuffle(scrambleSentences, 6, 'game2')`
- [ ] Modify `initGame3()` — use `state.sessionPlan.game3Words` instead of `freshShuffle(vocabulary, 10, 'game3')`
- [ ] Modify `initGame4()` — use `state.sessionPlan.game4Sentences` instead of `freshShuffle(trueFalseSentences, 8, 'game4')`
- [ ] Remove `freshShuffle()` dependency from game init (may keep for replay-only mode)
- [ ] Handle replay: when replaying a single game, re-use the planned set (shuffle order only)

### Phase 4: Validation & Edge Cases

- [ ] Add `validateSessionPlan()` — verifies all 55 words are covered
- [ ] Call validation on plan creation, log warning if any word missed
- [ ] Handle edge case: if `planSession()` can't achieve 100%, gracefully degrade (expand Game 1/3 rounds)
- [ ] Test with `executeReset()` → verify fresh plan is generated

### Phase 5: Testing & Verification

- [ ] Manual test: play all 4 games → word tracker shows 0 remaining
- [ ] Console validation: `validateSessionPlan()` returns all-clear
- [ ] Test replay behavior: replaying a game doesn't break coverage
- [ ] Test reset: after reset, new plan covers all 55 words

### Phase 6: Roadmap & Version Updates

- [ ] Bump version to `1.8.0` in `backend/defaults.py`
- [ ] Update `APP_CHANGELOG` with user-friendly description
- [ ] Update `README.md` "Recent Updates" (keep 6 items)
- [ ] Mark `current-sprint.md` checkboxes as complete
- [ ] Add entry to `docs/roadmap/completed/feature-sprints/sprint-1.md`

---

## Files to Modify/Create

```
frontend/templates/english-fun.html  (modify — sentences, planner, game init)
backend/defaults.py                  (modify — version bump + changelog)
README.md                            (modify — recent updates)
docs/roadmap/current-sprint.md       (modify — mark complete)
docs/roadmap/completed/feature-sprints/sprint-1.md  (modify — add entry)
```

## Dependencies

None — all changes are frontend JS within the existing HTML template + version/docs updates.

---

## Testing Strategy

### Unit Tests
- **New**: None needed (all logic is frontend JS, no backend changes)
- **Update**: None — backend game_service unchanged
- **Delete**: None

### Integration Tests
- None needed — no API changes

### Manual Testing

**Happy path:** Start a session → play Game 1 → Game 2 → Game 3 → Game 4 → verify word tracker shows "0/55 נשארו"

**Boundary/Negative:**
- Reset mid-session → verify new plan regenerated → play all 4 → 0 remaining
- Replay a single game → verify coverage still tracked correctly
- Refresh page mid-session → verify practiced words persist

**Verification:**
- Open browser console → run `validateSessionPlan()` → expect all 55 words allocated
- Check `state.sessionPlan` object → verify 4 game sets with no gaps

---

## Relevant Agents

| Agent | Role |
|-------|------|
| **product-manager** | Sprint alignment, success criteria |
| **game-designer** | Sentence writing, game balance (round counts) |
| **frontend-developer** | JS implementation of planner + game init changes |
| **qa-expert** | Manual test scenarios |
| **content-marketer** | Changelog wording |

---

## Security Review

**Security Review: All clear.**

No new endpoints, no user input handling changes, no data exposure. All changes are client-side game logic within an existing HTML template.

---

## Architecture / Documentation Updates

- **Architecture Docs**: No — No new services, routes, or DB changes
- **Reason**: Pure frontend game logic change within existing template

---

## Potential Issues & Mitigations

| Issue | Mitigation |
|-------|------------|
| New sentences feel unnatural | Review with game-designer agent; keep Jet 2 textbook vocabulary level |
| Greedy set-cover doesn't achieve 100% | Validation function catches this; fallback: expand Game 1/3 rounds |
| Replay breaks planned allocation | Replay re-uses same planned set, only re-shuffles order |
| `freshShuffle()` localStorage conflicts | Clear `ariel_recent_gameN` on session plan creation |
| Player skips a game (plays 3 of 4) | Word tracker correctly shows remaining; coverage is "if all 4 played" |

---

## Progress Log

| Date | Phase | Status | Notes |
|------|-------|--------|-------|
| — | Phase 1: Sentences | Not Started | |
| — | Phase 2: Planner | Not Started | |
| — | Phase 3: Integration | Not Started | |
| — | Phase 4: Validation | Not Started | |
| — | Phase 5: Testing | Not Started | |
| — | Phase 6: Roadmap | Not Started | |

## Completion Checklist

- [ ] All 55 words covered after 4 games
- [ ] New sentences added and natural
- [ ] Session planner working
- [ ] Game init functions wired to planner
- [ ] Validation passes
- [ ] Manual test: full playthrough → 0 remaining
- [ ] Version bumped to 1.8.0
- [ ] Changelog, README, sprint docs updated

---

> Delete this file after feature is complete and merged.
