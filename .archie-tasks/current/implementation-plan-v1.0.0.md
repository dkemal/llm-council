# LLM Council - Deliberation Improvements Implementation Plan

**Version**: 1.0.0
**Created**: 2026-01-02 12:30:00
**Last Updated**: 2026-01-02 12:30:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.prd/features/deliberation-improvements-v1.0.0.md`
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/epics/EPIC-F2-iterative-refinement.md`
  - `/.archie-tasks/epics/EPIC-P1-features-overview.md`
**Agent**: product-manager

---

## Executive Summary

This plan details the implementation of deliberation improvements for LLM Council, transforming it from a single-pass voting system into an iterative deliberation platform with structured evaluation criteria.

**Total Effort**: ~200 hours (~25 days)
**Priority**: P0 features first, then P1

---

## Phase Overview

| Phase | Features | Duration | Milestone |
|-------|----------|----------|-----------|
| Phase 1 | F1: Structured Criteria (Backend) | Week 1 | Criteria-aware prompts working |
| Phase 2 | F1: Structured Criteria (Frontend) | Week 2 | Full criteria flow testable |
| Phase 3 | F2: Iterative Refinement | Weeks 3-4 | Stage 2.5 working end-to-end |
| Phase 4 | P1: Polish & Enhancement | Weeks 5-6 | Production-ready MVP |

---

## Phase 1: F1 Backend (Week 1)

### Goal
Backend supports criteria-aware deliberation with score extraction.

### Tasks in Order

```
Day 1-2:
  F1-BE-01: Criteria Data Schema         [S, 2h]
  F1-BE-02: Criteria Validation          [S, 2h]

Day 3:
  F1-BE-03: Criterion-Aware Prompts      [M, 4h]

Day 4:
  F1-BE-04: Stage 1 Criteria Integration [M, 4h]

Day 5:
  F1-BE-05: Score Extraction Parser      [L, 8h]
```

### Validation Checkpoint
- [ ] Can send criteria with message request
- [ ] Stage 1 prompts include all criteria
- [ ] Scores can be extracted from responses
- [ ] All unit tests pass

### Files Created/Modified
```
NEW:  /backend/models.py
NEW:  /backend/validation.py
NEW:  /backend/prompts.py
NEW:  /backend/parsing.py
MOD:  /backend/council.py
```

---

## Phase 2: F1 Frontend + Backend Completion (Week 2)

### Goal
Complete criteria flow with UI and scoring matrix.

### Tasks in Order

```
Day 1:
  F1-FE-01: Criteria Input UI Design     [M, 4h]

Day 2:
  F1-FE-02: Criteria Editor (Drag/Reorder) [M, 4h]
  F1-FE-03: Weight Selection             [S, 2h]
  F1-FE-04: Table Stakes Toggle          [S, 2h]

Day 3:
  F1-BE-06: Table Stakes Logic           [M, 4h]
  F1-BE-07: Scoring Matrix Aggregator    [M, 4h]

Day 4:
  F1-BE-08: API Endpoints Update         [M, 4h]
  F1-FE-05: ChatInterface Integration    [M, 4h]

Day 5:
  F1-FE-06: Scoring Matrix Component     [L, 8h]
  F1-FE-07: Stage1 Criterion Display     [M, 4h]

Day 6:
  F1-INT-01: Connect UI to Backend       [M, 4h]
  F1-INT-02: E2E Testing                 [M, 4h]
```

### Validation Checkpoint
- [ ] Can define criteria in UI
- [ ] Can set weights and table stakes
- [ ] Deliberation uses criteria prompts
- [ ] Scoring matrix displays correctly
- [ ] Disqualified options shown appropriately

### Files Created/Modified
```
NEW:  /frontend/src/components/CriteriaInput.jsx
NEW:  /frontend/src/components/CriteriaInput.css
NEW:  /frontend/src/components/ScoringMatrix.jsx
NEW:  /frontend/src/components/ScoringMatrix.css
NEW:  /backend/aggregation.py
MOD:  /backend/main.py
MOD:  /frontend/src/App.jsx
MOD:  /frontend/src/api.js
MOD:  /frontend/src/components/ChatInterface.jsx
MOD:  /frontend/src/components/Stage1.jsx
```

