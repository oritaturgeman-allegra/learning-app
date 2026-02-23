# React Migration — Implementation Tracker

**Task**: Migrate frontend from vanilla JS/Jinja2 to React + MUI + TypeScript
**Type**: Infrastructure / Major Refactor
**Complexity**: Very Large (multi-session)
**Priority**: Medium
**Target Version**: v3.0.0

---

## Implementation Phases

### Phase 1: React Project Scaffolding ✅ (v2.14.0)
- [x] Initialize Vite + React + TypeScript project (`frontend/src/`, `frontend/package.json`, `frontend/vite.config.ts`)
- [x] Install dependencies: react, react-dom, react-router-dom, @mui/material, @mui/icons-material, @emotion/react, @emotion/styled, @emotion/cache, stylis-plugin-rtl
- [x] Create MUI theme (`frontend/src/theme.ts`) with existing design tokens from `shared.css`
- [x] Create `App.tsx` with React Router matching current URL structure
- [x] Configure Vite dev server proxy: `/api/*` → `localhost:8000`
- [x] **Verify**: `npm run dev` shows React page at `localhost:5173`

### Phase 2: Backend Adaptation ✅ (v2.14.1)
- [x] Add `/api/game/config` endpoint (reward_tiers, sessions, version, changelog)
- [x] Serve `frontend/dist/` as static files from FastAPI
- [x] Add SPA catch-all route `/app/{full_path:path}` → serve `index.html`
- [x] Keep Jinja2 routes alive alongside React during migration
- [x] **Verify**: `npm run build` → FastAPI serves React app at `localhost:8000/app/`

### Phase 3: Core Layout & Navigation Screens ✅ (v2.15.0)
- [x] Create shared components: Layout, StarCounter, RewardCollection
- [x] Create API client (`frontend/src/api/game.ts`) + TypeScript types (`api/types.ts`)
- [x] Create AppContext (`context/AppContext.tsx`) — progress + config state with localStorage fallback
- [x] Port pages: Welcome, SubjectPicker, SessionPicker, GameMenu
- [x] Create game card data (`data/games.ts`) — metadata per subject
- [x] Bring over CSS keyframe animations in `styles/global.css`
- [ ] **User tests**: Navigate all screens on iPhone — responsive layout, RTL, star counter

### Phase 4: Audio & Reward Systems ✅ (v2.16.0)
- [x] Create `useAudio` module (AudioContext tones + Web Speech API TTS)
- [x] Create `useRewards` hook (milestone checks, reward unlock, confetti orchestration)
- [x] Create celebration components: Confetti, MilestoneOverlay, RewardPopup
- [x] Wire into Layout (renders all overlays) + AppContext (`awardStars()`)
- [ ] **Verify**: Earn stars → sound plays, confetti appears, rewards unlock

### Phase 5: English Games
- [x] Migrate `english-data.js` → `frontend/src/data/english.ts` (typed vocab, sentences, session planner)
- [x] Create `useGameEngine` hook (shared game loop: rounds, scoring, answer delays)
- [x] Port games: WordMatch, SentenceScramble, ListenAndChoose, TrueFalse
- [x] Port WordTracker (sidebar on desktop, MUI Drawer on mobile)
- [x] GameScreen route wrapper + CompletionScreen + milestone watcher in Layout
- [x] GameMenu navigates to games, shows completion checkmarks
- [ ] **User tests all 4 English games on iPhone**

### Phase 6: Math Games ✅ (v2.18.0)
- [x] Create `frontend/src/data/math.ts` — typed problem generators, hints, categories
  - Port `generateProblemByCategory()` for all 15 categories (multiply_tens, multiply_hundreds, divide_single, divide_tens, properties_0_1, order_of_operations, two_digit_x_one_digit, two_digit_x_two_digit, powers, divide_remainder, long_division, division_verify, divisibility_rules, prime_composite, prime_factorization)
  - Port `generateDistractors()`, `generateTFProblem()`, `generateExpressionsForTarget()`, `generateWrongExpressions()`
  - Port `CATEGORIES_BY_SESSION` mapping (4 sessions × 3-6 categories each)
  - Port `MATH_HINTS` — Hebrew hint functions/strings per category
  - Types: `MathProblem`, `TFProblem`, `BubbleItem`, `MissingNumberProblem`
