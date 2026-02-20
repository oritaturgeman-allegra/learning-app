# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
**Production Launch** - Deploy the application to production, then enhance with content discovery features.

## Sprint Theme
Infrastructure First - Get to production mid-sprint, then ship new features as live updates.

---

## Timeline

| Week | Focus | Milestone |
|------|-------|-----------|
| **Week 1** (Feb 6-12) | Infrastructure | 🚀 **Production Deploy by Feb 12** |
| **Week 2** (Feb 13-19) | Features | Ship filtering features to production |

---

## Tasks

### 🚀 WEEK 1: INFRASTRUCTURE (Feb 6-12)

**Goal:** Deploy to production by end of Week 1

---

### 📦 WEEK 2: FEATURES (Feb 13-19)

**Goal:** Ship content discovery features to production

---

#### 3. Keyword Filtering 🔍
**Priority:** High
**Why:** Users want to focus on specific topics. First feature shipped to production!
**Carryover:** No (new feature)
**Target:** Feb 13-15

**Implementation:**
- [ ] Add search input with chip-based filter UI above news carousel
- [ ] Implement client-side filtering with 300ms debounce
- [ ] Support multiple keywords (comma-separated → chips)
- [ ] Filter applies across articles (US, Israel, AI, Crypto categories)
- [ ] Highlight matching keywords in article titles/text
- [ ] Save keywords to localStorage for persistence
- [ ] Add clear/remove functionality for individual chips
- [ ] Empty state: "No articles match '[keyword]'"

**Technical Notes:**
- Extend existing `renderArticles()` function to filter by keyword
- Reuse existing `.filter-toggle` + `.topic-chip` CSS patterns
- `aria-live="polite"` for accessibility

**Estimated Effort:** 2-3 days

---

#### 4. Source Navigation & Expanded Content 📰
**Priority:** High
**Why:** Current 5-article limit is too restrictive. Users want more content.
**Carryover:** No (new feature)
**Target:** Feb 16-19

**Implementation:**
- [ ] Add source filter chips within each carousel slide header
- [ ] Populate source list dynamically from `sources_metadata`
- [ ] Implement client-side filtering by source
- [ ] Add "Show More" accordion button (show first 5, expand for rest)
- [ ] Show article count per source: "Yahoo Finance (8)"
- [ ] "All Sources" selected by default
- [ ] Save source preferences to localStorage

**Backend Change:**
- [ ] Increase `max_count` in `quality_metrics_service.py` from 5 to 8-10 articles

**Estimated Effort:** 3-4 days

---

## Deferred to Backlog

The following Sprint 5 tasks were moved to backlog (not blocking launch):
- User Analytics & Event Tracking
- Account Deletion (GDPR)
- Playwright E2E Tests
- Data Export (GDPR)
- Stripe Payment Integration
- Performance Monitoring

See `docs/roadmap/backlog.md` for details.

---

## Dependencies

| Task | Depends On | Blocks |
|------|------------|--------|
| ~~Environment Config~~ | ~~None~~ | ~~Supabase, Deployment~~ ✅ |
| ~~Supabase Migration~~ | ~~Env Config~~ | ~~Deployment~~ ✅ |
| ~~Production Deployment~~ | ~~Env Config + Supabase~~ | ~~Week 2 features~~ ✅ |
| Keyword Filtering | ~~Production~~ ✅ | None |
| Source Navigation | ~~Production~~ ✅ | None |

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| ~~Supabase migration issues~~ | ~~High~~ | ~~Medium~~ | ~~Completed ✅~~ |
| ~~Deployment blockers~~ | ~~High~~ | ~~Low~~ | ~~Deployed to Railway ✅~~ |
| Week 1 delays | Medium | Medium | Features can slip to Sprint 7 if needed |

---

## Success Criteria

Sprint is successful if:
- [x] Podcast caching optimization (~97% cost reduction) ✅
- [x] **Production deployment live** ✅ Railway (v1.51.0)
- [x] Environment configuration documented with `.env.example` ✅
- [x] Supabase database operational ✅
- [x] AI Analytics Service - Daily feed provider analysis + email reports (v1.50.0) ✅
- [x] CI/CD pipeline working ✅ v1.51.0
- [ ] Keyword filtering shipped to production
- [ ] Source filtering shipped to production
- [x] Test coverage maintained at 60%+ ✅ (68%)

---

## Launch Checklist ✅ (Completed Feb 17)

**Before Deploy:**
- [x] All env vars configured in hosting platform ✅
- [x] Supabase database migrated and tested ✅
- [x] SSL certificate ready ✅ (Railway auto-SSL)
- [x] Health check endpoint working ✅
- [x] Persistent volume for `audio_cache/` ✅

**After Deploy:**
- [x] Verify app loads correctly ✅
- [x] Test auth flow (Google OAuth) ✅ v1.51.1
- [x] Test newsletter generation ✅
- [x] Test podcast generation (verify cache works) ✅ v1.51.2 ffmpeg fix
- [x] Monitor Sentry for errors ✅ Active and monitored

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
**Next Sprint Planning:** March 6, 2026
