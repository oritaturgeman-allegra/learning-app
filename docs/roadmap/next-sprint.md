# Sprint 7: Feb 20 - Mar 5, 2026

## Sprint Goal
**Post-Launch Quality & Compliance** - Add analytics, GDPR compliance, and automated testing after production deployment.

## Sprint Theme
Quality & Compliance - Ensuring the product is legally compliant and well-monitored.

---

## Planned Features

| # | Feature | Priority | Effort |
|---|---------|----------|--------|
| 1 | User Analytics & Event Tracking 📊 | Medium | 0.5 sprint |
| 2 | Account Deletion (GDPR) 🗑️ | Medium | 0.5 sprint |
| 3 | Playwright E2E Tests 🎭 | Medium | 0.5 sprint |

---

## Feature Details

### 1. User Analytics & Event Tracking 📊
**Priority:** Medium
**Why:** Post-launch, need to understand user behavior to improve product
**Deferred from:** Sprint 5

**Implementation:**
- [ ] Choose analytics provider (Plausible, PostHog, or custom)
- [ ] Track key events:
  - Page views
  - Newsletter generation
  - Podcast plays (start, complete, duration)
  - Sign up / login
  - Category filter changes
- [ ] Create analytics dashboard or use provider's
- [ ] Respect cookie consent - don't track without permission

---

### 2. Account Deletion (GDPR Right to Erasure) 🗑️
**Priority:** Medium
**Why:** Legal requirement for EU users - should be added shortly after launch
**Deferred from:** Sprint 5

**Implementation:**
- [ ] Add "Delete Account" button in user settings
- [ ] Confirmation modal with warning
- [ ] Delete user data (user record, preferences)
- [ ] Send confirmation email
- [ ] Endpoint: `DELETE /api/auth/account`
- [ ] 30-day grace period option (soft delete)

---

### 3. Playwright E2E Tests 🎭
**Priority:** Medium
**Why:** Now in production, automated testing catches regressions before users see them
**Deferred from:** Sprint 5

**Implementation:**
- [ ] Install Playwright: `pip install playwright pytest-playwright`
- [ ] Install browsers: `playwright install chromium`
- [ ] Create `tests/e2e/` directory
- [ ] Write E2E tests for critical flows:
  - [ ] Homepage loads correctly
  - [ ] Login/signup flow
  - [ ] Newsletter generation
  - [ ] Podcast player controls
- [ ] Add to CI pipeline (GitHub Actions)
- [ ] Screenshot on failure for debugging

---

## Dependencies & Risks

**Dependencies:**
- All features require production to be deployed (Sprint 6)
- Account deletion requires user authentication system

**Risks:**
- Analytics provider selection may require evaluation time
- GDPR compliance needs legal review

**Mitigation:**
- Start with simple analytics (Plausible) - can switch later
- Use standard GDPR deletion patterns

---

## Success Criteria

Sprint is successful if:
- [ ] Analytics tracking key user events
- [ ] Account deletion working for GDPR compliance
- [ ] E2E tests in CI pipeline for critical flows
- [ ] Test coverage maintained at 60%+

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
**Next Sprint Planning:** March 6, 2026
