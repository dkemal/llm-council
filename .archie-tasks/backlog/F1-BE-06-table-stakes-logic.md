# Task: F1-BE-06 - Add Table Stakes Disqualification Logic

**Version**: 1.0.0
**Created**: 2026-01-02 11:30:00
**Last Updated**: 2026-01-02 11:30:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/backlog/F1-BE-05-score-extraction.md`
**Agent**: product-manager

---

## Task Summary

Implement logic to automatically disqualify options that fail Table Stakes criteria, with clear reporting of disqualification reasons.

## Complexity: M (4 hours)

## Dependencies
- F1-BE-05 (Score Extraction Parser)

## Blocked By
- F1-BE-05

## Blocks
- F1-BE-07

---

## Technical Specification

### File to Modify
`/backend/parsing.py` (add functions)

### Functions to Implement

```python
from typing import List, Tuple
from .models import (
    EvaluationCriteria, CriterionType, OptionScores,
    CriterionScore
)

def apply_table_stakes_disqualification(
    options: List[OptionScores],
    criteria: EvaluationCriteria
) -> Tuple[List[OptionScores], List[OptionScores]]:
    """
    Separate options into qualified and disqualified based on Table Stakes.

    Args:
        options: List of option scores
        criteria: Criteria including table stakes definitions

    Returns:
        Tuple of (qualified_options, disqualified_options)
    """
    qualified = []
    disqualified = []

    # Get table stakes criteria
    table_stakes = {
        c.id: c for c in criteria.criteria
        if c.type == CriterionType.TABLE_STAKES
    }

    if not table_stakes:
        # No table stakes - all options qualify
        return options, []

    for option in options:
        failures = check_table_stakes_failures(option, table_stakes)

        if failures:
            option.disqualified = True
            option.disqualification_reason = format_disqualification_reason(failures)
            disqualified.append(option)
        else:
            qualified.append(option)

    return qualified, disqualified


def check_table_stakes_failures(
    option: OptionScores,
    table_stakes: dict
) -> List[Tuple[str, str]]:
    """
    Check which table stakes an option fails.

    Returns:
        List of (criterion_name, failure_reason) tuples
    """
    failures = []

    # Build map of option's scores
    score_map = {s.criterion_id: s for s in option.scores}

    for criterion_id, criterion in table_stakes.items():
        score = score_map.get(criterion_id)

        if score is None:
            # Missing score for table stakes = failure
            failures.append((
                criterion.name,
                "No assessment provided"
            ))
        elif score.passed is False:
            # Explicit FAIL
            failures.append((
                criterion.name,
                score.evidence or "Failed requirement"
            ))
        elif score.passed is None and score.score is not None:
            # Numeric score provided for table stakes - interpret <5 as fail
            if score.score < 5:
                failures.append((
                    criterion.name,
                    f"Score {score.score}/10 below threshold"
                ))

    return failures


def format_disqualification_reason(
    failures: List[Tuple[str, str]]
) -> str:
    """Format failures into user-friendly message."""
    if len(failures) == 1:
        name, reason = failures[0]
        return f"Failed Table Stakes: {name} - {reason}"

    reasons = [f"{name}: {reason}" for name, reason in failures]
    return f"Failed {len(failures)} Table Stakes requirements:\n- " + "\n- ".join(reasons)


def check_all_options_disqualified(
    disqualified: List[OptionScores],
    total_options: int
) -> dict:
    """
    Check if all options are disqualified and provide guidance.

    Returns:
        Dict with status and recommendations
    """
    if len(disqualified) == total_options:
        # Find most common failure
        failure_counts = {}
        for opt in disqualified:
            if opt.disqualification_reason:
                # Extract criterion names from reason
                import re
                criteria_mentioned = re.findall(r'Failed.*?: (\w+)', opt.disqualification_reason)
                for c in criteria_mentioned:
                    failure_counts[c] = failure_counts.get(c, 0) + 1

        most_common = max(failure_counts.items(), key=lambda x: x[1])[0] if failure_counts else None

        return {
            "all_disqualified": True,
            "message": "All options failed to meet Table Stakes requirements",
            "recommendation": f"Consider reviewing the '{most_common}' requirement or exploring additional options" if most_common else "Consider reviewing Table Stakes criteria",
            "failure_summary": failure_counts
        }

    return {"all_disqualified": False}