---

## Phase 3: F2 Iterative Refinement (Weeks 3-4)

### Goal
Implement Stage 2.5 refinement loop with full UI support.

### Week 3: Backend

```
Day 1:
  F2-BE-01: Iteration State Management   [M, 4h]
  F2-BE-02: Critique Extraction          [M, 4h]

Day 2:
  F2-BE-03: Refinement Prompt Builder    [M, 4h]

Day 3-4:
  F2-BE-04: stage2_5_refine_responses()  [L, 8h]

Day 5:
  F2-BE-05: Iteration Depth Config       [S, 2h]
  F2-BE-06: Multi-Round Loop             [M, 4h]
  F2-BE-07: Change Detection             [S, 2h]
```

### Week 4: Integration + Frontend

```
Day 1:
  F2-BE-08: Update run_full_council()    [M, 4h]
  F2-BE-09: SSE Events for Stage 2.5     [M, 4h]

Day 2:
  F2-FE-01: Iteration History UI         [M, 4h]
  F2-FE-02: Enable Iteration Toggle      [S, 2h]

Day 3:
  F2-FE-03: Stage2_5 Component           [M, 4h]
  F2-FE-04: Collapsible History          [M, 4h]

Day 4:
  F2-FE-05: Iteration Progress           [S, 2h]
  F2-FE-06: App.jsx Event Handling       [M, 4h]

Day 5:
  F2-INT-01: E2E Iteration Testing       [M, 4h]
  F2-INT-02: Performance Testing         [M, 4h]
```

### Validation Checkpoint
- [ ] Can enable/disable iteration via UI
- [ ] Stage 2.5 shows refinements
- [ ] History shows evolution of answers
- [ ] Iteration stops on convergence
- [ ] Each round < 90 seconds

### Files Created/Modified
```
NEW:  /backend/iteration.py
NEW:  /backend/critique.py
NEW:  /frontend/src/components/Stage2_5.jsx
NEW:  /frontend/src/components/Stage2_5.css
NEW:  /frontend/src/components/IterationHistory.jsx
MOD:  /backend/council.py
MOD:  /backend/main.py
MOD:  /frontend/src/App.jsx
MOD:  /frontend/src/api.js
MOD:  /frontend/src/components/ChatInterface.jsx
```

---

## Phase 4: P1 Features (Weeks 5-6)

### Week 5: F5 Scoring Matrix Polish + F6 Table Stakes

```
Day 1-2:
  F5-FE-02: Cell Drill-Down Modal        [M, 4h]
  F5-FE-03: Sort/Filter Controls         [S, 2h]

Day 3:
  F6-FE-01: Disqualified Section         [S, 2h]
  F6-FE-02: DQ Reason Tooltip            [S, 2h]

Day 4-5:
  F4-BE-01: Template Data Model          [S, 2h]
  F4-BE-02: Default Templates Library    [S, 2h]
  F4-BE-03: Template API                 [S, 2h]
```

### Week 6: F4 Templates + F8 Export

```
Day 1-2:
  F4-FE-01: Template Selector            [M, 4h]
  F4-FE-02: Template Apply Flow          [M, 4h]
  F4-FE-03: Save Custom Template         [M, 4h]

Day 3-4:
  F8-BE-01: Export Data Formatter        [M, 4h]
  F8-BE-02: Markdown Generator           [M, 4h]
  F8-FE-01: Export Button                [S, 2h]
  F8-FE-02: Export Preview               [M, 4h]
  F8-FE-03: Download Trigger             [S, 2h]

Day 5:
  Final Testing & Bug Fixes              [4h]
  Documentation Updates                  [2h]
```

### Validation Checkpoint
- [ ] Templates pre-populate criteria correctly
- [ ] Export produces valid Markdown
- [ ] All features work together
- [ ] Performance meets targets

---

## Dependency Graph

