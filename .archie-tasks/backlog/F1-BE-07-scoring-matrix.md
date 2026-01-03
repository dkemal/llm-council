# Task: F1-BE-07 - Create Scoring Matrix Aggregator

**Version**: 1.0.0
**Created**: 2026-01-02 11:30:00
**Last Updated**: 2026-01-02 11:30:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/backlog/F1-BE-05-score-extraction.md`
  - `/.archie-tasks/backlog/F1-BE-06-table-stakes-logic.md`
**Agent**: product-manager

---

## Task Summary

Create aggregation logic to combine scores from multiple models into a unified scoring matrix with consensus tracking.

## Complexity: M (4 hours)

## Dependencies
- F1-BE-05 (Score Extraction Parser)
- F1-BE-06 (Table Stakes Logic)

## Blocked By
- F1-BE-05, F1-BE-06

## Blocks
- F1-BE-08, F1-FE-06

---

## Technical Specification

### File Location
`/backend/aggregation.py` (new file)

### Data Models

```python
from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class ConsensusLevel(str, Enum):
    HIGH = "high"       # Std dev < 1.0
    MEDIUM = "medium"   # Std dev 1.0-2.0
    LOW = "low"         # Std dev > 2.0

class AggregatedCriterionScore(BaseModel):
    """Aggregated score for one criterion on one option."""
    criterion_id: str
    criterion_name: str
    average_score: Optional[float]
    min_score: Optional[float]
    max_score: Optional[float]
    std_dev: Optional[float]
    consensus: ConsensusLevel
    model_scores: Dict[str, float]  # model_name -> score
    pass_count: Optional[int]  # For table stakes
    fail_count: Optional[int]

class AggregatedOptionScore(BaseModel):
    """Aggregated scores for one option across all criteria."""
    option_name: str
    criterion_scores: List[AggregatedCriterionScore]
    total_weighted_score: float
    rank: int
    disqualified: bool = False
    disqualification_reason: Optional[str] = None

class ScoringMatrix(BaseModel):
    """Complete scoring matrix for display."""
    options: List[AggregatedOptionScore]
    criteria: List[dict]  # Criteria metadata for headers
    recommendation: Optional[str]
    all_disqualified_warning: Optional[str]
```

### Functions to Implement

```python
from typing import List, Dict
from statistics import mean, stdev
from .models import EvaluationCriteria, OptionScores, CriterionType
from .parsing import (
    extract_scores_from_response,
    calculate_weighted_scores,
    apply_table_stakes_disqualification
)

def aggregate_model_scores(
    stage1_results: List[Dict],
    criteria: EvaluationCriteria
) -> ScoringMatrix:
    """
    Aggregate scores from all models into unified matrix.

    Args:
        stage1_results: Results from stage 1 (list of {model, response})
        criteria: Evaluation criteria

    Returns:
        ScoringMatrix with aggregated scores
    """
    # Extract scores from each model's response
    model_scores = {}
    for result in stage1_results:
        model_name = result['model']
        response_text = result['response']

        option_scores = extract_scores_from_response(response_text, criteria)
        model_scores[model_name] = option_scores

    # Get all unique options across models
    all_options = set()
    for scores_list in model_scores.values():
        for option_score in scores_list:
            all_options.add(option_score.option_name)

    # Aggregate scores per option
    aggregated_options = []
    for option_name in all_options:
        aggregated = aggregate_option_scores(
            option_name, model_scores, criteria
        )
        aggregated_options.append(aggregated)

    # Apply table stakes disqualification
    qualified, disqualified = separate_by_qualification(
        aggregated_options, criteria
    )

    # Calculate ranks for qualified options
    qualified.sort(key=lambda x: x.total_weighted_score, reverse=True)
    for i, opt in enumerate(qualified):
        opt.rank = i + 1

    # Disqualified get rank = None
    for opt in disqualified:
        opt.rank = len(qualified) + 1  # Below all qualified

    # Build matrix
    all_options_ranked = qualified + disqualified

    # Check if all disqualified
    warning = None
    if len(disqualified) == len(all_options_ranked):
        warning = "All options failed Table Stakes requirements. Consider reviewing criteria or adding more options."

    # Generate recommendation
    recommendation = None
    if qualified:
        top = qualified[0]
        if len(qualified) > 1:
            second = qualified[1]
            margin = top.total_weighted_score - second.total_weighted_score
            if margin > 1.0:
                recommendation = f"Strong recommendation: {top.option_name} (leads by {margin:.1f} points)"
            else:
                recommendation = f"Close call between {top.option_name} and {second.option_name}"
        else:
            recommendation = f"Recommendation: {top.option_name} (only qualified option)"

    return ScoringMatrix(
        options=all_options_ranked,
        criteria=[{"id": c.id, "name": c.name, "type": c.type.value, "weight": c.weight.value}
                  for c in criteria.criteria],
        recommendation=recommendation,
        all_disqualified_warning=warning
    )