- [x] Create `frontend/src/games/math/MathGameScreen.tsx` — route wrapper (like English GameScreen)
  - Reads `gameId` + `sessionSlug` from URL params
  - Switches on gameId to render correct math game component
  - Saves result to API on finish, reuses CompletionScreen
- [x] Port Game 1: `QuickSolve.tsx` (פתרי מהר!) — 10 rounds, 1 star/correct
  - Multiple-choice for standard problems (4 options)
  - Remainder input UI for `divide_remainder` problems (quotient + remainder fields)
  - Hint button per problem
- [x] Port Game 2: `MissingNumber.tsx` (מצאי את המספר!) — 8 rounds, 1 star/correct
  - Blanks a number from the equation, shows 4 options
  - Handles special categories: division_verify, prime_composite, prime_factorization, divide_remainder
- [x] Port Game 3: `MathTrueFalse.tsx` (נכון או לא?) — 10 rounds, 1 star/correct
  - Shows equation with answer (correct or wrong), yes/no buttons
  - Special T/F for prime_composite ("13 — מספר ראשוני") and prime_factorization
  - Shows correct answer on wrong response
- [x] Port Game 4: `BubblePop.tsx` (פוצצי בועות!) — 8 rounds, 1 star per correct bubble
  - Shows target number, 6 bubbles (2-3 correct + 3-4 wrong expressions)
  - Floating animation, pop on correct tap, shake on wrong
  - Session-aware target numbers (BUBBLE_TARGETS per session)
- [x] Port hint system — `HintButton.tsx` component (💡 icon, MUI Popover, auto-close 4s)
- [x] Add math game route to `App.tsx` — GameRouter checks subject and renders English/Math GameScreen
- [x] Update `GameMenu.tsx` — math cards navigate to games (removed "coming soon" snackbar)
- [x] Check & update architecture docs (`docs/architecture/`)
- [x] Bump version, update README + sprint docs
- [ ] **User tests all 4 Math games on iPhone**

