# Task: F1-BE-03 - Implement Criterion-Aware Prompt Builder

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

Create prompt builder functions that inject evaluation criteria into Stage 1 prompts, ensuring models address each criterion explicitly and provide structured scores.

## Complexity: M (4 hours)

## Dependencies
- F1-BE-01 (Criteria Data Schema)

## Blocked By
- F1-BE-01

## Blocks
- F1-BE-04, F1-BE-05

---

## Technical Specification

### File Location
`/backend/prompts.py` (new file)

### Functions to Implement

```python
from typing import List, Optional
from .models import EvaluationCriteria, Criterion, CriterionType

def build_stage1_prompt_with_criteria(
    user_query: str,
    criteria: EvaluationCriteria
) -> str:
    """
    Build Stage 1 prompt that instructs model to evaluate against criteria.

    Key requirements:
    - Model must address each criterion explicitly
    - Model must provide scores in parseable format
    - Table Stakes must be clearly pass/fail
    """

    # Build criteria section
    criteria_text = build_criteria_section(criteria)

    # Build options section if provided
    options_text = ""
    if criteria.options:
        options_list = "\n".join(f"- {opt}" for opt in criteria.options)
        options_text = f"\n\nOPTIONS TO EVALUATE:\n{options_list}"

    prompt = f"""You are evaluating options to help answer a user's question. You MUST analyze each option against specific evaluation criteria.

USER QUESTION: {user_query}
{options_text}

{criteria_text}

RESPONSE FORMAT:
For each option, provide your evaluation in the following structure:

## [Option Name]

### Criterion Evaluations
For each criterion below, provide:
1. Your assessment
2. Supporting evidence or reasoning
3. A score (see scoring guide below)

{build_scoring_guide(criteria)}

### Overall Assessment
Summarize the option's strengths and weaknesses.

IMPORTANT:
- You MUST address EVERY criterion listed above
- For Table Stakes criteria, clearly state PASS or FAIL
- For Scored criteria, provide a numerical score 1-10
- Base scores on evidence, not assumptions
- If information is unavailable, state "Unable to assess - [reason]" and score as N/A

Begin your evaluation:"""

    return prompt


def build_criteria_section(criteria: EvaluationCriteria) -> str:
    """Build formatted criteria list for prompt."""

    table_stakes = [c for c in criteria.criteria if c.type == CriterionType.TABLE_STAKES]
    scored = [c for c in criteria.criteria if c.type == CriterionType.SCORED]

    sections = []

    if table_stakes:
        ts_text = "TABLE STAKES (Must Pass - Failure Disqualifies):\n"
        for c in table_stakes:
            desc = f": {c.description}" if c.description else ""
            ts_text += f"- {c.name}{desc}\n"
        sections.append(ts_text)

    if scored:
        scored_text = "SCORED CRITERIA (Rate 1-10):\n"
        for c in scored:
            weight_label = {"P0": "Critical", "P1": "Important", "P2": "Nice-to-have"}
            weight = weight_label.get(c.weight.value, "Important")
            desc = f": {c.description}" if c.description else ""
            scored_text += f"- {c.name} [{weight}]{desc}\n"
        sections.append(scored_text)

    return "\n".join(sections)


def build_scoring_guide(criteria: EvaluationCriteria) -> str:
    """Build scoring guide section."""

    has_table_stakes = any(c.type == CriterionType.TABLE_STAKES for c in criteria.criteria)
    has_scored = any(c.type == CriterionType.SCORED for c in criteria.criteria)

    guide = "SCORING GUIDE:\n"

    if has_table_stakes:
        guide += """
Table Stakes Scoring:
- PASS: Option meets the requirement
- FAIL: Option does not meet the requirement (disqualifies option)
"""

    if has_scored:
        guide += """
Numeric Scoring (1-10):
- 9-10: Exceptional, best-in-class
- 7-8: Strong, above average
- 5-6: Adequate, meets basic needs
- 3-4: Weak, significant gaps
- 1-2: Poor, fails to meet needs
- N/A: Cannot assess due to missing information
"""

    return guide


def build_stage1_score_extraction_format() -> str:
    """
    Build the expected output format for score extraction.
    Used to instruct models on exact format needed.
    """
    return """
REQUIRED OUTPUT FORMAT FOR SCORES:

At the end of EACH option's evaluation, include a score block:

```scores
Option: [Option Name]
---
[Criterion Name]: [SCORE] | [Brief Justification]
[Criterion Name]: [PASS/FAIL] | [Brief Justification]
...
```

Example:
```scores
Option: AWS Transcribe
---
Accuracy: 8 | Strong WER scores in benchmarks
Pricing: 6 | Competitive but not cheapest
GDPR Compliance: PASS | EU data residency available
```
"""


def build_stage2_prompt_with_criteria(
    user_query: str,
    responses_text: str,
    criteria: Optional[EvaluationCriteria] = None
) -> str:
    """
    Build Stage 2 ranking prompt that considers criteria coverage.
    """

    criteria_instruction = ""
    if criteria:
        criteria_names = ", ".join(c.name for c in criteria.criteria)
        criteria_instruction = f"""
When ranking responses, consider:
1. How thoroughly each response addresses these criteria: {criteria_names}
2. Quality of evidence provided for scores
3. Accuracy of assessments
4. Identification of trade-offs
"""

    prompt = f"""You are evaluating different responses to the following question:

Question: {user_query}
{criteria_instruction}

Here are the responses from different models (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. Consider:
   - Completeness: Did it address all evaluation criteria?
   - Evidence quality: Are scores backed by reasoning?
   - Accuracy: Are the assessments factually correct?
   - Insight: Does it surface important trade-offs?

2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Example format:
FINAL RANKING:
1. Response C
2. Response A
3. Response B

Now provide your evaluation and ranking:"""

    return prompt
```

