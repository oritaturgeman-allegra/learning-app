# Star Rewards System — Implementation Tracker

## Task Overview
**Feature:** Collectible rewards system triggered by star milestones
**Priority:** High (engagement & retention for a 9-year-old)
**Version Target:** v1.9.0
**Type:** Feature (MINOR bump)

---

## Implementation Phases

### Phase 1: Design & Data Layer
- [ ] Define reward tiers, thresholds, and collectible items
- [ ] Create rewards data structure in `backend/defaults.py`
- [ ] Add `ariel_rewards` localStorage key for earned rewards
- [ ] Add rewards to progress API response

### Phase 2: Reward Popup UI
- [ ] Create reward card popup HTML (overlay with card reveal animation)
- [ ] CSS styling — card flip/reveal animation, glassmorphism, glow effects
- [ ] Card gallery grid for "My Collection" section
- [ ] Locked vs. unlocked card visual states

### Phase 3: Trigger Logic
- [ ] Hook into `checkMilestone()` to detect reward thresholds
- [ ] Show reward popup when new tier reached (after emoji parade)
- [ ] Persist earned rewards to localStorage
- [ ] Show collection count badge on trophy icon in header

### Phase 4: Collection Gallery (Header-Triggered)
- [ ] Add trophy/collection icon button to `.star-counter` header area (next to star count)
- [ ] Clicking trophy icon opens full-screen gallery overlay
- [ ] Grid display of all collectible cards (earned = vibrant, locked = grey silhouettes with "?")
- [ ] Progress bar showing "next reward at X stars"
- [ ] Hebrew labels and RTL layout
- [ ] Close button returns to previous screen

### Phase 5: Testing & Polish
- [ ] Unit tests for reward threshold logic
- [ ] Test milestone → reward popup flow
- [ ] Test persistence (reload preserves earned rewards)
- [ ] Version bump, README, sprint docs

---

## Files to Modify/Create

| File | Action | Description |
|------|--------|-------------|
| `backend/defaults.py` | Modify | Add REWARD_TIERS constant + version bump |
| `frontend/templates/english-fun.html` | Modify | Popup HTML, CSS, JS for rewards |
| `backend/services/game_service.py` | Modify | Add earned_rewards to progress response |
| `backend/routes/game.py` | Modify | Update progress endpoint schema |
| `tests/unit/test_game_service.py` | Modify | Test reward tier logic |

---

## Reward Tiers (Proposed)

| Stars | English Name | Hebrew Name | Emoji | Vibe |
|-------|-------------|-------------|-------|------|
| 25 | Spark | ניצוץ | ✨ | First glow-up — you're on fire |
| 50 | Flame | להבה | 🔥 | Officially lit |
| 100 | Rocket | רקטה | 🚀 | Blasting off, no limits |
| 150 | Unicorn | חד-קרן | 🦄 | Rare and magical |
| 200 | GOAT | מלכת הכל | 🐐 | Greatest of all time |
| 300 | Legend | אגדה | 👑 | Final boss unlocked |

---

## Potential Issues & Mitigations

| Issue | Mitigation |
|-------|------------|
| Child loses interest if rewards too far apart | Space tiers closer at start (25, 50) then wider |
| Popup interrupts gameplay flow | Show reward after game completion, not mid-game |
| localStorage full/cleared | Backend tracks total_stars → can recalculate earned tiers |
| Too many animations stack | Queue reward popup after milestone animation |

---

## Progress Log

| Date | Phase | Status | Notes |
|------|-------|--------|-------|
| | | | |

---

## Completion Checklist
- [ ] Feature works as specified
- [ ] Tests pass
- [ ] Version bumped in `backend/defaults.py`
- [ ] `APP_CHANGELOG` updated
- [ ] `README.md` updated
- [ ] `docs/roadmap/current-sprint.md` updated
- [ ] Sprint completion logged

---

*Delete this file after feature is complete and merged.*
