# Task: F1-BE-05 - Implement Score Extraction Parser

**Version**: 1.0.0
**Created**: 2026-01-02 11:15:00
**Last Updated**: 2026-01-02 11:15:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/backlog/F1-BE-04-stage1-criteria-integration.md`
**Agent**: product-manager

---

## Task Summary

Create robust parser to extract structured scores from model responses, handling various output formats with fallback strategies.

## Complexity: L (8 hours)

## Dependencies
- F1-BE-04 (Stage 1 Criteria Integration)

## Blocked By
- F1-BE-04

## Blocks
- F1-BE-06, F1-BE-07

---

## Technical Specification

### File Location
`/backend/parsing.py` (new file)

### Functions to Implement

```python
import re
from typing import List, Dict, Optional, Tuple
from .models import (
    EvaluationCriteria, Criterion, CriterionType,
    CriterionScore, OptionScores
)

def extract_scores_from_response(
    response_text: str,
    criteria: EvaluationCriteria
) -> List[OptionScores]:
    """
    Extract structured scores from a model's response.

    Tries multiple extraction strategies in order:
    1. Structured score blocks (```scores ... ```)
    2. Markdown table format
    3. Inline score patterns
    4. Heuristic fallback

    Args:
        response_text: Full model response
        criteria: Expected criteria to extract

    Returns:
        List of OptionScores, one per option found
    """
    results = []

    # Strategy 1: Try structured score blocks
    results = _extract_from_score_blocks(response_text, criteria)
    if results:
        return results

    # Strategy 2: Try markdown tables
    results = _extract_from_tables(response_text, criteria)
    if results:
        return results

    # Strategy 3: Try inline patterns
    results = _extract_from_inline(response_text, criteria)
    if results:
        return results

    # Strategy 4: Heuristic fallback
    return _extract_heuristic(response_text, criteria)


def _extract_from_score_blocks(
    text: str,
    criteria: EvaluationCriteria
) -> List[OptionScores]:
    """
    Extract from ```scores blocks.

    Expected format:
    ```scores
    Option: Option Name
    ---
    Criterion Name: 8 | Justification
    ```
    """
    results = []

    # Find all score blocks
    block_pattern = r'```scores\s*(.*?)```'
    blocks = re.findall(block_pattern, text, re.DOTALL | re.IGNORECASE)

    for block in blocks:
        option_name = None
        scores = []

        lines = block.strip().split('\n')
        for line in lines:
            line = line.strip()

            # Extract option name
            if line.lower().startswith('option:'):
                option_name = line.split(':', 1)[1].strip()
                continue

            if line == '---' or not line:
                continue

            # Extract criterion score
            score_match = re.match(
                r'^(.+?):\s*(\d+|PASS|FAIL|N/A)\s*\|?\s*(.*)$',
                line,
                re.IGNORECASE
            )

            if score_match:
                criterion_name = score_match.group(1).strip()
                score_value = score_match.group(2).strip().upper()
                evidence = score_match.group(3).strip() if score_match.group(3) else None

                # Find matching criterion
                criterion = _find_criterion(criterion_name, criteria)
                if criterion:
                    score = CriterionScore(
                        criterion_id=criterion.id,
                        score=float(score_value) if score_value.isdigit() else None,
                        passed=score_value == "PASS" if score_value in ["PASS", "FAIL"] else None,
                        evidence=evidence
                    )
                    scores.append(score)

        if option_name and scores:
            results.append(OptionScores(
                option_name=option_name,
                scores=scores
            ))

    return results


