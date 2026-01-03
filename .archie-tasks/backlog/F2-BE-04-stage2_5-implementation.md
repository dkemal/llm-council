# Task: F2-BE-04 - Implement stage2_5_refine_responses()

**Version**: 1.0.0
**Created**: 2026-01-02 12:00:00
**Last Updated**: 2026-01-02 12:00:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-tasks/epics/EPIC-F2-iterative-refinement.md`
  - `/.archie-tasks/backlog/F2-BE-01-iteration-state.md`
  - `/.archie-tasks/backlog/F2-BE-02-critique-extraction.md`
  - `/.archie-tasks/backlog/F2-BE-03-refinement-prompts.md`
**Agent**: product-manager

---

## Task Summary

Implement the core Stage 2.5 function that orchestrates model refinement based on peer critiques.

## Complexity: L (8 hours)

## Dependencies
- F2-BE-01 (Iteration State)
- F2-BE-02 (Critique Extraction)
- F2-BE-03 (Refinement Prompts)

## Blocked By
- F2-BE-01, F2-BE-02, F2-BE-03

## Blocks
- F2-BE-06, F2-BE-08

---

## Technical Specification

### File Location
`/backend/council.py` (modify existing file)

### New Function to Add

```python
from typing import List, Dict, Any, Tuple, Optional
from .openrouter import query_models_parallel, query_model
from .config import COUNCIL_MODELS
from .iteration import (
    IterationState, IterationRound, RefinementResult,
    start_new_round, complete_round
)
from .critique import (
    extract_critiques_from_rankings,
    format_critiques_for_refinement
)
from .models import EvaluationCriteria

async def stage2_5_refine_responses(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str],
    iteration_state: IterationState,
    criteria: Optional[EvaluationCriteria] = None
) -> Tuple[List[Dict[str, Any]], IterationRound]:
    """
    Stage 2.5: Refine responses based on peer critiques.

    Each model receives:
    1. Their original response
    2. Critiques from peer evaluations
    3. Instructions to refine their response

    Args:
        user_query: Original user question
        stage1_results: Original responses from Stage 1
        stage2_results: Evaluation/rankings from Stage 2
        label_to_model: Mapping from "Response A" to model names
        iteration_state: Current iteration state
        criteria: Optional evaluation criteria

    Returns:
        Tuple of (refined_results, round_data)
    """
    # Start new round
    round_data = start_new_round(iteration_state)

    # Extract critiques from Stage 2 rankings
    all_critiques = extract_critiques_from_rankings(stage2_results, label_to_model)
    round_data.critiques = all_critiques

    # Create model-to-label mapping (reverse of label_to_model)
    model_to_label = {v: k for k, v in label_to_model.items()}

    # Build refinement prompts for each model
    refinement_tasks = {}

    for result in stage1_results:
        model = result['model']
        original_response = result['response']

        # Find this model's label
        label = model_to_label.get(model)
        if not label:
            continue

        # Get critiques for this model's response
        critiques = all_critiques.get(label, [])

        if not critiques:
            # No critiques - model can maintain position
            refinement_tasks[model] = {
                'original': original_response,
                'critiques': [],
                'prompt': None  # Will skip refinement
            }
            continue

        # Build refinement prompt
        refinement_prompt = build_refinement_prompt(
            user_query=user_query,
            original_response=original_response,
            critiques=critiques,
            criteria=criteria
        )

        refinement_tasks[model] = {
            'original': original_response,
            'critiques': critiques,
            'prompt': refinement_prompt
        }

    # Query models for refinements in parallel
    prompts_to_send = {
        model: [{"role": "user", "content": task['prompt']}]
        for model, task in refinement_tasks.items()
        if task['prompt'] is not None
    }

    refined_responses = {}
    if prompts_to_send:
        # Query all models that need refinement
        responses = await query_models_parallel_with_prompts(prompts_to_send)
        refined_responses = responses

    # Process results
    refined_results = []
    for result in stage1_results:
        model = result['model']
        task = refinement_tasks.get(model, {})
        original = task.get('original', result['response'])

        if model in refined_responses and refined_responses[model]:
            refined_content = refined_responses[model].get('content', '')

            # Detect if model actually changed their response
            changes_made = detect_significant_changes(original, refined_content)

            refinement = RefinementResult(
                model=model,
                original_response=original,
                refined_response=refined_content,
                critiques_addressed=[c.critique_text for c in task.get('critiques', [])],
                changes_made=changes_made,
                change_summary=summarize_changes(original, refined_content) if changes_made else None
            )

            round_data.refinements.append(refinement)

            if changes_made:
                round_data.models_that_changed.append(model)
            else:
                round_data.models_unchanged.append(model)

            refined_results.append({
                'model': model,
                'response': refined_content,
                'original_response': original,
                'refined': True,
                'changes_made': changes_made
            })
        else:
            # No refinement (no critiques or query failed)
            round_data.models_unchanged.append(model)
            refined_results.append({
                'model': model,
                'response': original,
                'refined': False,
                'changes_made': False
            })

    # Estimate tokens used (rough calculation)
    tokens_used = estimate_tokens_used(refinement_tasks, refined_responses)
    complete_round(iteration_state, round_data, tokens_used)

    return refined_results, round_data