def generate_disqualification_summary(
    qualified: List[OptionScores],
    disqualified: List[OptionScores]
) -> dict:
    """
    Generate summary for UI display.

    Returns:
        Dict with counts and details for display
    """
    return {
        "total_options": len(qualified) + len(disqualified),
        "qualified_count": len(qualified),
        "disqualified_count": len(disqualified),
        "qualified_options": [opt.option_name for opt in qualified],
        "disqualified_options": [
            {
                "name": opt.option_name,
                "reason": opt.disqualification_reason
            }
            for opt in disqualified
        ]
    }
```

---

## Acceptance Criteria

- [ ] Options failing any Table Stakes criterion are marked disqualified
- [ ] Disqualification reason clearly states which criterion failed
- [ ] Missing Table Stakes assessments treated as failures
- [ ] Numeric scores <5 on Table Stakes treated as failures
- [ ] When all options disqualified, provides helpful guidance
- [ ] Summary includes qualified/disqualified counts for UI

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_disqualification.py

def test_single_table_stakes_failure():
    """Option failing one table stakes should be disqualified"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="GDPR", type=CriterionType.TABLE_STAKES),
        Criterion(id="c2", name="Quality", type=CriterionType.SCORED)
    ])

    options = [
        OptionScores(option_name="Opt A", scores=[
            CriterionScore(criterion_id="c1", passed=True),
            CriterionScore(criterion_id="c2", score=8)
        ]),
        OptionScores(option_name="Opt B", scores=[
            CriterionScore(criterion_id="c1", passed=False),
            CriterionScore(criterion_id="c2", score=9)
        ])
    ]

    qualified, disqualified = apply_table_stakes_disqualification(options, criteria)

    assert len(qualified) == 1
    assert qualified[0].option_name == "Opt A"
    assert len(disqualified) == 1
    assert disqualified[0].option_name == "Opt B"
    assert "GDPR" in disqualified[0].disqualification_reason


def test_missing_table_stakes_score():
    """Missing table stakes assessment should disqualify"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="SOC2", type=CriterionType.TABLE_STAKES)
    ])

    options = [
        OptionScores(option_name="Opt A", scores=[])  # No scores
    ]

    qualified, disqualified = apply_table_stakes_disqualification(options, criteria)

    assert len(disqualified) == 1
    assert "No assessment" in disqualified[0].disqualification_reason


def test_low_numeric_score_on_table_stakes():
    """Low numeric score on table stakes should disqualify"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Security", type=CriterionType.TABLE_STAKES)
    ])

    options = [
        OptionScores(option_name="Opt A", scores=[
            CriterionScore(criterion_id="c1", score=3)  # Below threshold
        ])
    ]

    qualified, disqualified = apply_table_stakes_disqualification(options, criteria)

    assert len(disqualified) == 1
    assert "below threshold" in disqualified[0].disqualification_reason.lower()


def test_all_options_disqualified_guidance():
    """Should provide guidance when all options fail"""
    disqualified = [
        OptionScores(option_name="A", disqualification_reason="Failed: GDPR"),
        OptionScores(option_name="B", disqualification_reason="Failed: GDPR")
    ]

    result = check_all_options_disqualified(disqualified, 2)

    assert result["all_disqualified"] == True
    assert "recommendation" in result


def test_no_table_stakes_all_qualify():
    """Without table stakes, all options qualify"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Quality", type=CriterionType.SCORED)
    ])

    options = [
        OptionScores(option_name="A", scores=[]),
        OptionScores(option_name="B", scores=[])
    ]

    qualified, disqualified = apply_table_stakes_disqualification(options, criteria)

    assert len(qualified) == 2
    assert len(disqualified) == 0
```

### Manual Verification

1. Test with mix of passing/failing options
2. Verify disqualification reasons are user-friendly
3. Test edge case: all options disqualified
4. Test edge case: no table stakes defined

---

## Implementation Notes

- Keep threshold (5) configurable for future
- Consider "partial pass" states in future enhancement
- Disqualification is deterministic, not probabilistic