```
F1-BE-01 ─┬─> F1-BE-02
          └─> F1-BE-03 ──> F1-BE-04 ──> F1-BE-05 ──┬─> F1-BE-06 ──> F1-BE-07 ──> F1-BE-08
                                                    │
F1-FE-01 ──┬─> F1-FE-02 ──┐                        │
           ├─> F1-FE-03 ──┼─> F1-FE-05 ────────────┼─> F1-INT-01 ──> F1-INT-02
           └─> F1-FE-04 ──┘                        │
                                                    └─> F1-FE-06 ──┘

F2-BE-01 ──┬─> F2-BE-04 ──> F2-BE-06 ──> F2-BE-08 ──> F2-BE-09
F2-BE-02 ──┤                                           │
F2-BE-03 ──┘                                           v
                                                   F2-FE-03 ──> F2-FE-06 ──> F2-INT-01
F2-FE-01 ──> F2-FE-04
F2-FE-02
F2-FE-05

F1-BE-07 ──> F5-FE-01 ──> F5-FE-02
F1-BE-06 ──> F6-FE-01

F1-FE-01 ──> F4-FE-01 ──> F4-FE-02
F1-BE-07 ──> F8-BE-01 ──> F8-BE-02 ──> F8-FE-02
```

---

## Risk Mitigation

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| Score extraction unreliable | Multiple parsing strategies, fallbacks | Manual scoring UI |
| Context window limits | Token tracking, summarization | Reduce iteration rounds |
| API latency > 90s/round | Parallel queries, model selection | Lower model count |
| UI complexity | Progressive disclosure | Simplify to essential features |

---

## Success Metrics

### Phase 1-2 (F1)
- [ ] Criteria-aware responses in 100% of test cases
- [ ] Score extraction success rate > 80%
- [ ] UI usability score > 4/5

### Phase 3 (F2)
- [ ] Refinement improves responses in > 70% of cases
- [ ] Iteration round < 90 seconds
- [ ] No context overflow errors

### Phase 4 (P1)
- [ ] Templates reduce setup time by > 50%
- [ ] Export used in > 40% of deliberations
- [ ] Overall satisfaction > 4/5

---

## Getting Started

### Prerequisites
- Python 3.11+ with backend dependencies
- Node.js 18+ with frontend dependencies
- OpenRouter API key configured

### First Task
Start with `F1-BE-01: Criteria Data Schema`:
```bash
cd /Users/djamil/Github/llm-counsel/llm-council
# Create /backend/models.py with Pydantic models
# Run: python -c "from backend.models import Criterion; print('OK')"
```

---

## Task Files Reference

### P0: Structured Criteria (F1)
- `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
- `/.archie-tasks/backlog/F1-BE-01-criteria-data-schema.md`
- `/.archie-tasks/backlog/F1-BE-02-criteria-validation.md`
- `/.archie-tasks/backlog/F1-BE-03-criterion-aware-prompts.md`
- `/.archie-tasks/backlog/F1-BE-04-stage1-criteria-integration.md`
- `/.archie-tasks/backlog/F1-BE-05-score-extraction.md`
- `/.archie-tasks/backlog/F1-BE-06-table-stakes-logic.md`
- `/.archie-tasks/backlog/F1-BE-07-scoring-matrix.md`
- `/.archie-tasks/backlog/F1-BE-08-api-endpoints.md`
- `/.archie-tasks/backlog/F1-FE-01-criteria-ui-design.md`
- `/.archie-tasks/backlog/F1-FE-06-scoring-matrix-component.md`

### P0: Iterative Refinement (F2)
- `/.archie-tasks/epics/EPIC-F2-iterative-refinement.md`
- `/.archie-tasks/backlog/F2-BE-01-iteration-state.md`
- `/.archie-tasks/backlog/F2-BE-02-critique-extraction.md`
- `/.archie-tasks/backlog/F2-BE-04-stage2_5-implementation.md`

### P1: Enhancement Features
- `/.archie-tasks/epics/EPIC-P1-features-overview.md`