def build_refinement_prompt(
    user_query: str,
    original_response: str,
    critiques: List,
    criteria: Optional[EvaluationCriteria] = None
) -> str:
    """
    Build prompt for model to refine their response.
    """
    critiques_text = format_critiques_for_refinement(critiques)

    criteria_context = ""
    if criteria:
        criteria_names = ", ".join(c.name for c in criteria.criteria)
        criteria_context = f"\nThe evaluation criteria were: {criteria_names}\n"

    prompt = f"""You previously provided a response to the following question:

QUESTION: {user_query}
{criteria_context}
YOUR ORIGINAL RESPONSE:
{original_response}

---

PEER FEEDBACK:
{critiques_text}

---

TASK: Please provide a refined version of your response that addresses the peer feedback.

Guidelines:
1. Address each critique point explicitly where valid
2. Maintain your correct insights from the original response
3. If you disagree with a critique, briefly explain why while still considering the point
4. Improve clarity, depth, or accuracy as suggested
5. If the critiques don't apply or your original response was already complete, you may restate your position with any clarifications

REFINED RESPONSE:"""

    return prompt


async def query_models_parallel_with_prompts(
    model_prompts: Dict[str, List[Dict]]
) -> Dict[str, Any]:
    """
    Query multiple models with different prompts in parallel.

    Args:
        model_prompts: Dict mapping model name to messages list

    Returns:
        Dict mapping model name to response
    """
    import asyncio
    from .openrouter import query_model

    async def query_one(model: str, messages: List[Dict]) -> Tuple[str, Any]:
        response = await query_model(model, messages)
        return model, response

    tasks = [
        query_one(model, messages)
        for model, messages in model_prompts.items()
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    response_dict = {}
    for result in results:
        if isinstance(result, Exception):
            continue
        model, response = result
        response_dict[model] = response

    return response_dict


def detect_significant_changes(original: str, refined: str) -> bool:
    """
    Detect if the refined response has significant changes from original.

    Returns True if changes are meaningful, False if essentially unchanged.
    """
    if not refined or not original:
        return False

    # Normalize for comparison
    orig_normalized = original.lower().strip()
    ref_normalized = refined.lower().strip()

    # Check if identical or nearly identical
    if orig_normalized == ref_normalized:
        return False

    # Calculate change ratio
    from difflib import SequenceMatcher
    similarity = SequenceMatcher(None, orig_normalized, ref_normalized).ratio()

    # If >95% similar, consider unchanged
    if similarity > 0.95:
        return False

    # If <50% similar, definitely changed
    if similarity < 0.5:
        return True

    # For middle range, check for new content
    orig_words = set(orig_normalized.split())
    ref_words = set(ref_normalized.split())

    new_words = ref_words - orig_words
    new_word_ratio = len(new_words) / max(len(ref_words), 1)

    # If >10% new words, consider changed
    return new_word_ratio > 0.1


def summarize_changes(original: str, refined: str) -> str:
    """
    Generate brief summary of what changed between responses.
    """
    from difflib import unified_diff

    orig_lines = original.split('\n')
    ref_lines = refined.split('\n')

    diff = list(unified_diff(orig_lines, ref_lines, lineterm=''))

    added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))

    if added > removed:
        return f"Added content (+{added - removed} lines)"
    elif removed > added:
        return f"Condensed content (-{removed - added} lines)"
    else:
        return f"Restructured content ({added} changes)"


