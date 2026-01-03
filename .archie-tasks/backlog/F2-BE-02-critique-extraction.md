# Task: F2-BE-02 - Extract Critiques from Stage 2 Rankings

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

Create parser to extract actionable critique points from Stage 2 ranking evaluations that can be used to guide response refinement.

## Complexity: M (4 hours)

## Dependencies
- None (uses existing Stage 2 output)

## Blocked By
- None

## Blocks
- F2-BE-03, F2-BE-04

---

## Technical Specification

### File Location
`/backend/critique.py` (new file)

### Functions to Implement

```python
import re
from typing import List, Dict, Tuple
from .iteration import CritiqueItem

def extract_critiques_from_rankings(
    stage2_results: List[Dict],
    label_to_model: Dict[str, str]
) -> Dict[str, List[CritiqueItem]]:
    """
    Extract critique points from Stage 2 ranking evaluations.

    Args:
        stage2_results: Results from stage2_collect_rankings
        label_to_model: Mapping from "Response A" to model names

    Returns:
        Dict mapping response labels to list of critiques about that response
    """
    all_critiques = {label: [] for label in label_to_model.keys()}

    for ranking in stage2_results:
        evaluator_model = ranking['model']
        ranking_text = ranking['ranking']

        # Extract critiques for each response mentioned
        for response_label in label_to_model.keys():
            critiques = extract_critiques_for_response(
                ranking_text,
                response_label,
                evaluator_model
            )
            all_critiques[response_label].extend(critiques)

    # Deduplicate and prioritize critiques
    for label in all_critiques:
        all_critiques[label] = deduplicate_critiques(all_critiques[label])
        all_critiques[label] = prioritize_critiques(all_critiques[label])

    return all_critiques


def extract_critiques_for_response(
    ranking_text: str,
    response_label: str,
    evaluator_model: str
) -> List[CritiqueItem]:
    """
    Extract critiques about a specific response from evaluation text.
    """
    critiques = []

    # Find section about this response
    section_patterns = [
        rf'{response_label}[:\s]+(.*?)(?=Response [A-Z]|FINAL RANKING|$)',
        rf'(?:evaluating|analyzing|reviewing)\s+{response_label}[:\s]*(.*?)(?=Response [A-Z]|FINAL RANKING|$)',
    ]

    section_text = ""
    for pattern in section_patterns:
        match = re.search(pattern, ranking_text, re.IGNORECASE | re.DOTALL)
        if match:
            section_text = match.group(1)
            break

    if not section_text:
        # Fallback: look for any sentence mentioning the response
        sentences = re.split(r'[.!?]+', ranking_text)
        section_text = " ".join(
            s for s in sentences
            if response_label.lower() in s.lower()
        )

    if not section_text:
        return critiques

    # Extract negative points (critiques)
    critique_patterns = [
        # "Response A lacks X"
        (r'lacks?\s+(.+?)(?:\.|,|but|however)', 'high'),
        # "Response A fails to X"
        (r'fails?\s+to\s+(.+?)(?:\.|,|but|however)', 'high'),
        # "Response A does not X"
        (r'does(?:n\'t| not)\s+(.+?)(?:\.|,|but|however)', 'medium'),
        # "Response A could improve X"
        (r'could\s+(?:improve|enhance|address)\s+(.+?)(?:\.|,|$)', 'medium'),
        # "Response A misses X"
        (r'miss(?:es|ing)?\s+(.+?)(?:\.|,|but|however)', 'high'),
        # "weakness" or "limitation"
        (r'weakness(?:es)?[:\s]+(.+?)(?:\.|,|$)', 'high'),
        (r'limitation[s]?[:\s]+(.+?)(?:\.|,|$)', 'high'),
        # "however, X"
        (r'however[,\s]+(.+?)(?:\.|$)', 'medium'),
        # "but X"
        (r'\bbut\s+(.+?)(?:\.|$)', 'low'),
        # "should have X"
        (r'should\s+(?:have\s+)?(.+?)(?:\.|,|$)', 'medium'),
        # "doesn't address X"
        (r'doesn\'t\s+(?:address|cover|mention)\s+(.+?)(?:\.|,|$)', 'high'),
        # "incomplete" mentions
        (r'incomplete\s+(?:analysis|coverage|discussion)\s+(?:of\s+)?(.+?)(?:\.|,|$)', 'high'),
    ]

    for pattern, severity in critique_patterns:
        matches = re.findall(pattern, section_text, re.IGNORECASE)
        for match in matches:
            critique_text = match.strip()
            if len(critique_text) > 10 and len(critique_text) < 500:
                critiques.append(CritiqueItem(
                    source_model=evaluator_model,
                    target_response=response_label,
                    critique_text=critique_text,
                    severity=severity
                ))

    return critiques


def deduplicate_critiques(critiques: List[CritiqueItem]) -> List[CritiqueItem]:
    """
    Remove duplicate or very similar critiques.
    """
    if not critiques:
        return critiques

    unique = []
    seen_texts = set()

    for critique in critiques:
        # Normalize text for comparison
        normalized = critique.critique_text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)

        # Check for duplicates
        is_duplicate = False
        for seen in seen_texts:
            if normalized == seen:
                is_duplicate = True
                break
            # Check for high similarity (>70% overlap)
            if calculate_overlap(normalized, seen) > 0.7:
                is_duplicate = True
                break

        if not is_duplicate:
            unique.append(critique)
            seen_texts.add(normalized)

    return unique


def calculate_overlap(text1: str, text2: str) -> float:
    """Calculate word overlap ratio between two texts."""
    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def prioritize_critiques(
    critiques: List[CritiqueItem],
    max_critiques: int = 5
) -> List[CritiqueItem]:
    """
    Prioritize critiques by severity and consensus.

    Returns top N critiques that should be addressed.
    """
    if len(critiques) <= max_critiques:
        return critiques

    # Score critiques
    severity_scores = {'high': 3, 'medium': 2, 'low': 1}

    scored = []
    for critique in critiques:
        score = severity_scores.get(critique.severity, 1)

        # Boost if multiple sources mention similar issue
        similar_count = sum(
            1 for c in critiques
            if c != critique and calculate_overlap(
                c.critique_text.lower(),
                critique.critique_text.lower()
            ) > 0.3
        )
        score += similar_count * 0.5

        scored.append((score, critique))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    return [critique for _, critique in scored[:max_critiques]]


def format_critiques_for_refinement(
    critiques: List[CritiqueItem],
    include_source: bool = False
) -> str:
    """
    Format critiques into prompt-ready text for refinement.
    """
    if not critiques:
        return "No specific critiques to address."

    lines = ["Your response received the following feedback from peer reviewers:\n"]

    for i, critique in enumerate(critiques, 1):
        severity_marker = {"high": "[!]", "medium": "[-]", "low": "[ ]"}
        marker = severity_marker.get(critique.severity, "[-]")

        line = f"{i}. {marker} {critique.critique_text}"
        if include_source:
            # Anonymize source
            line += f" (from another model)"

        lines.append(line)

    lines.append("\nPlease address these points in your refined response.")

    return "\n".join(lines)


def summarize_critiques_by_theme(
    all_critiques: Dict[str, List[CritiqueItem]]
) -> Dict[str, Dict[str, int]]:
    """
    Summarize critiques by common themes for analysis.

    Returns dict mapping themes to occurrence counts.
    """
    themes = {
        "missing_detail": ["lacks", "missing", "incomplete", "should have"],
        "accuracy": ["incorrect", "wrong", "inaccurate", "error"],
        "depth": ["shallow", "superficial", "more detail", "deeper"],
        "structure": ["organization", "structure", "format", "clarity"],
        "evidence": ["evidence", "source", "citation", "support"],
        "edge_cases": ["edge case", "exception", "corner case", "scenario"]
    }

    theme_counts = {theme: 0 for theme in themes}

    for label, critiques in all_critiques.items():
        for critique in critiques:
            text_lower = critique.critique_text.lower()
            for theme, keywords in themes.items():
                if any(kw in text_lower for kw in keywords):
                    theme_counts[theme] += 1

    return theme_counts
```

