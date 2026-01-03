# Task: F1-BE-08 - Update API Endpoints for Criteria

**Version**: 1.0.0
**Created**: 2026-01-02 11:30:00
**Last Updated**: 2026-01-02 11:30:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
  - `/.archie-tasks/backlog/F1-BE-07-scoring-matrix.md`
**Agent**: product-manager

---

## Task Summary

Update FastAPI endpoints to accept criteria in message requests and return scoring matrix in responses.

## Complexity: M (4 hours)

## Dependencies
- F1-BE-07 (Scoring Matrix Aggregator)

## Blocked By
- F1-BE-07

## Blocks
- F1-INT-01

---

## Technical Specification

### File to Modify
`/backend/main.py`

### Changes Required

#### 1. Update Request Model

```python
from typing import Optional, List
from .models import EvaluationCriteria, Criterion
from .validation import validate_criteria

class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    content: str
    criteria: Optional[EvaluationCriteria] = None
    options: Optional[List[str]] = None  # Convenience field

    @validator('criteria')
    def validate_criteria_if_provided(cls, v):
        if v is not None:
            is_valid, messages = validate_criteria(v)
            if not is_valid:
                raise ValueError(f"Invalid criteria: {'; '.join(messages)}")
        return v
```

#### 2. Update Response Models

```python
from .aggregation import ScoringMatrix

class DeliberationResponse(BaseModel):
    """Complete response from deliberation."""
    stage1: List[Dict[str, Any]]
    stage2: List[Dict[str, Any]]
    stage3: Dict[str, Any]
    metadata: Dict[str, Any]
    scoring_matrix: Optional[ScoringMatrix] = None
```

#### 3. Update send_message Endpoint

```python
@app.post("/api/conversations/{conversation_id}/message")
async def send_message(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and run the 3-stage council process.
    Returns the complete response with all stages.
    """
    # Check if conversation exists
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Merge options into criteria if provided separately
    criteria = request.criteria
    if criteria and request.options:
        criteria.options = request.options
    elif request.options and not criteria:
        # Create minimal criteria for options comparison
        criteria = EvaluationCriteria(
            criteria=[Criterion(id="quality", name="Overall Quality")],
            options=request.options
        )

    # Check if this is the first message
    is_first_message = len(conversation["messages"]) == 0

    # Add user message
    storage.add_user_message(conversation_id, request.content)

    # If this is the first message, generate a title
    if is_first_message:
        title = await generate_conversation_title(request.content)
        storage.update_conversation_title(conversation_id, title)

    # Run the 3-stage council process with criteria
    stage1_results, stage2_results, stage3_result, metadata = await run_full_council(
        request.content,
        criteria
    )

    # Generate scoring matrix if criteria provided
    scoring_matrix = None
    if criteria:
        from .aggregation import aggregate_model_scores
        scoring_matrix = aggregate_model_scores(stage1_results, criteria)

    # Add assistant message with all stages
    storage.add_assistant_message(
        conversation_id,
        stage1_results,
        stage2_results,
        stage3_result
    )

    # Return the complete response with metadata and matrix
    return {
        "stage1": stage1_results,
        "stage2": stage2_results,
        "stage3": stage3_result,
        "metadata": metadata,
        "scoring_matrix": scoring_matrix.model_dump() if scoring_matrix else None
    }
```

#### 4. Update Streaming Endpoint

