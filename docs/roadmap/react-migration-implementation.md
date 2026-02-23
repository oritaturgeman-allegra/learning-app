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

### Phase 3: Core Layout & Navigation Screens
- [ ] Create shared components: Layout, StarCounter, SubjectCard, SessionCard, GameCard
- [ ] Create API client (`frontend/src/api/game.ts`) wrapping existing endpoints
- [ ] Create `useProgress` hook (stars, accuracy, practiced words — localStorage + API sync)
- [ ] Port pages: Welcome, SubjectPicker, SessionPicker, GameMenu
- [ ] Bring over CSS keyframe animations in `global.css`
- [ ] **User tests**: Navigate all screens on iPhone — responsive layout, RTL, star counter

### Phase 4: Audio & Reward Systems
- [ ] Create `useAudio` hook (AudioContext tones + Web Speech API TTS)
- [ ] Create `useRewards` hook (tier checking, unlock detection, collection)
- [ ] Create reward components: RewardPopup, Confetti, EmojiParade, MilestoneOverlay, RewardCollection
- [ ] **Verify**: Earn stars → sound plays, confetti appears, rewards unlock

### Phase 5: English Games
- [ ] Migrate `english-data.js` → `frontend/src/data/english.ts` (typed)
- [ ] Create `useGameEngine` hook (shared game loop: rounds, scoring, answer checking)
- [ ] Port games: WordMatch, SentenceBuilder, ListenAndChoose, TrueFalse
- [ ] Port WordTracker (sidebar on desktop, MUI Drawer on mobile)
- [ ] Wire up `buildCoverageMap` and word distribution logic
- [ ] **User tests all 4 English games on iPhone**

### Phase 6: Math Games
- [ ] Migrate `math-data.js` → `frontend/src/data/math.ts` (typed)
- [ ] Port games: QuickSolve, MissingNumber, MathTrueFalse, BubblePop
- [ ] Port hint system (MUI Tooltip, touch-friendly)
- [ ] Port problem generators (generateProblem, generateProblemByCategory)
- [ ] **User tests all 4 Math games on iPhone**

### Phase 7: Cleanup & Polish
- [ ] Delete old frontend files (templates/*.html, static/css/*.css, static/js/*.js)
- [ ] Remove Jinja2 dependency from `backend/web_app.py`
- [ ] Add `React.lazy()` + Suspense for game components
- [ ] Touch tuning: min-height 44px on all interactive elements
- [ ] Test on iPhone SE (375px), iPhone 15 (393px), iPad (768px)
- [ ] Check & update architecture docs (`docs/architecture/`)
- [ ] Bump version to v3.0.0 in `backend/defaults.py`
- [ ] Update README.md, APP_CHANGELOG, sprint docs

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
| ✅ Done | `frontend/src/App.tsx` | Routes + theme provider |
| ✅ Done | `frontend/src/theme.ts` | MUI theme (design tokens) |
| Create | `frontend/src/api/game.ts` | API client (fetch wrapper) |
| Create | `frontend/src/hooks/useAudio.ts` | Audio system hook |
| Create | `frontend/src/hooks/useProgress.ts` | Stars, rewards, API sync |
| Create | `frontend/src/hooks/useRewards.ts` | Reward tier logic |
| Create | `frontend/src/hooks/useGameEngine.ts` | Shared game loop |
| Create | `frontend/src/components/*.tsx` | Layout, StarCounter, cards, rewards |
| Create | `frontend/src/pages/*.tsx` | Welcome, SubjectPicker, SessionPicker, GameMenu |
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

---

## Completion Checklist

- [ ] All 8 games playable on mobile (iPhone)
- [ ] RTL Hebrew renders correctly
- [ ] Stars persist across sessions (localStorage + API)
- [ ] Audio works (sound effects + TTS)
- [ ] All reward tiers unlock correctly
- [ ] Old frontend files deleted
- [ ] Architecture docs updated
- [ ] Version bumped to v3.0.0
- [ ] README.md updated
- [ ] Tests passing

---

*Delete this file after feature is complete and merged.*
