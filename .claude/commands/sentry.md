---
description: Fetch, analyze, and auto-fix Sentry issues with full documentation
---

Fetch Sentry issues for the Capital Market Newsletter project, automatically investigate and fix them, then document all changes.

## Configuration Required

The following environment variables must be set in `.env`:
- `SENTRY_AUTH_TOKEN` - Personal auth token from Sentry (needs read+write)
- `SENTRY_ORG` - Organization slug (your-newsletter-your-way)
- `SENTRY_PROJECT` - Project slug (python-fastapi)

## Command Usage

$ARGUMENTS

- **No args**: Full workflow - fetch, analyze, fix, document
- **`--check`**: Only show issues without fixing
- **`<issue-id>`** (e.g., `PYTHON-FASTAPI-Q`): Investigate specific issue only

### Examples
```
/sentry              # Full workflow: fetch → fix → document
/sentry --check      # View only, no fixes
/sentry PYTHON-Q     # Investigate specific issue
```

---

## Execution Workflow

### Phase 1: Fetch Issues

Read `.env` for credentials, then fetch unresolved issues:

```bash
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/issues/?query=is:unresolved&limit=20"
```

Display summary table:
| ID | Title | Count | Last Seen | Priority |
|----|-------|-------|-----------|----------|

**If 0 issues:** Report "Sentry dashboard is clean!" and stop.

---

### Phase 2: Analyze Each Issue

For each unresolved issue:

1. **Fetch detailed event data** including stack trace via:
   ```bash
   curl -s -H "Authorization: Bearer $TOKEN" "https://sentry.io/api/0/issues/{issue_id}/events/latest/"
   ```
2. **Identify root cause** from error message and affected file/line
3. **Classify issue type:**
   - Test data (from pytest) → Mark for resolution only
   - Configuration error → Fix config
   - Code bug → Fix code
   - External API error → Add better error handling

---

### Phase 3: Auto-Fix Issues

For each fixable issue:

1. **Read the affected file(s)** to understand context
2. **Implement the fix** following project conventions:
   - Type hints on all functions
   - Custom exceptions from `backend/exceptions.py`
   - Logging, not print()
3. **Run relevant tests** to verify fix doesn't break anything
4. **Resolve the issue in Sentry** via API after fix is confirmed:
   ```bash
   curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"status": "resolved"}' "https://sentry.io/api/0/issues/{issue_id}/"
   ```

---

### Phase 4: Documentation Updates

After all fixes are complete:

#### 1. Bump Version
Edit `backend/defaults.py`:
- PATCH bump for bug fixes (x.x.1 → x.x.2)
- MINOR bump for new features (x.1.x → x.2.x)

#### 2. Update README.md
Add entry to "Recent Updates" table (keep 6 items):
```markdown
| vX.Y.Z  | MM/DD | Fix: Brief description of Sentry fixes applied |
```

#### 3. Update Sprint File
Add entry to `docs/roadmap/completed/feature-sprints/sprint-6.md`:
```markdown
### N. Sentry Fixes (vX.Y.Z)
Brief description of fixes applied.
- Fix 1: Description
- Fix 2: Description

---
```

Also update Sprint Summary version range if needed.

---

### Phase 5: Summary Report

Display final summary:

```markdown
## Sentry Fix Summary

**Issues Processed:** X
**Issues Fixed:** Y
**Issues Resolved (test data):** Z

### Changes Made

| File | Change |
|------|--------|
| backend/config.py | Added TTS voice validation |
| tests/conftest.py | Disabled Sentry in tests |

### Version Bump
v1.50.2 → v1.50.3

### Files Updated
- backend/defaults.py (version)
- README.md (changelog)
- docs/roadmap/completed/feature-sprints/sprint-6.md (sprint log)

### Next Steps
- [ ] Review changes: `git diff`
- [ ] Run full test suite: `.venv/bin/pytest tests/`
- [ ] Commit when ready
```

---

## Notes

- **Test issues** (from pytest runs with test data like "TestSource", "http://test.com") are resolved without code changes
- **Production issues** get full investigation and fixes
- All fixes follow CLAUDE.md conventions
- Tests are run to verify fixes before marking issues resolved
- The current sprint file is `docs/roadmap/completed/feature-sprints/sprint-6.md`