```python
@app.post("/api/conversations/{conversation_id}/message/stream")
async def send_message_stream(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and stream the 3-stage council process.
    """
    # Validate and prepare criteria (same as above)
    criteria = request.criteria
    if criteria and request.options:
        criteria.options = request.options

    async def event_generator():
        try:
            storage.add_user_message(conversation_id, request.content)

            title_task = None
            if is_first_message:
                title_task = asyncio.create_task(...)

            # Stage 1 with criteria
            yield f"data: {json.dumps({'type': 'stage1_start'})}\n\n"
            stage1_results = await stage1_collect_responses(request.content, criteria)
            yield f"data: {json.dumps({'type': 'stage1_complete', 'data': stage1_results})}\n\n"

            # Stage 2 with criteria context
            yield f"data: {json.dumps({'type': 'stage2_start'})}\n\n"
            stage2_results, label_to_model = await stage2_collect_rankings(
                request.content, stage1_results, criteria
            )
            # ... existing ranking logic ...
            yield f"data: {json.dumps({'type': 'stage2_complete', ...})}\n\n"

            # Stage 3
            yield f"data: {json.dumps({'type': 'stage3_start'})}\n\n"
            stage3_result = await stage3_synthesize_final(
                request.content, stage1_results, stage2_results, criteria
            )
            yield f"data: {json.dumps({'type': 'stage3_complete', 'data': stage3_result})}\n\n"

            # Generate and emit scoring matrix
            if criteria:
                from .aggregation import aggregate_model_scores
                scoring_matrix = aggregate_model_scores(stage1_results, criteria)
                yield f"data: {json.dumps({'type': 'scoring_matrix', 'data': scoring_matrix.model_dump()})}\n\n"

            # ... title and completion events ...

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

#### 5. Add Criteria Validation Endpoint

```python
@app.post("/api/criteria/validate")
async def validate_criteria_endpoint(criteria: EvaluationCriteria):
    """
    Validate criteria before submission.
    Returns validation status and suggestions.
    """
    from .validation import (
        validate_criteria as do_validate,
        detect_criteria_conflicts,
        suggest_missing_criteria
    )

    is_valid, messages = do_validate(criteria)
    conflicts = detect_criteria_conflicts(criteria)
    suggestions = suggest_missing_criteria(criteria)

    return {
        "valid": is_valid,
        "messages": messages,
        "conflicts": conflicts,
        "suggestions": suggestions
    }
```

---

## Acceptance Criteria

- [ ] POST `/api/conversations/{id}/message` accepts optional `criteria` field
- [ ] POST `/api/conversations/{id}/message` accepts optional `options` field
- [ ] Response includes `scoring_matrix` when criteria provided
- [ ] Streaming endpoint emits `scoring_matrix` event
- [ ] POST `/api/criteria/validate` returns validation results
- [ ] Backward compatible - requests without criteria work as before
- [ ] OpenAPI docs updated with new schema

---

## Validation Steps

### API Tests

```python
# /backend/tests/test_api.py

@pytest.mark.asyncio
async def test_message_without_criteria():
    """Should work without criteria (backward compat)"""
    response = client.post(
        "/api/conversations/test/message",
        json={"content": "What is Python?"}
    )
    assert response.status_code == 200
    assert "stage1" in response.json()
    assert response.json().get("scoring_matrix") is None


@pytest.mark.asyncio
async def test_message_with_criteria():
    """Should return scoring matrix with criteria"""
    response = client.post(
        "/api/conversations/test/message",
        json={
            "content": "Which API is best?",
            "criteria": {
                "criteria": [
                    {"id": "c1", "name": "Quality"},
                    {"id": "c2", "name": "Cost"}
                ],
                "options": ["API A", "API B"]
            }
        }
    )
    assert response.status_code == 200
    assert response.json().get("scoring_matrix") is not None


@pytest.mark.asyncio
async def test_criteria_validation_endpoint():
    """Should validate criteria"""
    response = client.post(
        "/api/criteria/validate",
        json={
            "criteria": [
                {"id": "c1", "name": "Quality"}
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["valid"] == True


@pytest.mark.asyncio
async def test_invalid_criteria_rejected():
    """Should reject invalid criteria"""
    response = client.post(
        "/api/conversations/test/message",
        json={
            "content": "Test",
            "criteria": {
                "criteria": []  # Empty - invalid
            }
        }
    )
    assert response.status_code == 422  # Validation error
```

### Manual Verification

1. Test via curl/Postman with various criteria configs
2. Verify OpenAPI docs at /docs show new schema
3. Test streaming endpoint emits scoring_matrix event
4. Verify backward compatibility with existing frontend

---

## Implementation Notes

- Keep response sizes reasonable - don't include full model responses in matrix
- Consider pagination for large scoring matrices
- Rate limit criteria validation endpoint

