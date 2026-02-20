---
description: Plan the next sprint with automated file updates, retrospective, and agent-driven prioritization
---

Plan the next sprint by analyzing completed work, writing a retrospective, and creating a prioritized sprint backlog.

## Sprint Planning Workflow

Execute the following phases in order:

---

## Phase 1: Automated File Updates

### Step 1.1: Parse Current State
Read `docs/roadmap/current-sprint.md` and extract:
- Current sprint number (N)
- Current sprint dates
- List of incomplete tasks (tasks with unchecked `[ ]` boxes)

### Step 1.2: Update `next-sprint.md` Dates

Update `docs/roadmap/next-sprint.md` dates to Sprint N+2:
- [ ] Change header: Sprint N+1 → Sprint N+2
- [ ] Change dates in header (bump 2 weeks from N+1)
- [ ] Change footer dates (Sprint Start, Sprint End, Next Sprint Planning)

**Note:** Keep the planned features content - agents will read this in Phase 3. The content stays as-is, only dates change.

### Step 1.3: Create Sprint Template
Create `docs/roadmap/completed/feature-sprints/sprint-{N+1}.md` using this template:

```markdown
# Sprint {N+1}: [Date Range]

## Sprint Goal
_To be defined_

## Sprint Theme
_To be defined_

---

## Completed Tasks

_None yet_

---

## Retrospective

_To be completed after sprint_

---

**Sprint Start:** [Date]
**Sprint End:** [Date]
**Next Sprint Planning:** [Date]
```

---

## Phase 2: Retrospective Flow

### Step 2.1: Read Previous Retro
1. Read the latest retrospective from `docs/roadmap/completed/retros/` to understand the format
2. Find the "Action Items" section from that retro
3. These are the action items that should have been addressed during this sprint

### Step 2.2: Write Sprint N Retrospective
Create `docs/roadmap/completed/retros/sprint-{N}.md` with a **full retrospective** (not a template).

Analyze the completed sprint and write:

**What Went Well:**
- Features completed successfully
- Technical wins
- Process improvements

**What Could Be Improved:**
- Challenges faced
- Scope issues
- Process gaps

**Previous Retro Action Items Review:**
- List each action item from the previous retro file
- Mark as completed or not completed
- Explain progress or why it wasn't addressed
- Incomplete items carry forward to new action items

**New Action Items:**
- Specific, actionable improvements for future sprints
- Based on this sprint's challenges

**Key Metrics:**
- Features completed vs planned
- Versions shipped
- Test coverage

**Highlights:**
- Top wins
- Technical debt addressed
- Features shipped table

### Step 2.3: Action Items Stay in Retro
Action items are tracked in the retro file:
- **Incomplete items** from previous retro carry forward
- **New action items** are added based on this sprint's learnings
- Next retro will review these items

This keeps `current-sprint.md` focused on deliverables only.

---

## Phase 3: Sprint Planning (Agent Flow)

### Step 3.1: Research Agent
**Agent:** `.claude/agents/knowledge/research.md`

**Input:** Read `docs/roadmap/next-sprint.md` to get planned features for Sprint N+1.

**For each planned feature that has technical unknowns:**
- Investigate technical requirements
- Research best practices and libraries
- Identify potential challenges
- Document findings for PM agent

### Step 3.2: UX Designer Agent
**Agent:** `.claude/agents/frontend/ux-designer.md`

**Input:** Read `docs/roadmap/next-sprint.md` to get planned features for Sprint N+1.

**For each feature with user-facing changes:**
- Define user flows
- Identify UX requirements
- Note accessibility considerations
- Flag potential usability issues
- Document recommendations for PM agent

### Step 3.3: Architect Review Agent
**Agent:** `.claude/agents/quality-assurance/architect-review.md`

**Input:** Read `docs/roadmap/next-sprint.md` to get planned features for Sprint N+1.

**Review each planned feature for:**
- Technical feasibility - can this be built as described?
- Dependency issues - what needs to exist first?
- Potential blockers - external dependencies, API limitations
- Effort estimates - is this realistic for 1 sprint?
- Technical risks - what could go wrong?

**Output:** Technical assessment for each feature to inform PM prioritization.

### Step 3.4: Product Manager Agent
**Agent:** `.claude/agents/business/product-manager.md`

