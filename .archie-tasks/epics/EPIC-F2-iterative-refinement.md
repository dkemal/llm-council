# EPIC: F2 - Iterative Refinement Loop (Stage 2.5)

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

Add an iterative refinement stage (Stage 2.5) where models can revise their initial responses based on peer critiques from Stage 2, producing deeper analysis that addresses counterarguments.

## Job Story

When **I see the initial responses from the council**
I want to **have models refine their answers based on peer critiques**
So I can **get deeper analysis that addresses counterarguments and edge cases**

## ODI Score: 15/20
- Importance: 9/10
- Satisfaction: 1/10
- Priority: P0 - Core innovation

## Success Criteria

1. Models receive relevant critiques and produce refined responses
2. Refined answers explicitly address critique points
3. Configurable iteration depth (1-3 rounds)
4. Each iteration round completes in <90 seconds
5. Clear UI showing evolution of each answer

---

## Task Breakdown

### Backend Tasks (9 tasks)

| Task ID | Name | Complexity | Dependencies |
|---------|------|------------|--------------|
| F2-BE-01 | Design Iteration State Management | M | None |
| F2-BE-02 | Extract Critiques from Stage 2 Rankings | M | None |
| F2-BE-03 | Create Refinement Prompt Builder | M | F2-BE-02 |
| F2-BE-04 | Implement stage2_5_refine_responses() | L | F2-BE-01, F2-BE-03 |
| F2-BE-05 | Add Iteration Depth Configuration | S | F2-BE-04 |
| F2-BE-06 | Implement Multi-Round Iteration Loop | M | F2-BE-04, F2-BE-05 |
| F2-BE-07 | Track Change Detection (No-Revision Cases) | S | F2-BE-04 |
| F2-BE-08 | Update run_full_council() for Iteration | M | F2-BE-06 |
| F2-BE-09 | Add SSE Events for Stage 2.5 | M | F2-BE-08 |

### Frontend Tasks (6 tasks)

| Task ID | Name | Complexity | Dependencies |
|---------|------|------------|--------------|
| F2-FE-01 | Design Iteration History UI Component | M | None |
| F2-FE-02 | Add "Enable Iteration" Toggle to ChatInterface | S | None |
| F2-FE-03 | Create Stage2_5 Component | M | F2-BE-09 |
| F2-FE-04 | Implement Collapsible Iteration History | M | F2-FE-01 |
| F2-FE-05 | Add Iteration Progress Indicator | S | F2-BE-09 |
| F2-FE-06 | Update App.jsx for Stage 2.5 Event Handling | M | F2-BE-09, F2-FE-03 |

### Integration Tasks (2 tasks)

| Task ID | Name | Complexity | Dependencies |
|---------|------|------------|--------------|
| F2-INT-01 | End-to-End Iteration Flow Testing | M | F2-BE-09, F2-FE-06 |
| F2-INT-02 | Performance Testing (Context Limits) | M | F2-INT-01 |

---

## Total Effort Estimate

- Small (S): 4 tasks x 2h = 8h
- Medium (M): 11 tasks x 4h = 44h
- Large (L): 1 task x 8h = 8h
- **Total: 60h (~7.5 days)**

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Context window overflow | Medium | High | Token tracking, truncation strategy |
| Diminishing returns on iterations | Medium | Medium | Smart termination conditions |
| Latency exceeds 90s/round | Medium | Medium | Model selection, parallel refinement |
| Models refuse to change position | Low | Low | Document unchanged stance as valid |

---

## Technical Considerations

### Context Management Strategy
- Track token usage per iteration
- Summarize previous iterations if approaching limit
- Prioritize recent critiques over historical context

### Termination Conditions
1. Max iteration rounds reached
2. No model changed position (convergence)
3. Quality delta below threshold
4. User manual stop

### State Model
```python
iteration_state = {
    "round": 1,
    "max_rounds": 2,
    "history": [
        {
            "round": 1,
            "critiques": {...},
            "refinements": {...},
            "changes_detected": True
        }
    ],
    "terminated_reason": None
}
```

---

## Dependencies on Other Epics

- **F1 (Structured Criteria)**: Refinement can be criterion-specific
- **F7 (Confidence)**: Track confidence changes across iterations