def _extract_from_tables(
    text: str,
    criteria: EvaluationCriteria
) -> List[OptionScores]:
    """
    Extract from markdown tables.

    Expected format:
    | Option | Criterion A | Criterion B |
    |--------|-------------|-------------|
    | Opt 1  | 8           | PASS        |
    """
    results = []

    # Find markdown tables
    table_pattern = r'\|(.+\|)+\n\|[-:\s|]+\|\n((?:\|.+\|(?:\n|$))+)'
    tables = re.findall(table_pattern, text)

    for header_row, body in tables:
        # Parse header to find criterion columns
        headers = [h.strip() for h in header_row.split('|') if h.strip()]

        if not headers or headers[0].lower() != 'option':
            continue

        criterion_indices = {}
        for i, header in enumerate(headers[1:], start=1):
            criterion = _find_criterion(header, criteria)
            if criterion:
                criterion_indices[i] = criterion

        if not criterion_indices:
            continue

        # Parse body rows
        rows = body.strip().split('\n')
        for row in rows:
            cells = [c.strip() for c in row.split('|') if c.strip()]
            if len(cells) < 2:
                continue

            option_name = cells[0]
            scores = []

            for idx, criterion in criterion_indices.items():
                if idx < len(cells):
                    value = cells[idx].upper()
                    score = CriterionScore(
                        criterion_id=criterion.id,
                        score=float(value) if value.replace('.', '').isdigit() else None,
                        passed=value == "PASS" if value in ["PASS", "FAIL"] else None
                    )
                    scores.append(score)

            if scores:
                results.append(OptionScores(option_name=option_name, scores=scores))

    return results


def _extract_from_inline(
    text: str,
    criteria: EvaluationCriteria
) -> List[OptionScores]:
    """
    Extract from inline patterns like "Accuracy: 8/10" or "GDPR: PASS".
    """
    results = []
    options = criteria.options or []

    # If no explicit options, try to find option headers
    if not options:
        option_pattern = r'(?:^|\n)##?\s*(?:Option\s*)?(\d+|[A-Z])[:\s]*([^\n]+)'
        matches = re.findall(option_pattern, text)
        options = [m[1].strip() for m in matches if m[1].strip()]

    for option in options:
        # Find section for this option
        option_pattern = rf'(?:^|\n)##?\s*(?:Option\s*)?.*?{re.escape(option)}.*?(?=(?:\n##|\Z))'
        section_match = re.search(option_pattern, text, re.DOTALL | re.IGNORECASE)

        if not section_match:
            continue

        section = section_match.group(0)
        scores = []

        for criterion in criteria.criteria:
            # Look for patterns like "Criterion: 8" or "Criterion: PASS"
            patterns = [
                rf'{re.escape(criterion.name)}[:\s]+(\d+(?:\.\d+)?)\s*(?:/\s*10)?',
                rf'{re.escape(criterion.name)}[:\s]+(PASS|FAIL)',
                rf'{re.escape(criterion.name)}.*?(?:score|rating)[:\s]+(\d+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    value = match.group(1).upper()
                    score = CriterionScore(
                        criterion_id=criterion.id,
                        score=float(value) if value.replace('.', '').isdigit() else None,
                        passed=value == "PASS" if value in ["PASS", "FAIL"] else None
                    )
                    scores.append(score)
                    break

        if scores:
            results.append(OptionScores(option_name=option, scores=scores))

    return results


def _extract_heuristic(
    text: str,
    criteria: EvaluationCriteria
) -> List[OptionScores]:
    """
    Fallback heuristic extraction when structured formats fail.
    Uses NLP-like patterns to infer scores from prose.
    """
    # Simplified heuristic: look for sentiment around criterion mentions
    results = []

    sentiment_positive = ['excellent', 'great', 'strong', 'best', 'superior', 'outstanding']
    sentiment_negative = ['poor', 'weak', 'lacking', 'fails', 'inadequate', 'worst']
    sentiment_neutral = ['adequate', 'acceptable', 'average', 'moderate', 'sufficient']

    options = criteria.options or ["Option"]

    for option in options:
        scores = []

        for criterion in criteria.criteria:
            # Find sentences mentioning this criterion
            sentences = re.findall(
                rf'[^.]*{re.escape(criterion.name)}[^.]*\.',
                text,
                re.IGNORECASE
            )

            if sentences:
                sentence = sentences[0].lower()

                if any(word in sentence for word in sentiment_positive):
                    inferred_score = 8.0
                elif any(word in sentence for word in sentiment_negative):
                    inferred_score = 3.0
                elif any(word in sentence for word in sentiment_neutral):
                    inferred_score = 5.5
                else:
                    inferred_score = None

                if inferred_score is not None:
                    scores.append(CriterionScore(
                        criterion_id=criterion.id,
                        score=inferred_score,
                        evidence=f"Inferred from: '{sentences[0][:100]}...'"
                    ))

        if scores:
            results.append(OptionScores(option_name=option, scores=scores))

    return results


def _find_criterion(
    name: str,
    criteria: EvaluationCriteria
) -> Optional[Criterion]:
    """Find criterion by name (case-insensitive, fuzzy)."""
    name_lower = name.lower().strip()

    # Exact match
    for c in criteria.criteria:
        if c.name.lower() == name_lower:
            return c

    # Partial match
    for c in criteria.criteria:
        if name_lower in c.name.lower() or c.name.lower() in name_lower:
            return c

    return None


def calculate_weighted_scores(
    option_scores: OptionScores,
    criteria: EvaluationCriteria
) -> float:
    """
    Calculate total weighted score for an option.

    Returns:
        Weighted average score (0-10 scale)
    """
    total_weight = 0.0
    weighted_sum = 0.0

    criterion_map = {c.id: c for c in criteria.criteria}

    for score in option_scores.scores:
        criterion = criterion_map.get(score.criterion_id)
        if not criterion or score.score is None:
            continue

        weight = criterion.numeric_weight or 1.0
        total_weight += weight
        weighted_sum += score.score * weight

    return round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0
```

---

## Acceptance Criteria

- [ ] Extracts scores from structured ```scores blocks
- [ ] Extracts scores from markdown tables
- [ ] Extracts inline scores (Criterion: 8/10 format)
- [ ] Heuristic fallback provides reasonable estimates
- [ ] Handles mixed formats in single response
- [ ] Calculates weighted scores correctly
- [ ] Performance: <500ms for typical response parsing

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_parsing.py

def test_extract_from_score_block():
    """Should parse structured score block"""
    text = """
Some analysis text...

```scores
Option: AWS Transcribe
---
Accuracy: 8 | Good WER scores
Cost: 6 | Mid-range pricing
GDPR: PASS | EU available
```
"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Accuracy"),
        Criterion(id="c2", name="Cost"),
        Criterion(id="c3", name="GDPR", type=CriterionType.TABLE_STAKES)
    ])

    results = extract_scores_from_response(text, criteria)
    assert len(results) == 1
    assert results[0].option_name == "AWS Transcribe"
    assert len(results[0].scores) == 3


def test_extract_from_markdown_table():
    """Should parse markdown table"""
    text = """
| Option | Accuracy | Cost |
|--------|----------|------|
| Opt A  | 8        | 6    |
| Opt B  | 7        | 9    |
"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Accuracy"),
        Criterion(id="c2", name="Cost")
    ])

    results = extract_scores_from_response(text, criteria)
    assert len(results) == 2


