# Task: F1-BE-04 - Modify Stage 1 to Accept Criteria

**Version**: 1.0.0
**Created**: 2026-01-02 11:15:00
**Last Updated**: 2026-01-02 11:15:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/backlog/F1-BE-03-criterion-aware-prompts.md`
**Agent**: product-manager

---

## Task Summary

Modify `stage1_collect_responses()` in `council.py` to accept optional criteria parameter and use criterion-aware prompts when provided.

## Complexity: M (4 hours)

## Dependencies
- F1-BE-03 (Criterion-Aware Prompt Builder)

## Blocked By
- F1-BE-03

## Blocks
- F1-BE-05, F1-BE-07, F1-BE-08

---

## Technical Specification

### File to Modify
`/backend/council.py`

### Changes Required

#### 1. Update Function Signature

```python
from typing import List, Dict, Any, Optional
from .models import EvaluationCriteria
from .prompts import build_stage1_prompt_with_criteria

async def stage1_collect_responses(
    user_query: str,
    criteria: Optional[EvaluationCriteria] = None
) -> List[Dict[str, Any]]:
    """
    Stage 1: Collect individual responses from all council models.

    Args:
        user_query: The user's question
        criteria: Optional evaluation criteria for structured analysis

    Returns:
        List of dicts with 'model' and 'response' keys
    """
```

#### 2. Update Message Construction

```python
async def stage1_collect_responses(
    user_query: str,
    criteria: Optional[EvaluationCriteria] = None
) -> List[Dict[str, Any]]:
    """Stage 1: Collect individual responses from all council models."""

    # Build appropriate prompt based on whether criteria provided
    if criteria:
        prompt_content = build_stage1_prompt_with_criteria(user_query, criteria)
    else:
        prompt_content = user_query

    messages = [{"role": "user", "content": prompt_content}]

    # Query all models in parallel
    responses = await query_models_parallel(COUNCIL_MODELS, messages)

    # Format results
    stage1_results = []
    for model, response in responses.items():
        if response is not None:
            stage1_results.append({
                "model": model,
                "response": response.get('content', ''),
                "has_criteria": criteria is not None  # Track if criteria-aware
            })

    return stage1_results
```

#### 3. Update run_full_council()

```python
async def run_full_council(
    user_query: str,
    criteria: Optional[EvaluationCriteria] = None
) -> Tuple[List, List, Dict, Dict]:
    """
    Run the complete 3-stage council process.

    Args:
        user_query: The user's question
        criteria: Optional evaluation criteria

    Returns:
        Tuple of (stage1_results, stage2_results, stage3_result, metadata)
    """
    # Stage 1: Collect individual responses with criteria
    stage1_results = await stage1_collect_responses(user_query, criteria)

    # If no models responded successfully, return error
    if not stage1_results:
        return [], [], {
            "model": "error",
            "response": "All models failed to respond. Please try again."
        }, {}

    # Stage 2: Collect rankings (criteria passed for context)
    stage2_results, label_to_model = await stage2_collect_rankings(
        user_query, stage1_results, criteria
    )

    # Calculate aggregate rankings
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)

    # Stage 3: Synthesize final answer (criteria for context)
    stage3_result = await stage3_synthesize_final(
        user_query,
        stage1_results,
        stage2_results,
        criteria
    )

    # Prepare metadata
    metadata = {
        "label_to_model": label_to_model,
        "aggregate_rankings": aggregate_rankings,
        "criteria_used": criteria.model_dump() if criteria else None
    }

    return stage1_results, stage2_results, stage3_result, metadata
```

#### 4. Update stage2_collect_rankings() Signature

```python
async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    criteria: Optional[EvaluationCriteria] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Stage 2: Each model ranks the anonymized responses.
    """
    # ... existing label creation logic ...

    # Use criteria-aware Stage 2 prompt if criteria provided
    if criteria:
        ranking_prompt = build_stage2_prompt_with_criteria(
            user_query, responses_text, criteria
        )
    else:
        ranking_prompt = f"""..."""  # existing prompt

    # ... rest of function ...
```

#### 5. Update stage3_synthesize_final() Signature

```python
async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]],
    criteria: Optional[EvaluationCriteria] = None
) -> Dict[str, Any]:
    """
    Stage 3: Chairman synthesizes final response.
    """
    # Add criteria context to chairman prompt
    criteria_context = ""
    if criteria:
        criteria_names = ", ".join(c.name for c in criteria.criteria)
        criteria_context = f"\nThe evaluation was conducted against these criteria: {criteria_names}\n"

    chairman_prompt = f"""...{criteria_context}..."""
    # ... rest of function ...
```

---

## Acceptance Criteria

- [ ] `stage1_collect_responses()` accepts optional `criteria` parameter
- [ ] Criteria-aware prompt used when criteria provided
- [ ] Original behavior preserved when no criteria (backward compatible)
- [ ] All downstream functions receive criteria parameter
- [ ] Metadata includes criteria used for reference
- [ ] No breaking changes to existing API

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_council.py

@pytest.mark.asyncio
async def test_stage1_without_criteria():
    """Should work without criteria (backward compatible)"""
    results = await stage1_collect_responses("What is Python?")
    assert len(results) > 0
    assert results[0]["has_criteria"] == False

@pytest.mark.asyncio
async def test_stage1_with_criteria():
    """Should use criteria-aware prompt"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Accuracy")
    ])
    results = await stage1_collect_responses("Which API?", criteria)
    assert len(results) > 0
    assert results[0]["has_criteria"] == True

@pytest.mark.asyncio
async def test_run_full_council_with_criteria():
    """Full council should accept and pass criteria"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Quality")
    ])
    s1, s2, s3, metadata = await run_full_council("Test?", criteria)
    assert metadata.get("criteria_used") is not None
    assert metadata["criteria_used"]["criteria"][0]["name"] == "Quality"
```

### Integration Test

```python
@pytest.mark.asyncio
async def test_criteria_flow_end_to_end():
    """Full flow with criteria produces structured responses"""
    criteria = EvaluationCriteria(
        criteria=[
            Criterion(id="c1", name="Accuracy", type=CriterionType.SCORED),
            Criterion(id="c2", name="GDPR", type=CriterionType.TABLE_STAKES)
        ],
        options=["Option A", "Option B"]
    )

    s1, s2, s3, metadata = await run_full_council(
        "Which transcription API should I use?",
        criteria
    )

    # Verify responses mention criteria
    for result in s1:
        assert "Accuracy" in result["response"] or "accuracy" in result["response"].lower()
        assert "GDPR" in result["response"] or "gdpr" in result["response"].lower()
```

### Manual Verification

1. Run backend with test criteria via REPL
2. Verify model responses address each criterion
3. Check that responses include score blocks
4. Verify chairman summary references criteria

---

## Implementation Notes

- Maintain backward compatibility - no criteria = current behavior
- Consider logging criteria usage for analytics
- Monitor prompt token usage with criteria

