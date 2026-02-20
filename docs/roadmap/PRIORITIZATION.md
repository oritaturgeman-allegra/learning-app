# Feature Prioritization Framework

This framework helps evaluate new feature requests and determine where they should be placed in the roadmap.

---

## Evaluation Criteria

When a new feature is proposed, analyze it across these dimensions:

### 1. User Value (1-5)
**Score: How much does this benefit users?**

- **5 - Critical:** Solves a major pain point or unlocks core functionality
- **4 - High:** Significantly improves user experience or workflow
- **3 - Medium:** Nice improvement, users will appreciate it
- **2 - Low:** Minor improvement, some users may benefit
- **1 - Minimal:** Very niche use case or negligible impact

**Questions to ask:**
- Does this solve a real user problem?
- How many users will benefit?
- How frequently will they use it?
- What's the impact if we don't build it?

---

### 2. Strategic Fit (1-5)
**Score: How well does this align with product vision?**

- **5 - Core:** Essential to product vision and competitive positioning
- **4 - Strong:** Directly supports key product pillars
- **3 - Aligned:** Fits within product scope and strategy
- **2 - Tangential:** Loosely related to product goals
- **1 - Off-target:** Doesn't align with product direction

**Product Vision:** Transform complex capital market data into easily digestible, multilingual content experiences.

**Key Pillars:**
- Real-time market intelligence
- Accessible content (audio, multilingual)
- Personalization and customization
- Professional quality analysis

---

### 3. Technical Complexity (1-5)
**Score: How difficult is this to build?**

- **1 - Trivial:** 1-2 hours, simple changes, low risk
- **2 - Easy:** 1-2 days, straightforward implementation
- **3 - Moderate:** 3-5 days, some complexity, standard patterns
- **4 - Complex:** 1-2 weeks, significant effort, new patterns
- **5 - Very Complex:** 2+ weeks, high complexity, major architecture changes

**Factors to consider:**
- Development time
- Testing requirements
- New dependencies or infrastructure
- Technical risk and unknowns
- Documentation needs

---

### 4. Dependencies (Yes/No)
**Does this feature depend on other features or infrastructure?**

- **No Dependencies:** Can be built immediately with current system
- **Has Dependencies:** Requires other features to be completed first

**If yes, list dependencies:**
- What must be built first?
- Are those dependencies already planned?
- What's the earliest this could realistically start?

---

## Priority Score Calculation

```
Priority Score = (User Value + Strategic Fit) / Technical Complexity

Higher score = Higher priority
```

**Adjustment for Dependencies:**
- If dependencies exist, reduce priority or defer until dependencies are met

---

## Sprint Placement Decision Matrix

### Current Sprint (Next 2 weeks)
**Place here if:**
- Priority Score ≥ 2.5
- No dependencies OR dependencies already met
- Fits within sprint capacity (team isn't overloaded)
- Complements current sprint theme
- Urgency is high (user request, blocker, etc.)

**Don't place here if:**
- Sprint already full
- Requires significant research/discovery first
- Has unmet dependencies

---

### Next Sprint (2-4 weeks out)
**Place here if:**
- Priority Score ≥ 2.0
- Dependencies will be met by then
- Good fit for upcoming sprint theme
- Not urgent but important
- Allows time for proper planning/design

**Best for:**
- Features that need design work
- Features with dependencies in current sprint
- Medium-priority improvements
- Features requiring user research

---

### Backlog (Future versions)
**Place here if:**
- Priority Score < 2.0
- Has multiple unmet dependencies
- Requires significant architecture changes
- Nice-to-have but not essential
- Needs more research/validation
- Low user value or strategic fit

**Best for:**
- Exploratory ideas
- Long-term vision items
- Features needing market validation
- Low-impact improvements

---

## Feature Analysis Template

When evaluating a new feature, use this template:

```markdown
## Feature: [Feature Name]

### Description
[Brief description of what this feature does]

### Analysis

**User Value:** [1-5]
- Reasoning: [Why this score?]
- User Impact: [Who benefits and how?]

**Strategic Fit:** [1-5]
- Reasoning: [How does this align with product vision?]
- Pillar: [Which product pillar does this support?]

**Technical Complexity:** [1-5]
- Reasoning: [What makes this easy/hard?]
- Estimated Effort: [Time estimate]
- Technical Risk: [Any unknowns or challenges?]

**Dependencies:** [Yes/No]
- List: [What needs to be built first?]

**Priority Score:** [(User Value + Strategic Fit) / Technical Complexity]

### Recommendation

**Placement:** [Current Sprint / Next Sprint / Backlog]

**Reasoning:**
[Explain why this placement makes sense]

**Considerations:**
- [Any trade-offs or risks to be aware of]
- [Alternative approaches to consider]
```

---

## Example Analysis

### Feature: Dark Mode Theme

**User Value:** 4
- Reasoning: Many users prefer dark mode for reading, especially at night
- User Impact: Improves readability and reduces eye strain for 30-40% of users

**Strategic Fit:** 3
- Reasoning: Improves accessibility and user experience, but not core to market intelligence functionality
- Pillar: Accessible content

**Technical Complexity:** 2
- Reasoning: Standard CSS changes, theme toggle in UI
- Estimated Effort: 1-2 days
- Technical Risk: Low - well-established patterns

**Dependencies:** No

**Priority Score:** (4 + 3) / 2 = 3.5

### Recommendation

**Placement:** Next Sprint

**Reasoning:**
- High priority score (3.5)
- No dependencies
- Not urgent enough for current sprint
- Good fit for UX-focused sprint
- Allows time for proper design system setup

**Considerations:**
- Should we support system preference auto-detection?
- Need to test all components in dark mode
- Consider adding to user preferences (if that feature exists)

---

## Special Cases

### Bug Fixes
- **Critical bugs:** Always current sprint (override framework)
- **Major bugs:** Next sprint or current if capacity allows
- **Minor bugs:** Backlog or next available slot

### User Requests
- If multiple users request the same thing: +1 to User Value score
- If paying customers request: Consider bumping priority

### Technical Debt
- Evaluate like features, but Strategic Fit = impact on future development velocity
- High-impact debt that unblocks features: prioritize higher

### Quick Wins
- High User Value + Low Complexity = prioritize
- Great for filling sprint gaps or building momentum

---

## Framework Evolution

This framework should evolve as the product matures:

**v1.x (Current):** Focus on core features and stability
- Prioritize features that build foundation
- Lower complexity threshold (favor quick wins)

**v2.x (Future):** Focus on differentiation and scale
- Prioritize unique capabilities
- Accept higher complexity for strategic features

**Update this framework quarterly** based on:
- Product strategy changes
- User feedback patterns
- Team velocity and capacity
- Market conditions

---

**Last Updated:** November 28, 2025
**Next Review:** February 28, 2026
