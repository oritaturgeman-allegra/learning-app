# Sprint 2-3-4 Retrospective: Dec 12, 2025 - Jan 22, 2026

## What Went Well

- **Feature velocity:** 12 features shipped across 3 sprints (Sentiment Tracker, DB optimization, Quality Metrics, UI redesigns)
- **LLM integration matured:** Sentiment scoring and quality metrics now fully LLM-powered with batch optimization
- **Major UI overhaul:** Landing page, carousel, footer, podcast sidebar - professional look achieved
- **Infrastructure wins:** Feed URLs in DB, retention cleanup, stats optimization
- **Cost optimization:** Reduced LLM calls from 40+ to ~7 per refresh with batch scoring
- **Code quality:** CSS split from 1306 lines to 6 focused files (max 353 lines)

## What Could Be Improved

- **Sprint scope varied wildly:** Sprint 2 had 1 feature, Sprint 4 had 10 features
- **No mid-sprint check-ins:** Scope expanded without formal review
- **UI changes cascaded:** One redesign led to another, scope creep
- **No retro cadence:** This retro covers 6 weeks instead of 2

## Action Items

- [ ] Keep sprints more consistent in scope (3-5 features each)
- [ ] Schedule mid-sprint scope review
- [ ] Write retros immediately after each sprint
- [ ] Group related UI changes into single feature when planning

## Key Metrics

| Metric | Value |
|--------|-------|
| **Sprints Covered** | 3 (Sprint 2, 3, 4) |
| **Duration** | 6 weeks |
| **Features Completed** | 12 features |
| **Versions Shipped** | 17 (v1.28.0 → v1.32.1) |
| **Tests** | 273+ passing |
| **Refactors** | 1 (CSS split) |

## Highlights

### Top 3 Wins

1. **Sentiment Tracker** - Real-time LLM-calculated market mood with 7-day charts per category
2. **LLM Quality Metrics** - Batch scoring reduced API calls by 80%+ while improving article selection
3. **Landing Page Redesign** - Hero banner, carousel cards, professional conversion flow

### Technical Debt Addressed

- Moved RSS feed URLs from code to database
- Split monolithic CSS (1306 lines → 6 files)
- Removed low-reliability feed providers (4 sources)
- Implemented retention cleanup (60 days → 10 days)
- Renamed services for clarity (article_filter → quality_metrics, market_agent → market_data_service)

### Features Shipped

| Feature | Version | Sprint | Impact |
|---------|---------|--------|--------|
| Sentiment Tracker | v1.28.0-1 | 2 | Real-time market mood visualization |
| DB Stats Optimization | v1.29.0-1 | 3 | Reduced DB bloat, lifetime stats |
| Feed URL Storage | v1.29.3 | 4 | URLs managed in DB, not code |
| LLM Quality Metrics | v1.30.0 | 4 | 80% fewer LLM calls, better articles |
| Footer Redesign | v1.30.2 | 4 | Professional look, social icons |
| Feed Provider Cleanup | v1.30.3 | 4 | Removed 4 unreliable sources |
| Article Scoring Fix | v1.30.4 | 4 | Fixed truncation, optimized time window |
| Live Market Commentary | v1.30.5 | 4 | Scrollable tweet sidebar |
| Landing Page Carousel | v1.30.6 | 4 | 3-card horizontal layout |
| CSS File Split | v1.30.7 | 4 | 6 focused CSS files |
| Landing Page Redesign | v1.31.0 | 4 | Hero banner, simplified flow |
| Carousel Cards Update | v1.32.0 | 4 | 5 new feature-focused cards |
| Podcast Sidebar | v1.32.1 | 4 | Compact controls, better layout |

---

**Retrospective Date:** January 27, 2026
**Next Sprint:** [Sprint 5: Jan 23 - Feb 5](../feature-sprints/sprint-5.md)
