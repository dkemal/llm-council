# Task: F1-BE-02 - Create Criteria Validation Module

**Version**: 1.0.0
**Created**: 2026-01-02 11:15:00
**Last Updated**: 2026-01-02 11:15:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/backlog/F1-BE-01-criteria-data-schema.md`
**Agent**: product-manager

---

## Task Summary

Create validation functions for criteria input, including conflict detection, completeness checks, and helpful error messages.

## Complexity: S (2 hours)

## Dependencies
- F1-BE-01 (Criteria Data Schema)

## Blocked By
- F1-BE-01

## Blocks
- F1-BE-03, F1-BE-08

---

## Technical Specification

### File Location
`/backend/validation.py` (new file)

### Functions to Implement

```python
from typing import List, Tuple, Optional
from .models import EvaluationCriteria, Criterion, CriterionType

def validate_criteria(criteria: EvaluationCriteria) -> Tuple[bool, List[str]]:
    """
    Validate criteria set for logical consistency.

    Returns:
        Tuple of (is_valid, list_of_warnings_or_errors)
    """
    errors = []
    warnings = []

    # Check for minimum criteria
    if len(criteria.criteria) < 1:
        errors.append("At least one criterion is required")

    # Check table stakes ratio
    table_stakes = [c for c in criteria.criteria if c.type == CriterionType.TABLE_STAKES]
    if len(table_stakes) == len(criteria.criteria):
        warnings.append("All criteria are Table Stakes - consider adding scored criteria for nuanced comparison")

    # Check weight distribution
    p0_count = sum(1 for c in criteria.criteria if c.weight.value == "P0")
    if p0_count > len(criteria.criteria) * 0.5:
        warnings.append("More than 50% of criteria marked P0 - consider prioritizing")

    # Check for options if comparison mode
    if criteria.options and len(criteria.options) < 2:
        errors.append("Comparison mode requires at least 2 options")

    return (len(errors) == 0, errors + warnings)


def detect_criteria_conflicts(criteria: EvaluationCriteria) -> List[str]:
    """
    Detect potentially conflicting criteria.

    Example conflicts:
    - "Lowest Cost" vs "Premium Support"
    - "Maximum Features" vs "Simplicity"
    """
    conflicts = []

    conflict_pairs = [
        (["cost", "cheap", "budget", "price"], ["premium", "enterprise", "comprehensive"]),
        (["simple", "minimal", "lean"], ["feature", "comprehensive", "complete"]),
        (["fast", "speed", "performance"], ["thorough", "comprehensive", "complete"]),
    ]

    criterion_names = [c.name.lower() for c in criteria.criteria]

    for group_a, group_b in conflict_pairs:
        found_a = [n for n in criterion_names if any(term in n for term in group_a)]
        found_b = [n for n in criterion_names if any(term in n for term in group_b)]

        if found_a and found_b:
            conflicts.append(
                f"Potential conflict: '{found_a[0]}' may conflict with '{found_b[0]}'. "
                "Consider clarifying priority."
            )

    return conflicts


def suggest_missing_criteria(criteria: EvaluationCriteria, domain: str = "general") -> List[str]:
    """
    Suggest commonly important criteria that might be missing.

    Args:
        criteria: Current criteria set
        domain: "api_selection", "vendor", "architecture", "general"
    """
    domain_suggestions = {
        "api_selection": ["Pricing", "Documentation Quality", "Rate Limits", "SDK Support", "SLA"],
        "vendor": ["Support Response Time", "Security Compliance", "Data Residency", "Contract Flexibility"],
        "architecture": ["Scalability", "Maintainability", "Team Expertise", "Migration Complexity"],
        "general": ["Cost", "Quality", "Timeline", "Risk"]
    }

    existing = {c.name.lower() for c in criteria.criteria}
    suggestions = domain_suggestions.get(domain, domain_suggestions["general"])

    missing = [s for s in suggestions if s.lower() not in existing]
    return missing[:3]  # Return top 3 suggestions


def normalize_weight(criteria: EvaluationCriteria) -> EvaluationCriteria:
    """
    Normalize weights so they sum to 1.0 for percentage calculations.
    """
    total_weight = sum(c.numeric_weight for c in criteria.criteria)

    for c in criteria.criteria:
        c.normalized_weight = c.numeric_weight / total_weight

    return criteria
```

---

## Acceptance Criteria

- [ ] `validate_criteria()` returns clear error/warning messages
- [ ] `detect_criteria_conflicts()` identifies common trade-off conflicts
- [ ] `suggest_missing_criteria()` provides domain-aware suggestions
- [ ] All validation completes in <100ms for 20 criteria
- [ ] Error messages are user-friendly (no technical jargon)

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_validation.py

def test_validate_empty_criteria():
    """Should error on empty criteria"""
    criteria = EvaluationCriteria(criteria=[])
    is_valid, messages = validate_criteria(criteria)
    assert not is_valid
    assert "At least one criterion" in messages[0]

def test_detect_cost_vs_premium_conflict():
    """Should detect cost vs premium conflict"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Lowest Cost"),
        Criterion(id="c2", name="Premium Support")
    ])
    conflicts = detect_criteria_conflicts(criteria)
    assert len(conflicts) == 1
    assert "conflict" in conflicts[0].lower()

def test_suggest_missing_api_criteria():
    """Should suggest API-relevant criteria"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Accuracy")
    ])
    suggestions = suggest_missing_criteria(criteria, domain="api_selection")
    assert "Pricing" in suggestions or "Documentation" in suggestions

def test_validate_all_table_stakes_warning():
    """Should warn when all criteria are table stakes"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="GDPR", type=CriterionType.TABLE_STAKES),
        Criterion(id="c2", name="SOC2", type=CriterionType.TABLE_STAKES)
    ])
    is_valid, messages = validate_criteria(criteria)
    assert is_valid  # Warning, not error
    assert any("Table Stakes" in m for m in messages)
```

### Manual Verification

1. Test validation with edge cases in Python REPL
2. Verify error messages are understandable to non-technical users
3. Time validation with 20 criteria (must be <100ms)

---

## Implementation Notes

- Keep validation fast - no external API calls
- Consider i18n for error messages (future enhancement)
- Conflict detection is heuristic, not comprehensive