def estimate_tokens_used(
    refinement_tasks: Dict,
    responses: Dict
) -> int:
    """
    Estimate tokens used in refinement round.
    """
    total = 0

    for model, task in refinement_tasks.items():
        if task.get('prompt'):
            # Rough estimate: 4 chars per token
            total += len(task['prompt']) // 4

    for model, response in responses.items():
        if response and response.get('content'):
            total += len(response['content']) // 4

    return total
```

---

## Acceptance Criteria

- [ ] Function queries all models with refinement prompts in parallel
- [ ] Each model receives their original response + relevant critiques
- [ ] Models can maintain position if critiques don't apply
- [ ] Changes are detected between original and refined responses
- [ ] Round data captures all refinement results
- [ ] Token usage is estimated for context management
- [ ] Graceful handling of model failures

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_stage2_5.py

@pytest.mark.asyncio
async def test_stage2_5_basic_flow():
    """Should refine responses based on critiques"""
    stage1_results = [
        {"model": "gpt-4", "response": "Original answer about Python"},
        {"model": "claude", "response": "Another answer about Python"}
    ]

    stage2_results = [
        {"model": "gpt-4", "ranking": "Response A lacks examples. Response B is good."},
        {"model": "claude", "ranking": "Response A should be more detailed."}
    ]

    label_to_model = {
        "Response A": "gpt-4",
        "Response B": "claude"
    }

    state = IterationState(enabled=True, max_rounds=2)

    refined, round_data = await stage2_5_refine_responses(
        user_query="What is Python?",
        stage1_results=stage1_results,
        stage2_results=stage2_results,
        label_to_model=label_to_model,
        iteration_state=state
    )

    assert len(refined) == 2
    assert round_data.round_number == 1


def test_detect_significant_changes():
    """Should detect meaningful changes"""
    original = "Python is a programming language."
    refined = "Python is a versatile programming language used for web development, data science, and automation. It features clean syntax and extensive libraries."

    assert detect_significant_changes(original, refined) == True


def test_detect_no_changes():
    """Should detect when response unchanged"""
    original = "Python is a programming language."
    refined = "Python is a programming language."

    assert detect_significant_changes(original, refined) == False


def test_detect_minor_changes():
    """Should detect minor changes as unchanged"""
    original = "Python is a programming language."
    refined = "Python is a programming language!"  # Just punctuation

    assert detect_significant_changes(original, refined) == False


def test_build_refinement_prompt():
    """Should build valid refinement prompt"""
    critiques = [
        CritiqueItem(source_model="m1", target_response="A", critique_text="lacks examples")
    ]

    prompt = build_refinement_prompt(
        user_query="What is Python?",
        original_response="Python is a language.",
        critiques=critiques
    )

    assert "What is Python?" in prompt
    assert "Python is a language." in prompt
    assert "lacks examples" in prompt
    assert "REFINED RESPONSE" in prompt
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_refinement_flow():
    """Test complete Stage 2.5 with real model queries"""
    # ... setup with mock or real models ...

    # Verify:
    # 1. All models received appropriate prompts
    # 2. Critiques were correctly mapped
    # 3. Refined responses captured
    # 4. State updated correctly
```

### Manual Verification

1. Run with real models and observe refinement quality
2. Verify critiques are appropriately addressed
3. Check that unchanged responses are correctly identified
4. Verify token estimates are reasonable

---

## Implementation Notes

- Use asyncio.gather for parallel model queries
- Handle timeout gracefully (model may take longer for refinement)
- Consider retry logic for failed refinements
- Log all prompts and responses for debugging

