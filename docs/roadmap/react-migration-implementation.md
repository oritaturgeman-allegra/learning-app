# React Migration — Implementation Tracker

**Task**: Migrate frontend from vanilla JS/Jinja2 to React + MUI + TypeScript
**Type**: Infrastructure / Major Refactor
**Complexity**: Very Large (multi-session)
**Priority**: Medium
**Target Version**: v3.0.0

---

## Implementation Phases

### Phase 1: React Project Scaffolding
- [ ] Initialize Vite + React + TypeScript project (`frontend/src/`, `frontend/package.json`, `frontend/vite.config.ts`)
- [ ] Install dependencies: react, react-dom, react-router-dom, @mui/material, @mui/icons-material, @emotion/react, @emotion/styled, @emotion/cache, stylis-plugin-rtl
- [ ] Create MUI theme (`frontend/src/theme.ts`) with existing design tokens from `shared.css`
- [ ] Create `App.tsx` with React Router matching current URL structure
- [ ] Configure Vite dev server proxy: `/api/*` → `localhost:8000`
- [ ] **Verify**: `npm run dev` shows React page at `localhost:5173`

### Phase 2: Backend Adaptation
- [ ] Add `/api/config/{subject}/{session_slug}` endpoint (reward_tiers, sessions, version, changelog)
- [ ] Serve `frontend/dist/` as static files from FastAPI
- [ ] Add SPA catch-all route `/{full_path:path}` → serve `index.html`
- [ ] Keep Jinja2 routes alive alongside React during migration
- [ ] **Verify**: `npm run build` → FastAPI serves React app at `localhost:8000`

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
| Modify | `backend/web_app.py` | Add /api/config, SPA fallback, serve React build |
| Modify | `backend/routes/game.py` | Add config endpoint |
| Modify | `backend/defaults.py` | Version bump to 3.0.0 |
| Create | `frontend/package.json` | React, MUI, Vite dependencies |
| Create | `frontend/vite.config.ts` | Build config, proxy, RTL |
| Create | `frontend/tsconfig.json` | TypeScript config |
| Create | `frontend/index.html` | SPA entry point |
| Create | `frontend/src/main.tsx` | React root mount |
| Create | `frontend/src/App.tsx` | Routes + theme provider |
| Create | `frontend/src/theme.ts` | MUI theme (design tokens) |
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
| | | | |

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