### Phase 7: Cleanup & Polish ✅ (v3.0.0)
- [x] Delete old frontend files (templates/*.html, static/css/*.css, static/js/*.js) — 11 files, ~5000 lines removed
- [x] Remove Jinja2 dependency from `backend/web_app.py` and `requirements.txt`
- [x] Move React SPA from `/app/` to root `/` with backward-compat redirects
- [x] Migrate static assets to `frontend/public/`
- [x] Add `React.lazy()` + Suspense for all 8 game components + CompletionScreen
- [x] Touch tuning: min-height 48px on CompletionScreen buttons, HintButton
- [x] Remove unused CSS animation (`@keyframes wiggle`)
- [x] Check & update architecture docs (`docs/architecture/`)
- [x] Bump version to v3.0.0 in `backend/defaults.py`
- [x] Update README.md, APP_CHANGELOG, CLAUDE.md
- [ ] **User tests on iPhone SE (375px), iPhone 15 (393px), iPad (768px)**

---

## Files to Modify/Create

| Action | File | Description |
|--------|------|-------------|
| ✅ Done | `backend/web_app.py` | SPA fallback at /app/*, serve React build from frontend/dist/ |
| ✅ Done | `backend/routes/game.py` | Added /api/game/config endpoint |
| Modify | `backend/defaults.py` | Version bump to 3.0.0 (incremental bumps until then) |
| ✅ Done | `frontend/package.json` | React, MUI, Vite dependencies |
| ✅ Done | `frontend/vite.config.ts` | Build config, proxy, RTL |
| ✅ Done | `frontend/tsconfig.json` | TypeScript config |
| ✅ Done | `frontend/index.html` | SPA entry point |
| ✅ Done | `frontend/src/main.tsx` | React root mount |
| ✅ Done | `frontend/src/App.tsx` | Routes + AppProvider |
| ✅ Done | `frontend/src/theme.ts` | MUI theme (design tokens) |
| ✅ Done | `frontend/src/api/types.ts` | TypeScript interfaces for API responses |
| ✅ Done | `frontend/src/api/game.ts` | Typed API client (fetch wrapper) |
| ✅ Done | `frontend/src/context/AppContext.tsx` | React Context for progress + config |
| ✅ Done | `frontend/src/components/Layout.tsx` | Header shell with Outlet |
| ✅ Done | `frontend/src/components/StarCounter.tsx` | Gold pill star counter |
| ✅ Done | `frontend/src/components/RewardCollection.tsx` | Trophy gallery dialog |
| ✅ Done | `frontend/src/data/games.ts` | Game card metadata per subject |
| ✅ Done | `frontend/src/styles/global.css` | CSS keyframe animations |
| ✅ Done | `frontend/src/pages/Welcome.tsx` | Landing page |
| ✅ Done | `frontend/src/pages/SubjectPicker.tsx` | English/Math selection |
| ✅ Done | `frontend/src/pages/SessionPicker.tsx` | Unit selection with tabs |
| ✅ Done | `frontend/src/pages/GameMenu.tsx` | Game card grid |
| Create | `frontend/src/hooks/useAudio.ts` | Audio system hook |
| Create | `frontend/src/hooks/useRewards.ts` | Reward tier logic |
| Create | `frontend/src/hooks/useGameEngine.ts` | Shared game loop |
| Create | `frontend/src/pages/english/*.tsx` | 4 English game components |
| Create | `frontend/src/pages/math/*.tsx` | 4 Math game components |
| Create | `frontend/src/data/english.ts` | Typed vocabulary data |
| Create | `frontend/src/data/math.ts` | Typed math data |
| Create | `frontend/src/styles/global.css` | Keyframe animations |
| Delete | `frontend/templates/*.html` | Old Jinja2 templates (Phase 7) |
| Delete | `frontend/static/css/*.css` | Old stylesheets (Phase 7) |
| Delete | `frontend/static/js/*.js` | Old scripts (Phase 7) |

---

## Dependencies

```bash
npm install react react-dom react-router-dom @mui/material @mui/icons-material @emotion/react @emotion/styled @emotion/cache stylis-plugin-rtl
npm install -D vite @vitejs/plugin-react typescript @types/react @types/react-dom
```

---

## Potential Issues & Mitigations

| Issue | Mitigation |
|-------|-----------|
| Old frontend breaks during migration | Keep Jinja2 routes alive until Phase 7 |
| RTL rendering issues with MUI | MUI has official RTL support via `stylis-plugin-rtl`; test in Phase 1 |
| Game animations feel different | Keep exact CSS keyframes in `global.css`; don't rewrite them |
| Bundle too large for mobile | Lazy-load games with `React.lazy()`; MUI tree-shakes unused |
| Web Speech API quirks in React | Wrap in `useAudio` hook with same browser detection |
| Version jump to 3.0.0 | Major frontend rewrite — semver MAJOR is appropriate |

---

## Progress Log

| Date | Phase | What was done | Version |
|------|-------|---------------|---------|
| 02/23 | Phase 1 | Vite + React 19 + TS + MUI 7 scaffolding, theme, RTL, routing, placeholder pages | v2.14.0 |
| 02/23 | Phase 2 | /api/game/config endpoint, serve React build from FastAPI at /app/, SPA catch-all | v2.14.1 |
| 02/23 | Phase 3 | API client, AppContext, Layout, StarCounter, RewardCollection, 4 navigation pages, animations | v2.15.0 |
| 02/23 | Phase 4 | useAudio (tones + TTS), Confetti, MilestoneOverlay, RewardPopup, useRewards orchestration, Layout + AppContext wiring | v2.16.0 |
| 02/23 | Phase 5 | English games: data/english.ts, useGameEngine, 4 game components, GameScreen, CompletionScreen, WordTracker, GameMenu navigation | v2.17.0 |
| 02/23 | Phase 6 | Math games: data/math.ts (15 categories, hints, distractors, TF, bubbles), 4 game components (QuickSolve, MissingNumber, MathTrueFalse, BubblePop), HintButton, MathGameScreen, GameRouter, GameMenu enabled | v2.18.0 |
| 02/23 | Phase 7 | Delete legacy frontend (11 files, ~5000 lines), remove Jinja2, move React to root /, code splitting (React.lazy), touch target polish, migrate assets to public/ | v3.0.0 |

---

## Completion Checklist

- [ ] All 8 games playable on mobile (iPhone)
- [ ] RTL Hebrew renders correctly
- [ ] Stars persist across sessions (localStorage + API)
- [ ] Audio works (sound effects + TTS)
- [ ] All reward tiers unlock correctly
- [x] Old frontend files deleted
- [x] Architecture docs updated
- [x] Version bumped to v3.0.0
- [x] README.md updated
- [x] Tests passing (71 tests)

---

*Delete this file after feature is complete and merged.*
