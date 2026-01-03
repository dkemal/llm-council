# Task: F1-BE-01 - Define Criteria Data Schema

**Version**: 1.0.0
**Created**: 2026-01-02 11:15:00
**Last Updated**: 2026-01-02 11:15:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F1-structured-criteria.md`
**Agent**: product-manager

---

## Task Summary

Define the Pydantic data models for evaluation criteria, including weights, types (scored vs. table stakes), and validation rules.

## Complexity: S (2 hours)

## Dependencies
- None (foundational task)

## Blocked By
- None

## Blocks
- F1-BE-02, F1-BE-03, F1-FE-01

---

## Technical Specification

### File Location
`/backend/models.py` (new file)

### Data Models

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from enum import Enum

class CriterionType(str, Enum):
    SCORED = "scored"           # 1-10 rating
    TABLE_STAKES = "table_stakes"  # Pass/Fail

class WeightLevel(str, Enum):
    P0 = "P0"  # Critical (weight: 3.0)
    P1 = "P1"  # Important (weight: 2.0)
    P2 = "P2"  # Nice-to-have (weight: 1.0)

class Criterion(BaseModel):
    """Single evaluation criterion."""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: CriterionType = Field(default=CriterionType.SCORED)
    weight: WeightLevel = Field(default=WeightLevel.P1)
    numeric_weight: Optional[float] = Field(None, ge=1, le=10)

    @validator('numeric_weight', always=True)
    def set_numeric_weight(cls, v, values):
        if v is not None:
            return v
        weight_map = {"P0": 3.0, "P1": 2.0, "P2": 1.0}
        return weight_map.get(values.get('weight', 'P1'), 2.0)

class EvaluationCriteria(BaseModel):
    """Complete criteria set for a deliberation."""
    criteria: List[Criterion] = Field(..., min_items=1, max_items=20)
    options: Optional[List[str]] = Field(None, description="Options to evaluate")

    @validator('criteria')
    def validate_unique_names(cls, v):
        names = [c.name.lower() for c in v]
        if len(names) != len(set(names)):
            raise ValueError("Criterion names must be unique")
        return v

class CriterionScore(BaseModel):
    """Score for a single criterion from a model."""
    criterion_id: str
    score: Optional[float] = Field(None, ge=0, le=10)
    passed: Optional[bool] = Field(None)  # For table stakes
    evidence: Optional[str] = Field(None, max_length=1000)

class OptionScores(BaseModel):
    """All criterion scores for a single option."""
    option_name: str
    scores: List[CriterionScore]
    total_weighted_score: Optional[float] = None
    disqualified: bool = False
    disqualification_reason: Optional[str] = None
```

---

## Acceptance Criteria

- [ ] Pydantic models defined in `/backend/models.py`
- [ ] Criterion supports both P0/P1/P2 and 1-10 numeric weights
- [ ] CriterionType enum distinguishes scored vs. table_stakes
- [ ] Validation prevents duplicate criterion names
- [ ] Validation limits to 1-20 criteria per deliberation
- [ ] All models have proper Field descriptions for API docs

---

## Validation Steps

### Unit Tests to Create

```python
# /backend/tests/test_models.py

def test_criterion_default_weight():
    """P1 criterion should have numeric_weight 2.0"""
    c = Criterion(id="c1", name="Test")
    assert c.numeric_weight == 2.0

def test_criterion_p0_weight():
    """P0 criterion should have numeric_weight 3.0"""
    c = Criterion(id="c1", name="Test", weight=WeightLevel.P0)
    assert c.numeric_weight == 3.0

def test_criteria_unique_names():
    """Should reject duplicate criterion names"""
    with pytest.raises(ValueError):
        EvaluationCriteria(criteria=[
            Criterion(id="c1", name="Quality"),
            Criterion(id="c2", name="quality")  # Duplicate (case-insensitive)
        ])

def test_criteria_max_limit():
    """Should reject >20 criteria"""
    criteria = [Criterion(id=f"c{i}", name=f"Criterion {i}") for i in range(21)]
    with pytest.raises(ValueError):
        EvaluationCriteria(criteria=criteria)

def test_table_stakes_criterion():
    """Table stakes should use passed/failed, not score"""
    c = Criterion(id="c1", name="GDPR Compliance", type=CriterionType.TABLE_STAKES)
    assert c.type == CriterionType.TABLE_STAKES
```

### Manual Verification

1. Create model instance in Python REPL
2. Test JSON serialization/deserialization
3. Verify FastAPI auto-generates correct OpenAPI schema

---

## Implementation Notes

- Use `pydantic>=2.0` syntax if project uses v2
- Consider adding `model_config` for JSON schema customization
- Keep models in separate file to avoid circular imports

