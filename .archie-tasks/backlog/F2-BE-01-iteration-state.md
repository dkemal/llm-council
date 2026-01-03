# Task: F2-BE-01 - Design Iteration State Management

**Version**: 1.0.0
**Created**: 2026-01-02 12:00:00
**Last Updated**: 2026-01-02 12:00:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F2-iterative-refinement.md`
**Agent**: product-manager

---

## Task Summary

Design the data structures and state management for tracking iteration rounds, preserving history, and managing termination conditions.

## Complexity: M (4 hours)

## Dependencies
- None (foundational task)

## Blocked By
- None

## Blocks
- F2-BE-04, F2-BE-06

---

## Technical Specification

### File Location
`/backend/iteration.py` (new file)

### Data Models

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class TerminationReason(str, Enum):
    MAX_ROUNDS = "max_rounds_reached"
    CONVERGENCE = "models_converged"
    USER_STOP = "user_stopped"
    NO_CHANGES = "no_significant_changes"
    ERROR = "error_occurred"
    CONTEXT_LIMIT = "context_limit_reached"

class CritiqueItem(BaseModel):
    """Single critique point extracted from a ranking."""
    source_model: str
    target_response: str  # "Response A", "Response B", etc.
    critique_text: str
    severity: str = "medium"  # high, medium, low

class RefinementResult(BaseModel):
    """Result of a model refining its response."""
    model: str
    original_response: str
    refined_response: str
    critiques_addressed: List[str]
    changes_made: bool
    change_summary: Optional[str] = None

class IterationRound(BaseModel):
    """Complete data for one iteration round."""
    round_number: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    critiques: Dict[str, List[CritiqueItem]]  # response_label -> critiques
    refinements: List[RefinementResult]
    models_that_changed: List[str]
    models_unchanged: List[str]

class IterationState(BaseModel):
    """Complete iteration state for a deliberation."""
    enabled: bool = False
    max_rounds: int = Field(default=2, ge=1, le=5)
    current_round: int = 0
    rounds: List[IterationRound] = []
    terminated: bool = False
    termination_reason: Optional[TerminationReason] = None
    total_tokens_used: int = 0
    context_budget: int = 50000  # Max tokens to use

class IterationConfig(BaseModel):
    """User configuration for iteration behavior."""
    enabled: bool = True
    max_rounds: int = 2
    auto_stop_on_convergence: bool = True
    min_change_threshold: float = 0.1  # Minimum change ratio to continue
```

### State Management Functions

```python
from typing import Tuple

def initialize_iteration_state(config: IterationConfig) -> IterationState:
    """
    Initialize iteration state from user config.
    """
    return IterationState(
        enabled=config.enabled,
        max_rounds=config.max_rounds,
        current_round=0,
        rounds=[],
        terminated=False,
        termination_reason=None
    )


def should_continue_iteration(state: IterationState) -> Tuple[bool, Optional[TerminationReason]]:
    """
    Determine if another iteration round should occur.

    Returns:
        Tuple of (should_continue, reason_if_not)
    """
    if not state.enabled:
        return False, None

    if state.terminated:
        return False, state.termination_reason

    # Check max rounds
    if state.current_round >= state.max_rounds:
        return False, TerminationReason.MAX_ROUNDS

    # Check context budget
    if state.total_tokens_used > state.context_budget * 0.9:
        return False, TerminationReason.CONTEXT_LIMIT

    # Check for convergence (no changes in last round)
    if state.rounds:
        last_round = state.rounds[-1]
        if len(last_round.models_that_changed) == 0:
            return False, TerminationReason.CONVERGENCE

    return True, None


def start_new_round(state: IterationState) -> IterationRound:
    """
    Initialize a new iteration round.
    """
    state.current_round += 1

    new_round = IterationRound(
        round_number=state.current_round,
        started_at=datetime.utcnow(),
        critiques={},
        refinements=[],
        models_that_changed=[],
        models_unchanged=[]
    )

    state.rounds.append(new_round)
    return new_round


def complete_round(
    state: IterationState,
    round_data: IterationRound,
    tokens_used: int
) -> None:
    """
    Finalize a completed iteration round.
    """
    round_data.completed_at = datetime.utcnow()
    state.total_tokens_used += tokens_used

    # Update the round in state
    state.rounds[-1] = round_data


def terminate_iteration(
    state: IterationState,
    reason: TerminationReason
) -> None:
    """
    Mark iteration as terminated.
    """
    state.terminated = True
    state.termination_reason = reason


def get_iteration_summary(state: IterationState) -> Dict[str, Any]:
    """
    Generate summary of iteration process for display.
    """
    if not state.rounds:
        return {"message": "No iterations performed"}

    total_changes = sum(len(r.models_that_changed) for r in state.rounds)
    total_unchanged = sum(len(r.models_unchanged) for r in state.rounds)

    return {
        "rounds_completed": len(state.rounds),
        "max_rounds": state.max_rounds,
        "total_refinements": total_changes,
        "total_unchanged": total_unchanged,
        "terminated_reason": state.termination_reason.value if state.termination_reason else None,
        "tokens_used": state.total_tokens_used,
        "round_summaries": [
            {
                "round": r.round_number,
                "models_changed": len(r.models_that_changed),
                "models_unchanged": len(r.models_unchanged),
                "duration_seconds": (r.completed_at - r.started_at).total_seconds() if r.completed_at else None
            }
            for r in state.rounds
        ]
    }
```

