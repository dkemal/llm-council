# ARCHIE Loop Analysis & Backlog Automation Strategy

**Version**: 1.0.0
**Created**: 2026-01-02 15:30:00
**Last Updated**: 2026-01-02 15:30:00
**Status**: ✅ VALIDATED (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `~/.claude/commands/archie-loop.md`
  - `~/.claude/plugins/archie-loop/`
  - `/.archie-tasks/backlog/`
**Agent**: prompt-engineer

---

## Executive Summary

`/archie-loop` est un système de boucle itérative avec isolation de session qui permet d'exécuter des tâches répétitives jusqu'à completion. Cette analyse propose un workflow pour automatiser l'exécution séquentielle des tâches backend du backlog LLM Council.

---

## 1. Analyse du Fonctionnement `/archie-loop`

### 1.1 Mécanisme Core

**Architecture en 3 composants** :

1. **Setup Script** (`setup-archie-loop.sh`) :
   - Crée fichier d'état `.claude/archie-loop.local.md`
   - Initialise: iteration=1, prompt, limits, session_id=""
   - Affiche le prompt initial

2. **Stop Hook** (`stop-hook.sh`) :
   - Intercepte fin de réponse assistant
   - Vérifie conditions d'arrêt (max iter, timeout, promise)
   - Bloque exit et renvoie le même prompt si conditions non atteintes

3. **Isolation de Session** :
   - Session ID = SHA256(transcript_path)[:16]
   - Premier trigger → bind session
   - Autres sessions → ignorées

### 1.2 Conditions d'Arrêt

```bash
# 3 façons de terminer une boucle:
1. Max iterations atteint (défaut: 50)
2. Timeout atteint (défaut: 2h)
3. Output de <promise>TEXTE</promise> correspondant à --completion-promise
```

### 1.3 Flux de Données

```
User: /archie-loop "Fix bugs" --completion-promise "All tests pass"
  ↓
Setup: .claude/archie-loop.local.md créé
  ↓
Claude: Travaille sur le prompt
  ↓
Stop Hook: Vérifie <promise>All tests pass</promise>
  ↓ (si absent)
Re-inject: Même prompt, iteration++
  ↓
Claude: Continue... (boucle)
```

### 1.4 Points Clés

✅ **Session isolation forte** - pas d'interférence entre sessions
✅ **Safety limits par défaut** - max 50 iter, 2h timeout
✅ **Completion promise flexible** - condition d'arrêt personnalisable
✅ **État persistant** - survit aux crashes (fichier markdown)
⚠️ **Même prompt à chaque iteration** - pas d'évolution du prompt

---

## 2. Analyse du Backlog LLM Council

### 2.1 Inventaire des Tâches

**Feature 1 - Structured Criteria** (8 backend, 2 frontend):
```
F1-BE-01: Define Criteria Data Schema (S, 2h) - FOUNDATIONAL
F1-BE-02: Criteria Validation Module (S, 2h) - depends: BE-01
F1-BE-03: Criterion-Aware Prompts (M, 4h) - depends: BE-01
F1-BE-04: Stage1 Criteria Integration (M, 4h) - depends: BE-01, BE-03
F1-BE-05: Score Extraction (M, 4h) - depends: BE-01
F1-BE-06: Table Stakes Logic (M, 3h) - depends: BE-01, BE-05
F1-BE-07: Scoring Matrix (M, 4h) - depends: BE-05, BE-06
F1-BE-08: API Endpoints (M, 3h) - depends: BE-02, BE-04, BE-07

F1-FE-01: Criteria UI Design (L, 6h) - depends: BE-01, BE-08
F1-FE-06: Scoring Matrix Component (L, 6h) - depends: BE-07, BE-08
```

**Feature 2 - Iterative Refinement** (3 backend):
```
F2-BE-01: Iteration State (M, 4h) - depends: F1-BE-01
F2-BE-02: Critique Extraction (M, 5h) - depends: F2-BE-01
F2-BE-04: Stage2.5 Implementation (L, 6h) - depends: F2-BE-02
```

### 2.2 Graphe de Dépendances

```
BE-01 (Foundation)
  ├─→ BE-02 → BE-08
  ├─→ BE-03 → BE-04 → BE-08
  ├─→ BE-05 → BE-06 → BE-07 → BE-08
  └─→ F2-BE-01 → F2-BE-02 → F2-BE-04

Ordre d'exécution séquentiel optimal:
1. BE-01 (blocks all)
2. BE-02, BE-03, BE-05 (parallel possible, but sequential safer)
3. BE-04, BE-06 (depends on previous)
4. BE-07 (depends on BE-05, BE-06)
5. BE-08 (depends on BE-02, BE-04, BE-07)
6. F2-BE-01 (depends on BE-01)
7. F2-BE-02 (depends on F2-BE-01)
8. F2-BE-04 (depends on F2-BE-02)
```

---

## 3. Limites de `/archie-loop` pour le Backlog

### 3.1 Pourquoi `/archie-loop` seul ne suffit pas

❌ **Prompt fixe** - ne peut pas avancer à la tâche suivante automatiquement
❌ **Pas de gestion de dépendances** - ne sait pas quand passer à la suivante
❌ **Pas de tracking de completion** - difficile de savoir quelle tâche est done
❌ **Même iteration répétée** - conçu pour raffiner, pas pour progresser

### 3.2 Ce que `/archie-loop` fait bien

✅ **Itération sur une tâche unique** - parfait pour debugging/refinement
✅ **Completion promise** - peut détecter quand une tâche est finie
✅ **Safety limits** - empêche boucles infinies

---

## 4. Proposition de Workflow: `/archie-backlog-execute`

### 4.1 Approche Hybride (Recommandé)

**Concept** : Script orchestrateur qui utilise `/archie-loop` pour chaque tâche individuellement.

```bash
#!/bin/bash
# ~/.claude/bin/archie-backlog-execute

# Execute backlog tasks sequentially with archie-loop per task

BACKLOG_DIR=".archie-tasks/backlog"
COMPLETED_DIR=".archie-tasks/completed"
LOG_FILE=".archie-workspace/logs/backlog-execution-$(date +%Y%m%d-%H%M%S).log"

# Task order (respects dependencies)
TASK_ORDER=(
  "F1-BE-01-criteria-data-schema.md"
  "F1-BE-02-criteria-validation.md"
  "F1-BE-03-criterion-aware-prompts.md"
  "F1-BE-05-score-extraction.md"
  "F1-BE-04-stage1-criteria-integration.md"
  "F1-BE-06-table-stakes-logic.md"
  "F1-BE-07-scoring-matrix.md"
  "F1-BE-08-api-endpoints.md"
)

for TASK_FILE in "${TASK_ORDER[@]}"; do
  TASK_PATH="$BACKLOG_DIR/$TASK_FILE"

  if [[ ! -f "$TASK_PATH" ]]; then
    echo "SKIP: $TASK_FILE not found"
    continue
  fi

  echo "========================================" | tee -a "$LOG_FILE"
  echo "EXECUTING: $TASK_FILE" | tee -a "$LOG_FILE"
  echo "Started: $(date)" | tee -a "$LOG_FILE"
  echo "========================================" | tee -a "$LOG_FILE"

  # Extract task summary for prompt
  TASK_SUMMARY=$(grep -A 2 "## Task Summary" "$TASK_PATH" | tail -1)

  # Build archie-loop prompt
  PROMPT="Execute task $TASK_FILE: $TASK_SUMMARY. Follow acceptance criteria exactly. Run all tests. When complete and validated, output: <promise>TASK_COMPLETE</promise>"

  # Launch archie-loop for this task
  /archie-loop "$PROMPT" \
    --completion-promise "TASK_COMPLETE" \
    --max-iterations 20 \
    --timeout 1

  # Move to completed
  mkdir -p "$COMPLETED_DIR"
  mv "$TASK_PATH" "$COMPLETED_DIR/"

  echo "COMPLETED: $TASK_FILE at $(date)" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
done

echo "All tasks completed!" | tee -a "$LOG_FILE"
```

**Problème** : `/archie-loop` n'est pas appelable depuis un script bash externe - c'est une commande Claude.

---

### 4.2 Approche Pure Claude (Solution Viable)

**Single Mega-Loop avec State Machine**

```markdown
/archie-loop "Execute all backend tasks from backlog in dependency order.

TASK QUEUE:
1. F1-BE-01-criteria-data-schema.md
2. F1-BE-02-criteria-validation.md
3. F1-BE-03-criterion-aware-prompts.md
4. F1-BE-05-score-extraction.md
5. F1-BE-04-stage1-criteria-integration.md
6. F1-BE-06-table-stakes-logic.md
7. F1-BE-07-scoring-matrix.md
8. F1-BE-08-api-endpoints.md

PROCESS PER ITERATION:
1. Check .archie-tasks/backlog-state.json for current task
2. If no state file, start with task 1
3. Read task file from .archie-tasks/backlog/{task}
4. Execute task following acceptance criteria
5. Run validation steps and tests
6. If task validated:
   - Mark as complete in backlog-state.json
   - Move task file to .archie-tasks/completed/
   - Advance to next task
7. If all 8 tasks complete, output: <promise>ALL_BACKEND_TASKS_COMPLETE</promise>

RULES:
- Never skip tasks
- Never mark incomplete tasks as done
- Always run tests before marking complete
- Log progress to .archie-workspace/logs/backlog-execution.log
- If stuck on a task for 3+ iterations, request human intervention

Agent: @senior-backend-engineer

When ALL 8 tasks are validated and complete, output:
<promise>ALL_BACKEND_TASKS_COMPLETE</promise>" \
--completion-promise "ALL_BACKEND_TASKS_COMPLETE" \
--max-iterations 100 \
--timeout 8
```

**State file format** (`.archie-tasks/backlog-state.json`):
```json
{
  "current_task_index": 0,
  "tasks": [
    {
      "id": "F1-BE-01",
      "file": "F1-BE-01-criteria-data-schema.md",
      "status": "in_progress",
      "iterations": 2,
      "started_at": "2026-01-02T15:00:00Z",
      "completed_at": null
    },
    {
      "id": "F1-BE-02",
      "file": "F1-BE-02-criteria-validation.md",
      "status": "pending",
      "iterations": 0,
      "started_at": null,
      "completed_at": null
    }
  ],
  "total_iterations": 5,
  "started_at": "2026-01-02T15:00:00Z",
  "last_updated": "2026-01-02T15:30:00Z"
}
```

---

### 4.3 Approche Manuelle Guidée (Pragmatique)

**Pour chaque tâche individuellement** :

```bash
# Tâche 1
/archie-loop "Execute F1-BE-01: Define Criteria Data Schema.
Follow specs in .archie-tasks/backlog/F1-BE-01-criteria-data-schema.md.
Create /backend/models.py with Pydantic models.
Run all acceptance tests.
When validated, output: <promise>F1-BE-01_COMPLETE</promise>" \
--completion-promise "F1-BE-01_COMPLETE" \
--max-iterations 15 \
--timeout 1

# Tâche 2 (après validation de 1)
/archie-loop "Execute F1-BE-02: Criteria Validation Module.
Follow specs in .archie-tasks/backlog/F1-BE-02-criteria-validation.md.
Depends on F1-BE-01 (already complete).
Create /backend/validation.py.
Run all unit tests.
When validated, output: <promise>F1-BE-02_COMPLETE</promise>" \
--completion-promise "F1-BE-02_COMPLETE" \
--max-iterations 15 \
--timeout 1

# ... répéter pour chaque tâche
```

**Avantages** :
- ✅ Contrôle total sur chaque tâche
- ✅ Validation humaine entre chaque étape
- ✅ Pas de risque de skip de tâche
- ✅ Debugging facile

**Inconvénients** :
- ❌ Requiert intervention manuelle entre chaque tâche
- ❌ Pas d'automatisation complète

---

## 5. Recommandation Finale

### 5.1 Approche Recommandée: **Mega-Loop avec State Machine** (4.2)

**Pourquoi** :
1. ✅ **Automatisation complète** - aucune intervention entre tâches
2. ✅ **Traçabilité** - state file JSON track progress
3. ✅ **Robustesse** - peut reprendre après interruption
4. ✅ **Safety nets** - max 100 iter, 8h timeout, stuck detection
5. ✅ **Single command** - une seule invocation

**Risques** :
- ⚠️ Longue durée (8h max) - possibilité d'interruption
- ⚠️ Complexité du prompt - agent doit gérer state machine
- ⚠️ Validation automatique - risque de faux positifs

**Mitigations** :
- State file permet reprise après crash
- Human intervention si stuck 3+ iterations
- Logs détaillés dans `.archie-workspace/logs/`

### 5.2 Prompt Production-Ready

```markdown
Execute all Feature 1 backend tasks in dependency order using state machine pattern.

INITIALIZATION:
1. Check if .archie-tasks/backlog-state.json exists
2. If not, create it with all 8 tasks as "pending"
3. Load current task index

TASK QUEUE (dependency-ordered):
1. F1-BE-01-criteria-data-schema.md
2. F1-BE-02-criteria-validation.md
3. F1-BE-03-criterion-aware-prompts.md
4. F1-BE-05-score-extraction.md
5. F1-BE-04-stage1-criteria-integration.md
6. F1-BE-06-table-stakes-logic.md
7. F1-BE-07-scoring-matrix.md
8. F1-BE-08-api-endpoints.md

PER ITERATION WORKFLOW:
1. Load backlog-state.json
2. Get current task from tasks[current_task_index]
3. If task.status == "pending": Set to "in_progress", increment task.iterations
4. If task.status == "in_progress":
   a. Read task spec from .archie-tasks/backlog/{task.file}
   b. Execute implementation following acceptance criteria
   c. Run validation steps and unit tests
   d. If all tests pass AND acceptance criteria met:
      - Set task.status = "complete"
      - Set task.completed_at = now
      - Move .archie-tasks/backlog/{task.file} → .archie-tasks/completed/
      - Increment current_task_index
      - Log completion to .archie-workspace/logs/backlog-execution.log
   e. If task.iterations >= 3 AND not complete:
      - Log "STUCK on {task.id} - requesting human review"
      - Output detailed diagnostics
      - PAUSE (don't advance, wait for manual fix)
5. Update backlog-state.json with latest state
6. If current_task_index >= 8: ALL TASKS COMPLETE
   - Output: <promise>ALL_BACKEND_TASKS_COMPLETE</promise>
7. Otherwise, continue to next iteration

AGENT ASSIGNMENT:
- Primary: @senior-backend-engineer
- Fallback: @backend-architect (for complex tasks)

STRICT RULES:
- NEVER skip validation steps
- NEVER mark task complete without passing tests
- NEVER modify backlog files after moving to completed/
- ALWAYS update state file after each action
- ALWAYS log significant events

OUTPUT FORMAT PER ITERATION:
```
=== ITERATION {N} ===
Current Task: {task.id} ({task.status})
Action: {what was done this iteration}
Tests: {pass/fail summary}
Next: {next action or task}
State: {brief state summary}
```

COMPLETION CONDITION:
When all 8 tasks have status="complete", output EXACTLY:
<promise>ALL_BACKEND_TASKS_COMPLETE</promise>

LOGS:
- Append to: .archie-workspace/logs/backlog-execution-$(date +%Y%m%d).log
- Include: timestamp, task, action, result, tests

ERROR HANDLING:
- If test fails: Debug, fix, re-run (max 3 attempts per iteration)
- If dependency missing: Verify previous task completion in state
- If file not found: Check backlog/ vs completed/ directories
- If stuck: Request human intervention after 3 iterations on same task
```

### 5.3 Commande Finale

```bash
/archie-loop "Execute all Feature 1 backend tasks in dependency order using state machine pattern.

INITIALIZATION:
1. Check if .archie-tasks/backlog-state.json exists
2. If not, create it with all 8 tasks as pending
3. Load current task index

TASK QUEUE (dependency-ordered):
1. F1-BE-01-criteria-data-schema.md
2. F1-BE-02-criteria-validation.md
3. F1-BE-03-criterion-aware-prompts.md
4. F1-BE-05-score-extraction.md
5. F1-BE-04-stage1-criteria-integration.md
6. F1-BE-06-table-stakes-logic.md
7. F1-BE-07-scoring-matrix.md
8. F1-BE-08-api-endpoints.md

PER ITERATION:
1. Load state, get current task
2. Read task spec from .archie-tasks/backlog/{file}
3. Execute implementation + tests
4. If validated: mark complete, move to completed/, advance index
5. If stuck 3+ iterations: request human help
6. Update state JSON
7. If all 8 complete: output <promise>ALL_BACKEND_TASKS_COMPLETE</promise>

Agent: @senior-backend-engineer
Log to: .archie-workspace/logs/backlog-execution.log

RULES: Never skip validation, never fake completion, always test" \
--completion-promise "ALL_BACKEND_TASKS_COMPLETE" \
--max-iterations 100 \
--timeout 8
```

---

## 6. Exemple d'Exécution Concrète

### 6.1 Tâche Simple (F1-BE-01)

**Commande** :
```bash
/archie-loop "Execute F1-BE-01: Define Criteria Data Schema.

SPEC: .archie-tasks/backlog/F1-BE-01-criteria-data-schema.md

DELIVERABLES:
- Create backend/models.py with Pydantic models
- Implement: Criterion, CriterionType, WeightLevel, EvaluationCriteria, CriterionScore, OptionScores
- Add validators for unique names, 1-20 criteria limit, numeric_weight calculation

VALIDATION:
- Create backend/tests/test_models.py
- Run: uv run pytest backend/tests/test_models.py -v
- All 5 tests must pass (see acceptance criteria in spec)

COMPLETION:
When all tests pass and models match spec exactly, output:
<promise>F1-BE-01_COMPLETE</promise>" \
--completion-promise "F1-BE-01_COMPLETE" \
--max-iterations 15 \
--timeout 1
```

**Iterations attendues** :
```
Iteration 1: Read spec, create models.py with basic structure
Iteration 2: Add validators and enums
Iteration 3: Create test file with 5 tests
Iteration 4: Run tests, debug failures
Iteration 5: Fix validation issues, re-run tests
Iteration 6: All tests pass → Output <promise>F1-BE-01_COMPLETE</promise> → STOP
```

### 6.2 Séquence de 2 Tâches (BE-01 → BE-02)

**Commande 1** :
```bash
/archie-loop "Execute F1-BE-01 (see spec). When complete: <promise>BE01_DONE</promise>" \
--completion-promise "BE01_DONE" --max-iterations 15 --timeout 1
```

**Validation manuelle** : Vérifier que `backend/models.py` et tests existent et passent.

**Commande 2** :
```bash
/archie-loop "Execute F1-BE-02: Criteria Validation Module.

SPEC: .archie-tasks/backlog/F1-BE-02-criteria-validation.md

DEPENDENCIES: F1-BE-01 (already complete, models.py exists)

DELIVERABLES:
- Create backend/validation.py
- Implement: validate_criteria(), detect_criteria_conflicts(), suggest_missing_criteria(), normalize_weight()
- Import from backend.models

VALIDATION:
- Create backend/tests/test_validation.py
- Run: uv run pytest backend/tests/test_validation.py -v
- All 4 tests must pass

COMPLETION:
When all tests pass and validation <100ms for 20 criteria, output:
<promise>F1-BE-02_COMPLETE</promise>" \
--completion-promise "F1-BE-02_COMPLETE" \
--max-iterations 15 \
--timeout 1
```

---

## 7. Alternative: Script Helper (Non-Loop)

Si `/archie-loop` s'avère trop complexe, alternative simple :

```bash
#!/bin/bash
# .archie/scripts/execute-backlog.sh

# Simple task executor without loop - relies on agent intelligence

TASK=$1
AGENT="@senior-backend-engineer"

if [[ -z "$TASK" ]]; then
  echo "Usage: $0 <task-id>"
  echo "Example: $0 F1-BE-01"
  exit 1
fi

TASK_FILE=".archie-tasks/backlog/${TASK}-*.md"

if [[ ! -f $TASK_FILE ]]; then
  echo "Task not found: $TASK_FILE"
  exit 1
fi

# Extract task summary
SUMMARY=$(grep -A 2 "## Task Summary" $TASK_FILE | tail -1)

# Call agent directly (no loop, single shot)
echo "Executing $TASK: $SUMMARY"
echo "Agent: $AGENT"
echo "Spec: $TASK_FILE"
echo ""
echo "Please execute this task following the spec exactly."
echo "Run all tests and validation steps."
echo "When complete, report status."

# User then manually verifies and runs next task
```

**Usage** :
```bash
.archie/scripts/execute-backlog.sh F1-BE-01
# ... agent works, user validates
.archie/scripts/execute-backlog.sh F1-BE-02
# ... repeat
```

---

## 8. Conclusion

### 8.1 Recommandation par Use Case

| Use Case | Approche | Commande |
|----------|----------|----------|
| **Production (automatisation complète)** | Mega-Loop + State Machine (4.2) | Voir section 5.3 |
| **Développement (contrôle max)** | Loop par tâche (4.3) | Voir section 6.1 |
| **Prototypage (simplicité)** | Script helper (7) | `.archie/scripts/execute-backlog.sh` |

### 8.2 Next Steps

1. **Tester avec F1-BE-01** - Valider l'approche sur tâche simple
2. **Affiner le prompt** - Ajuster selon résultats iteration 1
3. **Implémenter state machine** - Si mega-loop choisi
4. **Documenter patterns** - Capturer learnings pour futures features

### 8.3 Métriques de Succès

- ✅ Toutes les tâches complétées sans intervention manuelle
- ✅ Tous les tests passent
- ✅ Respect des dépendances (pas de skip)
- ✅ Logs détaillés pour debugging
- ✅ State recoverable après interruption

---

## Annexes

### A. Backlog State Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "current_task_index": {"type": "integer", "minimum": 0},
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string", "pattern": "^F[0-9]+-[A-Z]+-[0-9]+$"},
          "file": {"type": "string"},
          "status": {"enum": ["pending", "in_progress", "complete", "blocked", "failed"]},
          "iterations": {"type": "integer", "minimum": 0},
          "started_at": {"type": ["string", "null"], "format": "date-time"},
          "completed_at": {"type": ["string", "null"], "format": "date-time"},
          "error": {"type": ["string", "null"]}
        },
        "required": ["id", "file", "status", "iterations"]
      }
    },
    "total_iterations": {"type": "integer", "minimum": 0},
    "started_at": {"type": "string", "format": "date-time"},
    "last_updated": {"type": "string", "format": "date-time"}
  },
  "required": ["current_task_index", "tasks", "total_iterations", "started_at", "last_updated"]
}
```

### B. Log Format Example

```
2026-01-02 15:30:00 | INIT | Created backlog-state.json with 8 tasks
2026-01-02 15:30:05 | START | F1-BE-01 | Iteration 1
2026-01-02 15:32:10 | ACTION | F1-BE-01 | Created backend/models.py (142 lines)
2026-01-02 15:32:45 | TEST | F1-BE-01 | Running pytest backend/tests/test_models.py
2026-01-02 15:32:50 | TEST | F1-BE-01 | PASS (5/5 tests)
2026-01-02 15:32:55 | COMPLETE | F1-BE-01 | Validated, moving to completed/
2026-01-02 15:33:00 | START | F1-BE-02 | Iteration 7
...
```

### C. Error Handling Scenarios

| Error | Detection | Action |
|-------|-----------|--------|
| Test failure | pytest exit code != 0 | Debug, fix, retry (max 3x per iteration) |
| Missing dependency | Import error | Verify previous task in state, report if blocked |
| Stuck (3+ iter) | task.iterations >= 3 && status != complete | Log diagnostics, request human intervention |
| Timeout | archie-loop timeout reached | Save state, log partial progress, allow resume |
| State corruption | JSON parse error | Backup state, recreate from backlog files |

---

**END OF ANALYSIS**
