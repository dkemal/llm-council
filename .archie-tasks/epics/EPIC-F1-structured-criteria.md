# EPIC: F1 - Structured Evaluation Criteria

**Version**: 1.0.0
**Created**: 2026-01-02 11:00:00
**Last Updated**: 2026-01-02 11:00:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.prd/features/deliberation-improvements-v1.0.0.md`
  - `/CLAUDE.md`
**Agent**: product-manager

---

## Epic Summary

Transform Stage 1 from free-form query handling to structured criterion-aware evaluation, enabling users to define weighted evaluation criteria that guide model responses.

## Job Story

When **I'm making a technical decision with multiple competing options**
I want to **define specific evaluation criteria with importance weights**
So I can **get systematic analysis against each criterion, not generic comparisons**

## ODI Score: 16/20
- Importance: 9/10
- Satisfaction: 2/10
- Priority: P0 - Core differentiator

## Success Criteria

1. Users can define 1-20 criteria with weights (P0/P1/P2 or 1-10 scale)
2. Each Stage 1 response explicitly addresses every criterion
3. Table Stakes criteria can disqualify options
4. Scoring matrix displays option scores per criterion
5. Criteria parsing completes in <2 seconds

---

## Task Breakdown

### Backend Tasks (8 tasks)

| Task ID | Name | Complexity | Dependencies |
|---------|------|------------|--------------|
| F1-BE-01 | Define Criteria Data Schema | S | None |
| F1-BE-02 | Create Criteria Validation Module | S | F1-BE-01 |
| F1-BE-03 | Implement Criterion-Aware Prompt Builder | M | F1-BE-01 |
| F1-BE-04 | Modify Stage 1 to Accept Criteria | M | F1-BE-03 |
| F1-BE-05 | Implement Score Extraction Parser | L | F1-BE-04 |
| F1-BE-06 | Add Table Stakes Disqualification Logic | M | F1-BE-05 |
| F1-BE-07 | Create Scoring Matrix Aggregator | M | F1-BE-05, F1-BE-06 |
| F1-BE-08 | Update API Endpoints for Criteria | M | F1-BE-07 |

### Frontend Tasks (7 tasks)

| Task ID | Name | Complexity | Dependencies |
|---------|------|------------|--------------|
| F1-FE-01 | Design Criteria Input UI Component | M | None |
| F1-FE-02 | Implement Criteria Editor with Drag/Reorder | M | F1-FE-01 |
| F1-FE-03 | Add Weight Selection Controls | S | F1-FE-01 |
| F1-FE-04 | Create Table Stakes Toggle | S | F1-FE-01 |
| F1-FE-05 | Update ChatInterface to Include Criteria | M | F1-FE-02, F1-FE-03, F1-FE-04 |
| F1-FE-06 | Create Scoring Matrix Component | L | F1-BE-07 |
| F1-FE-07 | Update Stage1 Component for Criterion Display | M | F1-BE-04 |

### Integration Tasks (2 tasks)

| Task ID | Name | Complexity | Dependencies |
|---------|------|------------|--------------|
| F1-INT-01 | Connect Criteria UI to Backend API | M | F1-BE-08, F1-FE-05 |
| F1-INT-02 | End-to-End Criteria Flow Testing | M | F1-INT-01 |

---

## Total Effort Estimate

- Small (S): 4 tasks x 2h = 8h
- Medium (M): 10 tasks x 4h = 40h
- Large (L): 2 tasks x 8h = 16h
- **Total: 64h (~8 days)**

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Models ignore criteria in responses | Medium | High | Strict prompt engineering, validation step |
| Score extraction fails for varied formats | High | Medium | Fallback parsing, manual override UI |
| UI complexity overwhelms users | Medium | Medium | Progressive disclosure, templates |

---

## Dependencies on Other Epics

- **F5 (Scoring Matrix)**: F1-FE-06 is shared foundation
- **F6 (Table Stakes)**: F1-BE-06 provides core logic
- **F4 (Templates)**: Built on top of F1 criteria schema