**Step 1 - Gather Inputs:**
Read and analyze:
1. `docs/roadmap/current-sprint.md` - incomplete tasks (carryover candidates)
2. `docs/roadmap/next-sprint.md` - planned features for the new sprint
3. `docs/roadmap/backlog.md` - available backlog items
4. Action items from the retrospective (Phase 2)
5. Research Agent output (from Step 3.1) - technical findings and challenges
6. UX Designer Agent output (from Step 3.2) - user flow recommendations
7. Architect Agent output (from Step 3.3) - technical feasibility assessment

**Note:** Steps 3.1-3.3 run before this step. Their outputs are available in the conversation context for the PM agent to reference.

**Step 2 - Handle Incomplete Tasks (CRITICAL):**
For EVERY incomplete task from `current-sprint.md`, decide ONE of:
1. **Carry over** → Include in Sprint N+1 with "Carryover: Yes" marker
2. **Defer** → Add to `docs/roadmap/next-sprint.md` OR `docs/roadmap/backlog.md` with explanation

**IMPORTANT:** No task can be deleted. Every incomplete task must be accounted for.

**Step 3 - Responsibilities:**
1. **Prioritize all inputs** - decide what makes it into the sprint
2. **Explain WHY** - each task must include a short rationale
3. **Define sprint goal & theme** - clear focus for the sprint
4. **Set success criteria** - measurable outcomes
5. **Identify dependencies & risks**

**Output Format for each task:**
```markdown
#### Task Name
**Priority:** High / Medium / Low
**Why:** [1-2 sentence explanation of why this was prioritized]
**Carryover:** Yes / No (if from previous sprint)

**Implementation:**
- [ ] Subtask 1
- [ ] Subtask 2
```

---

## Phase 4: Output

### Step 4.1: Update `docs/roadmap/current-sprint.md`

Replace the content with the new sprint plan including:

1. **Header:** Sprint N+1 with correct dates
2. **Sprint Goal:** Clear objective (from PM)
3. **Sprint Theme:** High-level focus area (from PM)
4. **Tasks Section:**
   - Organized by priority (High → Medium → Low)
   - Each task includes **Why** explanation
   - Carryover tasks marked
5. **Dependencies:** External dependencies and blockers
6. **Success Criteria:** Measurable outcomes
7. **Footer:** Sprint dates and next planning date

### Step 4.2: Clean Up Source Files

When features are moved to `current-sprint.md`, remove them from their source files:
- Remove from `docs/roadmap/next-sprint.md` if moved from there
- Remove from `docs/roadmap/backlog.md` if moved from there

**IMPORTANT:** Features should only exist in ONE roadmap file at a time. Never leave duplicates.

---

## Summary Checklist

After completion, verify:

- [ ] `current-sprint.md` updated with Sprint N+1 content
- [ ] `next-sprint.md` dates bumped to Sprint N+2
- [ ] `completed/feature-sprints/sprint-{N+1}.md` template created
- [ ] `completed/retros/sprint-{N}.md` retrospective written
- [ ] Each task has a "Why" explanation
- [ ] Carryover tasks identified and explained
- [ ] **All incomplete tasks accounted for** (carried over OR deferred to next-sprint/backlog)
- [ ] Sprint goal and theme defined
- [ ] Success criteria listed

---

## Example Output Structure

```markdown
# Sprint 6: Feb 6 - Feb 19, 2026

## Sprint Goal
**[Goal Name]** - [1 sentence description]

## Sprint Theme
[Theme] - [What this sprint focuses on]

---

## Tasks

### HIGH PRIORITY

#### 1. Feature Name
**Priority:** High
**Why:** [Explanation of why this is prioritized now]
**Carryover:** No

**Implementation:**
- [ ] Subtask 1
- [ ] Subtask 2

---

### MEDIUM PRIORITY

#### 2. Another Feature
**Priority:** Medium
**Why:** [Explanation]
**Carryover:** Yes (from Sprint 5 - was blocked by X)

**Implementation:**
- [ ] Subtask 1

---

## Dependencies

| Feature | Depends On |
|---------|------------|
| Feature 1 | External API |

---

## Success Criteria

Sprint is successful if:
- [ ] Criterion 1
- [ ] Criterion 2

---

**Sprint Start:** February 6, 2026
**Sprint End:** February 19, 2026
**Next Sprint Planning:** February 20, 2026
```

---

**Agents Used (in order):**
1. `.claude/agents/knowledge/research.md` - Research technical unknowns
2. `.claude/agents/frontend/ux-designer.md` - Design user flows
3. `.claude/agents/quality-assurance/architect-review.md` - Assess technical feasibility
4. `.claude/agents/business/product-manager.md` - Prioritize and create sprint plan
