---
description: Analyze task complexity and create actionable implementation plan
---

Analyze the following task and create a clear, actionable implementation plan.

## Task

$ARGUMENTS

## Analysis Framework

### 0. **Product Context** (Required)

**Always consult `.claude/agents/business/product-manager.md` first** to ensure:
- Task aligns with product vision and current sprint goals
- Proper prioritization (framework referenced in the agent)
- Clear success criteria tied to user value
- Task is broken into appropriately scoped stories

### 1. **Task Breakdown**
- Understand requirements
- Identify dependencies
- List affected files/components
- Estimate complexity (Small/Medium/Large)

### 2. **Time Estimation**
- **Small**: 1-2 hours (simple bug fix, minor feature)
- **Medium**: Half day to 1 day (new component, API endpoint)
- **Large**: 2-5 days (complex feature, multiple integrations)
- **Very Large**: 1+ week (major refactor, new subsystem)

### 3. **Risk Assessment**
Identify potential blockers:
- Unknown dependencies
- API limitations
- Data migration needs
- Breaking changes
- Third-party service issues

### 4. **Implementation Steps**

Create sequential, logical steps:
1. Setup/preparation
2. Backend changes (routes, services, models)
3. Frontend changes (templates, JS) - follow `docs/architecture/design.md` and `frontend/ui-designer` agent
4. Testing
5. Documentation
6. Deployment

### 5. **Success Criteria**

Define "done":
- Feature works as specified
- Tests pass
- No regressions
- Code reviewed
- Documented

## Output Format

### Task Analysis
- **Type**: [Bug Fix / Feature / Refactor / Infrastructure]
- **Complexity**: [Small / Medium / Large / Very Large]
- **Priority**: [High / Medium / Low]

### Relevant Agents

**Primary Agent:** `.claude/agents/business/product-manager.md` — Always include for task scoping and prioritization.

**Agent Discovery:** Dynamically scan `.claude/agents/` folder to discover all available agent categories and agents.

**How to recommend agents:**
1. **Start with product-manager** for strategic context
2. List all subfolders in `.claude/agents/` to discover agent categories
3. Read each agent's `.md` file within those folders
4. Check the "When to Use" section in each agent
5. Match the task type to relevant agents based on their descriptions
6. Recommend primary + supporting agents

**Agent Location**: `.claude/agents/`

### Implementation Plan

**Phase 1: [Name]**
- [ ] Step 1
- [ ] Step 2

**Phase 2: [Name]**
- [ ] Step 3
- [ ] Step 4

### Files to Modify/Create
```
backend/routes/api.py (modify)
backend/services/new_service.py (create)
backend/models/new_model.py (create)
frontend/templates/new_template.html (create)
tests/unit/test_new_feature.py (create)
tests/integration/test_new_feature.py (create)
```

### Dependencies
```bash
pip install package-name
```

### Testing Strategy

**Unit tests:**
- New: [List what needs new unit tests]
- Update: [List existing tests that need modification]
- Delete: [List obsolete tests to remove]

**Integration tests:**
- New: [List what needs new integration tests]
- Update: [List existing tests that need modification]
- Delete: [List obsolete tests to remove]

**Manual Testing:**

After implementation, provide 2-3 key scenarios for the user to verify using `.claude/agents/quality-assurance/qa-expert.md` format:
- **Happy path**: Specific actions to test normal expected usage
- **Boundary/Negative**: Edge values, invalid inputs, error conditions
- **Verification**: Expected behaviors and logs/indicators to check

**IMPORTANT - Auto-generate implementation tracker:**

**Create `docs/roadmap/[feature-name]-implementation.md`** with:
   - Task overview and priority
   - All implementation phases with checkboxes
   - Files to modify/create table
   - Configuration additions (if any)
   - Potential issues & mitigations
   - Progress log table
   - Completion checklist
   - Note at bottom: "Delete this file after feature is complete and merged."

### ⚠️ MANDATORY: Roadmap Updates (Do NOT Skip)

**These updates are REQUIRED after implementation, before considering the task complete:**

1. **`backend/defaults.py`** - Bump version (MINOR for features, PATCH for fixes)
2. **`backend/defaults.py` → `APP_CHANGELOG`** - Update with user-friendly text (consult `.claude/agents/business/content-marketer.md`). Write benefits, not technical details. Example: "3 new topics to explore — Space, Infrastructure & Energy" not "New categories with RSS feeds and topic chips". Keep only 3 entries.
3. **`README.md`** - Add entry to "Recent Updates" table (keep 6 items)
4. **`docs/roadmap/current-sprint.md`** - Mark completed checkboxes `[x]`, update Success Criteria
5. **`docs/roadmap/completed/feature-sprints/sprint-{N}.md`** - Add numbered entry under "## Completed Features", update "## Sprint Summary"

**Add these to your TodoWrite list as the final tasks!**

### Documentation Updates Required
- **Architecture Docs**: [Yes / No] — Update if adding new services, routes, data flows, or DB changes
  - `docs/architecture/overview.md` — New services, API routes, data flow changes
  - `docs/architecture/deep-dive.md` — LLM integrations, DB schema, microservices
  - `docs/architecture/design.md` — UI/design system changes
- **Reason**: [Brief explanation of what needs updating, or "No architectural changes"]

### Security Review

**Run using `.claude/agents/quality-assurance/security-auditor.md` principles.**

Scan all modified/created files for:
- **Injection**: SQL injection, XSS, command injection, template injection
- **Auth/AuthZ**: Missing authentication checks, broken access control, privilege escalation
- **Data exposure**: Secrets in code, sensitive data in logs, PII leaks, overly verbose error messages
- **Input validation**: Unvalidated user input, missing sanitization, type coercion issues
- **Dependencies**: Known vulnerabilities in new/updated packages
- **CORS/Headers**: Missing security headers, overly permissive CORS
- **Rate limiting**: Unprotected endpoints susceptible to abuse

**Output format:**
- **[CRITICAL]** — Must fix before merge (e.g., SQL injection, hardcoded secrets)
- **[HIGH]** — Should fix before merge (e.g., missing auth check, XSS)
- **[MEDIUM]** — Fix soon (e.g., missing rate limit, verbose errors)
- **[LOW]** — Nice to have (e.g., stricter CSP, additional logging)
- **[PASS]** — No issues found in this category

If no security issues are found, output: **Security Review: All clear.**

### Potential Issues
- Issue 1 and mitigation
- Issue 2 and mitigation

### Next Steps
1. Start with Phase 1, Step 1
2. Test incrementally
3. Commit often

---

Provide a clear, solo-developer-friendly plan that breaks down complex tasks into manageable steps.

**All agents:** Discover dynamically from `.claude/agents/` subfolders

**Sprint feature file format example:**
```markdown
### N. Feature Name (v1.X.Y)
Brief one-line description of what was done.
- Key detail 1
- Key detail 2 (if needed)

---
```