def aggregate_option_scores(
    option_name: str,
    model_scores: Dict[str, List[OptionScores]],
    criteria: EvaluationCriteria
) -> AggregatedOptionScore:
    """
    Aggregate scores for a single option across all models.
    """
    criterion_aggregates = []

    for criterion in criteria.criteria:
        scores_for_criterion = []
        model_score_map = {}
        pass_count = 0
        fail_count = 0

        for model_name, option_list in model_scores.items():
            # Find this option in model's scores
            for opt in option_list:
                if opt.option_name == option_name:
                    # Find score for this criterion
                    for score in opt.scores:
                        if score.criterion_id == criterion.id:
                            if score.score is not None:
                                scores_for_criterion.append(score.score)
                                model_score_map[model_name] = score.score
                            if score.passed is True:
                                pass_count += 1
                            elif score.passed is False:
                                fail_count += 1
                            break
                    break

        # Calculate aggregates
        avg = mean(scores_for_criterion) if scores_for_criterion else None
        min_s = min(scores_for_criterion) if scores_for_criterion else None
        max_s = max(scores_for_criterion) if scores_for_criterion else None
        std = stdev(scores_for_criterion) if len(scores_for_criterion) > 1 else 0.0

        # Determine consensus level
        if std is not None:
            if std < 1.0:
                consensus = ConsensusLevel.HIGH
            elif std < 2.0:
                consensus = ConsensusLevel.MEDIUM
            else:
                consensus = ConsensusLevel.LOW
        else:
            consensus = ConsensusLevel.LOW

        criterion_aggregates.append(AggregatedCriterionScore(
            criterion_id=criterion.id,
            criterion_name=criterion.name,
            average_score=round(avg, 2) if avg else None,
            min_score=min_s,
            max_score=max_s,
            std_dev=round(std, 2) if std else None,
            consensus=consensus,
            model_scores=model_score_map,
            pass_count=pass_count if criterion.type == CriterionType.TABLE_STAKES else None,
            fail_count=fail_count if criterion.type == CriterionType.TABLE_STAKES else None
        ))

    # Calculate total weighted score
    total_score = calculate_total_weighted_score(criterion_aggregates, criteria)

    return AggregatedOptionScore(
        option_name=option_name,
        criterion_scores=criterion_aggregates,
        total_weighted_score=total_score,
        rank=0  # Set later
    )


def calculate_total_weighted_score(
    criterion_scores: List[AggregatedCriterionScore],
    criteria: EvaluationCriteria
) -> float:
    """Calculate weighted average across all criteria."""
    criterion_map = {c.id: c for c in criteria.criteria}

    total_weight = 0.0
    weighted_sum = 0.0

    for agg_score in criterion_scores:
        criterion = criterion_map.get(agg_score.criterion_id)
        if not criterion or agg_score.average_score is None:
            continue

        # Skip table stakes in weighted calculation
        if criterion.type == CriterionType.TABLE_STAKES:
            continue

        weight = criterion.numeric_weight or 1.0
        total_weight += weight
        weighted_sum += agg_score.average_score * weight

    return round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0


def separate_by_qualification(
    options: List[AggregatedOptionScore],
    criteria: EvaluationCriteria
) -> tuple:
    """
    Separate options into qualified and disqualified.
    """
    qualified = []
    disqualified = []

    table_stakes = [c for c in criteria.criteria if c.type == CriterionType.TABLE_STAKES]

    for option in options:
        failures = []

        for ts in table_stakes:
            for cs in option.criterion_scores:
                if cs.criterion_id == ts.id:
                    if cs.fail_count and cs.fail_count > 0:
                        failures.append(ts.name)
                    elif cs.average_score is not None and cs.average_score < 5:
                        failures.append(f"{ts.name} (score: {cs.average_score})")
                    break

        if failures:
            option.disqualified = True
            option.disqualification_reason = f"Failed: {', '.join(failures)}"
            disqualified.append(option)
        else:
            qualified.append(option)

    return qualified, disqualified
```

---

## Acceptance Criteria

- [ ] Aggregates scores from all models for each option
- [ ] Calculates mean, min, max, std dev per criterion
- [ ] Determines consensus level (HIGH/MEDIUM/LOW)
- [ ] Separates qualified from disqualified options
- [ ] Ranks qualified options by weighted score
- [ ] Generates recommendation text
- [ ] Warns when all options disqualified

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_aggregation.py

def test_aggregate_two_models():
    """Should average scores from two models"""
    stage1_results = [
        {"model": "gpt-4", "response": "..scores\nOption: A\n---\nQuality: 8\n```"},
        {"model": "claude", "response": "..scores\nOption: A\n---\nQuality: 6\n```"}
    ]
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Quality")
    ])

    matrix = aggregate_model_scores(stage1_results, criteria)

    assert len(matrix.options) == 1
    assert matrix.options[0].criterion_scores[0].average_score == 7.0


def test_consensus_calculation():
    """Should correctly classify consensus levels"""
    # Low std dev = high consensus
    scores = [8, 8, 8, 7]
    std = stdev(scores)
    assert std < 1.0  # HIGH consensus

    # High std dev = low consensus
    scores = [2, 5, 9]
    std = stdev(scores)
    assert std > 2.0  # LOW consensus


def test_ranking_by_weighted_score():
    """Options should be ranked by total weighted score"""
    # ... test with multiple options ...


def test_disqualified_ranked_last():
    """Disqualified options should rank below qualified"""
    # ... test with mix of qualified/disqualified ...
```

### Manual Verification

1. Test with real model responses
2. Verify matrix displays correctly with various criteria counts
3. Check recommendation text is sensible
4. Verify ranking order matches expectations

---

## Implementation Notes

- Consider caching aggregated results for large councils
- Matrix should be serializable for API response
- Keep model attribution for drill-down UI