---

## Acceptance Criteria

- [ ] Stage 1 prompts include all criteria with descriptions
- [ ] Table Stakes clearly marked as pass/fail requirements
- [ ] Scored criteria include weight indicators (Critical/Important/Nice-to-have)
- [ ] Output format instructions enable reliable score extraction
- [ ] Stage 2 prompts reference criteria for evaluation quality
- [ ] Prompts work within model context limits (~8k tokens max for prompt)

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_prompts.py

def test_stage1_prompt_includes_all_criteria():
    """Prompt should mention every criterion"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Accuracy"),
        Criterion(id="c2", name="Cost"),
        Criterion(id="c3", name="GDPR", type=CriterionType.TABLE_STAKES)
    ])
    prompt = build_stage1_prompt_with_criteria("Which API?", criteria)
    assert "Accuracy" in prompt
    assert "Cost" in prompt
    assert "GDPR" in prompt
    assert "TABLE STAKES" in prompt

def test_stage1_prompt_includes_options():
    """Prompt should list options when provided"""
    criteria = EvaluationCriteria(
        criteria=[Criterion(id="c1", name="Quality")],
        options=["Option A", "Option B"]
    )
    prompt = build_stage1_prompt_with_criteria("Which?", criteria)
    assert "Option A" in prompt
    assert "Option B" in prompt

def test_scoring_guide_included():
    """Prompt should include scoring instructions"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id="c1", name="Quality")
    ])
    prompt = build_stage1_prompt_with_criteria("Test", criteria)
    assert "1-10" in prompt or "PASS" in prompt

def test_prompt_under_token_limit():
    """20 criteria prompt should be under 8k tokens"""
    criteria = EvaluationCriteria(criteria=[
        Criterion(id=f"c{i}", name=f"Criterion {i}", description="A" * 100)
        for i in range(20)
    ])
    prompt = build_stage1_prompt_with_criteria("Test query", criteria)
    # Rough estimate: 4 chars per token
    assert len(prompt) < 32000  # 8k tokens * 4 chars
```

### Manual Verification

1. Generate prompt with sample criteria
2. Submit to GPT-4 / Claude and verify output follows format
3. Verify all criteria are addressed in response
4. Test with edge cases (no options, all table stakes, etc.)

---

## Implementation Notes

- Keep prompts concise to leave room for model response
- Consider prompt versioning for A/B testing
- Monitor token usage in production