def test_extract_inline_patterns():
    """Should parse inline score patterns"""
    text = """
## Option A
Accuracy: 8/10 - Very good
Cost score: 6

## Option B
The Accuracy is rated 7 out of 10.
"""
    criteria = EvaluationCriteria(
        criteria=[Criterion(id="c1", name="Accuracy")],
        options=["Option A", "Option B"]
    )

    results = extract_scores_from_response(text, criteria)
    assert len(results) >= 1


def test_heuristic_fallback():
    """Should infer scores from sentiment"""
    text = "The accuracy is excellent and best-in-class."
    criteria = EvaluationCriteria(
        criteria=[Criterion(id="c1", name="Accuracy")],
        options=["Test"]
    )

    results = extract_scores_from_response(text, criteria)
    assert len(results) == 1
    assert results[0].scores[0].score >= 7  # Positive sentiment


def test_weighted_score_calculation():
    """Should calculate weighted average correctly"""
    scores = OptionScores(
        option_name="Test",
        scores=[
            CriterionScore(criterion_id="c1", score=10),  # P0 weight 3
            CriterionScore(criterion_id="c2", score=5),   # P1 weight 2
        ]
    )
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="A", weight=WeightLevel.P0),  # 3.0
        Criterion(id="c2", name="B", weight=WeightLevel.P1),  # 2.0
    ])

    # Expected: (10*3 + 5*2) / (3+2) = 40/5 = 8.0
    result = calculate_weighted_scores(scores, criteria)
    assert result == 8.0
```

### Manual Verification

1. Test parser with real model responses (GPT-4, Claude, Gemini)
2. Verify extraction accuracy across different output styles
3. Test edge cases: missing scores, malformed tables, unusual formatting
4. Benchmark parsing time with large responses

---

## Implementation Notes

- Parser should be defensive - never crash on unexpected input
- Log parsing failures for debugging and prompt improvement
- Consider adding confidence scores to extracted values
- May need model-specific parsing adjustments in future

