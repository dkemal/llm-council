# EPIC: P1 Features - High-Level Overview

**Version**: 1.0.0
**Created**: 2026-01-02 12:15:00
**Last Updated**: 2026-01-02 12:15:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.prd/features/deliberation-improvements-v1.0.0.md`
**Agent**: product-manager

---

## P1 Features Summary

These features enhance the core experience after P0 (Structured Criteria + Iterative Refinement) is complete.

---

## F4: Decision Mode Templates

### Summary
Pre-configured templates for common decision types (API selection, vendor comparison, architecture choice) that pre-populate relevant criteria.

### ODI Score: 12/20

### High-Level Tasks

| Task | Description | Complexity | Validation |
|------|-------------|------------|------------|
| F4-BE-01 | Template data model and storage | S | Unit tests for CRUD |
| F4-BE-02 | Default templates library | S | Review templates with PM |
| F4-BE-03 | Template API endpoints | S | API tests |
| F4-FE-01 | Template selector component | M | Visual test in browser |
| F4-FE-02 | Template preview/apply flow | M | E2E flow test |
| F4-FE-03 | Save custom template flow | M | Save/load roundtrip |

### Key Validation Criteria
- 5+ default templates covering common use cases
- Users can customize templates before applying
- Users can save custom templates for reuse
- Templates load in <500ms

### Dependencies
- Requires F1 (Criteria Input) complete

---

## F5: Aggregate Scoring Matrix

### Summary
Visual matrix showing each option's score per criterion with color coding and drill-down capability.

### ODI Score: 13/20

### High-Level Tasks

| Task | Description | Complexity | Validation |
|------|-------------|------------|------------|
| F5-BE-01 | Score aggregation logic | M | Unit tests with mock data |
| F5-BE-02 | Consensus calculation | S | Verify std dev thresholds |
| F5-FE-01 | Matrix table component | L | Visual test with 5x10 matrix |
| F5-FE-02 | Cell drill-down modal | M | Click reveals model scores |
| F5-FE-03 | Sort/filter controls | S | Verify sorting works |

**Note**: F5-BE tasks overlap with F1-BE-07 - reuse that work

### Key Validation Criteria
- Matrix renders with 10 options x 20 criteria (max)
- Color coding clear (green/yellow/red)
- Hover shows per-model breakdown
- Sort by rank or total score works

### Dependencies
- Requires F1-BE-07 (Scoring Matrix Aggregator)

---

## F6: Table Stakes Disqualification

### Summary
Options failing must-have requirements are automatically disqualified with clear explanation.

### ODI Score: 11/20

### High-Level Tasks

| Task | Description | Complexity | Validation |
|------|-------------|------------|------------|
| F6-BE-01 | Disqualification logic | M | Unit tests for pass/fail |
| F6-BE-02 | All-disqualified handling | S | Warning message generation |
| F6-FE-01 | Disqualified section UI | S | Visual separation test |
| F6-FE-02 | DQ reason tooltip | S | Hover shows reason |

**Note**: F6-BE-01 overlaps with F1-BE-06 - reuse that work

### Key Validation Criteria
- Failing one Table Stake disqualifies option
- Disqualification reason clearly shown
- All-disqualified case provides guidance
- Manual override option (stretch)

### Dependencies
- Requires F1 (Table Stakes checkbox in criteria)

---

## F8: Decision Export

### Summary
Export deliberation results as PDF, Markdown, or JSON for sharing and documentation.

### ODI Score: 11/20

### High-Level Tasks

| Task | Description | Complexity | Validation |
|------|-------------|------------|------------|
| F8-BE-01 | Export data formatter | M | JSON schema validation |
| F8-BE-02 | Markdown generator | M | Render markdown in viewer |
| F8-BE-03 | PDF generation (optional) | L | PDF opens correctly |
| F8-FE-01 | Export button + format selector | S | UI test |
| F8-FE-02 | Export preview modal | M | Preview before download |
| F8-FE-03 | Download trigger | S | File downloads correctly |

### Key Validation Criteria
- Export includes: question, criteria, options, matrix, recommendation
- Markdown renders correctly in GitHub/Notion
- PDF is professionally formatted (if implemented)
- Export completes in <10 seconds

### Dependencies
- Can start after F1+F5 (needs scoring matrix data)

---

## P1 Implementation Order

Recommended sequence based on dependencies and value:

1. **F5** (Scoring Matrix UI) - Builds on F1-BE-07, high visual impact
2. **F6** (Table Stakes) - Small addition to F1, low effort
3. **F4** (Templates) - Accelerates user adoption
4. **F8** (Export) - Enterprise requirement, can be last

---

## Total P1 Effort Estimate

| Feature | Backend | Frontend | Total |
|---------|---------|----------|-------|
| F4 Templates | 6h | 12h | 18h |
| F5 Scoring Matrix | 6h (shared with F1) | 16h | 22h |
| F6 Table Stakes | 4h (shared with F1) | 4h | 8h |
| F8 Export | 16h | 8h | 24h |
| **Total** | **32h** | **40h** | **72h (~9 days)** |

---

## P2 Features (Post-MVP)

### F3: Evidence Citations
- Extract citations from model outputs
- Link verification (optional)
- Complexity: L
- Defer due to RAG integration needs

### F7: Confidence Scores
- Cross-model agreement analysis
- Uncertainty indicators
- Complexity: S
- Nice-to-have polish

