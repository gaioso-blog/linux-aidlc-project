# PRF Template (Problem, Requirements, Forward Plan)

Use this template when the customer chose Option 2.

```markdown
# Intent: [Project or Feature Name]

**Author:** [customer name]    **Date:** [today]    **Status:** Draft

**Type:** Greenfield | Brownfield    **Target release:** [from North Star timeline]

---

## P - Problem

### Context

[One paragraph from Stage 1: the current situation, what exists today, why this matters now]

### Problem statement

[Expanded Today Statement from Stage 2. One or two paragraphs, stated from the user perspective, not the solution perspective]

### Target users

| User type | What they need | Pain today |
|---|---|---|
| [from Stage 1] | [from Stage 1 goals] | [from Stage 1 pain points] |
| [from Stage 1] | [from Stage 1 goals] | [from Stage 1 pain points] |

### Success metrics

| Metric | Target | Measured how |
|---|---|---|
| [from Stage 5] | [target] | [measurement method] |
| [from Stage 5] | [target] | [measurement method] |
| [from Stage 5] | [target] | [measurement method] |

---

## R - Requirements

### In scope (MVP)

- [Feature 1, derived from Stage 3 solution direction and Stage 4 future experience]
- [Feature 2]
- [Feature 3]

### Out of scope (explicit)

| Excluded feature | Reason | Target phase |
|---|---|---|
| [feature] | [why out now] | [Phase 2/3] |

### Constraints

- **Must use:** [languages, frameworks, services - ask customer if not already stated]
- **Must not change (brownfield only):** [existing APIs, schemas, services that must stay untouched]
- **Compliance / security:** [e.g. PCI, LGPD, SOC2, internal security baseline]
- **Non-functional targets:** [availability, latency, throughput, data residency]

### Assumptions

- [Assumption 1, state explicitly so AI-DLC can challenge it]
- [Assumption 2]

---

## F - Forward plan

### Open questions (pre-declared ambiguities)

- [Question 1, anything that came up during the session that remains undecided]
- [Question 2]

### Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| [risk] | H/M/L | H/M/L | [how to address] |

### Roll-out sketch

- **Phase 1 (MVP):** [what ships first]
- **Phase 2:** [next increment]
- **Phase 3+:** [aspirational]

### Stakeholders and approvals

| Role | Name | Approval needed on |
|---|---|---|
| Sponsor | [name] | Problem and MVP scope |
| Product owner | [name] | Requirements and stories |
| Tech lead | [name] | Application and NFR design |
| Security | [name] | Extension opt-ins, gates |
| QA lead | [name] | Build and test instructions |
```