---

## Acceptance Criteria

- [ ] IterationState model captures all round data
- [ ] IterationConfig allows user customization
- [ ] `should_continue_iteration()` correctly evaluates termination conditions
- [ ] State tracks token usage for context management
- [ ] Round start/complete functions maintain state consistency
- [ ] Summary function provides useful display data

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_iteration_state.py

def test_initialize_state():
    """Should create state from config"""
    config = IterationConfig(enabled=True, max_rounds=3)
    state = initialize_iteration_state(config)

    assert state.enabled == True
    assert state.max_rounds == 3
    assert state.current_round == 0
    assert len(state.rounds) == 0


def test_should_continue_first_round():
    """Should continue on first round"""
    state = IterationState(enabled=True, max_rounds=2, current_round=0)
    should_continue, reason = should_continue_iteration(state)

    assert should_continue == True
    assert reason is None


def test_should_stop_at_max_rounds():
    """Should stop when max rounds reached"""
    state = IterationState(enabled=True, max_rounds=2, current_round=2)
    should_continue, reason = should_continue_iteration(state)

    assert should_continue == False
    assert reason == TerminationReason.MAX_ROUNDS


def test_should_stop_on_convergence():
    """Should stop when no models changed"""
    state = IterationState(
        enabled=True,
        max_rounds=3,
        current_round=1,
        rounds=[
            IterationRound(
                round_number=1,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                critiques={},
                refinements=[],
                models_that_changed=[],  # No changes
                models_unchanged=["gpt-4", "claude"]
            )
        ]
    )
    should_continue, reason = should_continue_iteration(state)

    assert should_continue == False
    assert reason == TerminationReason.CONVERGENCE


def test_context_budget_limit():
    """Should stop when approaching context limit"""
    state = IterationState(
        enabled=True,
        max_rounds=5,
        current_round=1,
        total_tokens_used=46000,
        context_budget=50000
    )
    should_continue, reason = should_continue_iteration(state)

    assert should_continue == False
    assert reason == TerminationReason.CONTEXT_LIMIT


def test_start_new_round():
    """Should increment round and create new entry"""
    state = IterationState(enabled=True, max_rounds=3, current_round=0)
    new_round = start_new_round(state)

    assert state.current_round == 1
    assert len(state.rounds) == 1
    assert new_round.round_number == 1


def test_iteration_summary():
    """Should generate correct summary"""
    state = IterationState(
        enabled=True,
        max_rounds=2,
        current_round=2,
        terminated=True,
        termination_reason=TerminationReason.MAX_ROUNDS,
        total_tokens_used=25000,
        rounds=[
            IterationRound(
                round_number=1,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                critiques={},
                refinements=[],
                models_that_changed=["gpt-4"],
                models_unchanged=["claude"]
            )
        ]
    )

    summary = get_iteration_summary(state)

    assert summary["rounds_completed"] == 1
    assert summary["total_refinements"] == 1
    assert summary["terminated_reason"] == "max_rounds_reached"
```

---

## Implementation Notes

- Consider using dataclasses if Pydantic overhead is concern
- Token tracking is estimate - refine with actual tokenizer later
- State should be serializable for persistence if needed
- Keep round data lean - don't duplicate full responses