---

## Acceptance Criteria

- [ ] Extracts critique points from Stage 2 evaluation text
- [ ] Associates critiques with target response labels
- [ ] Assigns severity levels (high/medium/low)
- [ ] Deduplicates similar critiques
- [ ] Prioritizes most important critiques (max 5 per response)
- [ ] Formats critiques for refinement prompts
- [ ] Handles various evaluation text formats

---

## Validation Steps

### Unit Tests

```python
# /backend/tests/test_critique.py

def test_extract_lacks_critique():
    """Should extract 'lacks X' patterns"""
    text = "Response A provides good overview but lacks specific examples."
    critiques = extract_critiques_for_response(text, "Response A", "gpt-4")

    assert len(critiques) >= 1
    assert any("specific examples" in c.critique_text for c in critiques)


def test_extract_fails_to_critique():
    """Should extract 'fails to X' patterns"""
    text = "Response B fails to address the security implications."
    critiques = extract_critiques_for_response(text, "Response B", "claude")

    assert len(critiques) >= 1
    assert any("security" in c.critique_text for c in critiques)


def test_high_severity_for_critical_issues():
    """Critical patterns should have high severity"""
    text = "Response A misses the main point entirely."
    critiques = extract_critiques_for_response(text, "Response A", "gpt-4")

    assert len(critiques) >= 1
    assert critiques[0].severity == "high"


def test_deduplicate_similar_critiques():
    """Should remove duplicate critiques"""
    critiques = [
        CritiqueItem(source_model="m1", target_response="A", critique_text="lacks examples"),
        CritiqueItem(source_model="m2", target_response="A", critique_text="lacks examples"),
        CritiqueItem(source_model="m3", target_response="A", critique_text="missing examples"),
    ]

    unique = deduplicate_critiques(critiques)
    assert len(unique) <= 2  # Should merge similar


def test_prioritize_high_severity():
    """High severity critiques should rank first"""
    critiques = [
        CritiqueItem(source_model="m1", target_response="A", critique_text="minor formatting", severity="low"),
        CritiqueItem(source_model="m2", target_response="A", critique_text="misses key point", severity="high"),
        CritiqueItem(source_model="m3", target_response="A", critique_text="could be clearer", severity="medium"),
    ]

    prioritized = prioritize_critiques(critiques, max_critiques=2)

    assert len(prioritized) == 2
    assert prioritized[0].severity == "high"


def test_format_for_refinement():
    """Should format critiques as readable list"""
    critiques = [
        CritiqueItem(source_model="m1", target_response="A", critique_text="Add more examples", severity="high"),
        CritiqueItem(source_model="m2", target_response="A", critique_text="Clarify terminology", severity="medium"),
    ]

    formatted = format_critiques_for_refinement(critiques)

    assert "feedback" in formatted.lower()
    assert "Add more examples" in formatted
    assert "Clarify terminology" in formatted


def test_extract_from_full_ranking():
    """Should extract from realistic ranking text"""
    ranking_text = """
    Response A provides a comprehensive overview of the topic. However, it lacks specific benchmarks
    and fails to address edge cases. The analysis is thorough but could improve on citation of sources.

    Response B is more concise but misses important details about pricing. It does not cover
    the enterprise use case scenario.

    FINAL RANKING:
    1. Response A
    2. Response B
    """

    critiques_a = extract_critiques_for_response(ranking_text, "Response A", "gpt-4")
    critiques_b = extract_critiques_for_response(ranking_text, "Response B", "gpt-4")

    assert len(critiques_a) >= 2
    assert len(critiques_b) >= 1
```

### Manual Verification

1. Run extractor on real Stage 2 outputs
2. Verify critiques are actionable and specific
3. Check severity assignments are reasonable
4. Verify formatting is clear for LLM consumption

---

## Implementation Notes

- Critique extraction is heuristic - will need tuning
- Consider using spaCy for better NLP extraction in future
- Log extraction failures for pattern improvement
- Keep critique text concise (<500 chars)

