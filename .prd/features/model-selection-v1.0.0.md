# Model Selection Feature - PRD

**Version**: 1.0.0
**Created**: 2026-01-03 17:00:00
**Last Updated**: 2026-01-03 17:00:00
**Status**: DRAFT (2026-01-03)
**Supersedes**: N/A
**Related Docs**: `/.prd/features/deliberation-improvements-v1.0.0.md`
**Agent**: Product Manager

---

## Executive Summary

- **Elevator Pitch**: Let users pick which AI models debate and which one summarizes, instead of being stuck with hardcoded defaults.
- **Problem Statement**: Users cannot adapt the council composition to their needs - they are locked into 3 specific models and a chairman that fails on complex synthesis tasks.
- **Target Audience**: Power users who want control over model selection for cost, quality, or provider preference reasons.
- **Unique Selling Proposition**: Dynamic model configuration without code changes, with smart validation to prevent misconfiguration.
- **Success Metrics**: 100% of users can successfully configure their preferred models; 0 chairman synthesis failures due to weak model selection.

---

## Problem Analysis

### What specific problem are we solving?

1. **Hardcoded models**: Council models are defined in `backend/config.py` - users must edit code to change them
2. **Chairman failures**: Current chairman (Gemini Flash) struggles with complex synthesis, but users cannot select a more capable model
3. **No visibility into available models**: Users don't know which models they can use based on their configured API keys
4. **No persistence**: Even if selection were possible, preferences would be lost between sessions

### Who experiences this problem most acutely?

- Power users experimenting with different model combinations
- Users with specific provider preferences (cost, privacy, quality)
- Users experiencing synthesis failures with the default chairman

### Current workarounds

- Edit `backend/config.py` directly (requires restart)
- Set environment variables `COUNCIL_MODELS` and `CHAIRMAN_MODEL` (requires restart)
- Accept suboptimal results from hardcoded configuration

### Cost of not solving

- Users abandon the tool due to inflexibility
- Support burden for configuration questions
- Suboptimal deliberation quality from bad model combinations

---

## JTBD Analysis

### Core Job Story

When **I want to run a council deliberation**
I want to **select which models participate and which synthesizes**
So I can **optimize for my priorities (cost, quality, speed, provider preference)**

### Forces Analysis

| Force | Description |
|-------|-------------|
| **Push** (away from current) | Fixed models don't match my needs; chairman fails on complex tasks; can't use models I'm paying for |
| **Pull** (toward new) | Control over model selection; ability to use powerful chairman; experimentation capability |
| **Anxiety** (resistance) | Fear of misconfiguration; worry about breaking the system; uncertainty about which models work well |
| **Habit** (inertia) | Current setup "works enough"; editing config.py is acceptable for some users |

### ODI Score: 16/20

- **Importance**: 9/10 (core to product value proposition)
- **Satisfaction with current**: 3/10 (workaround exists but poor UX)
- **Priority**: P0 - Clear user value demonstrated

---

## User Stories

### US-1: Discover Available Models
**As a** user setting up the council
**I want to** see which models are available based on my configured API keys
**So that** I know my options before selecting

**Acceptance Criteria:**
- Given I have `OPENAI_API_KEY` configured, when I request available models, then I see OpenAI models listed
- Given I have `ANTHROPIC_API_KEY` configured, when I request available models, then I see Anthropic models listed
- Given I have `GOOGLE_API_KEY` configured, when I request available models, then I see Google models listed
- Given I have `OPENROUTER_API_KEY` configured, when I request available models, then I see OpenRouter-specific models listed
- Given no API keys are configured, when I request available models, then I see an empty list with a clear message

### US-2: Select Council Models
**As a** user configuring a deliberation
**I want to** select exactly 3 models for my council
**So that** I can customize the deliberation participants

**Acceptance Criteria:**
- Given I am on the council configuration UI, when I view model selection, then I see a list of available models with provider badges
- Given I have selected 2 models, when I try to start deliberation, then I see a validation error requiring exactly 3
- Given I have selected 3 models, when I view selection, then I see a checkmark/confirmation
- Given I select more than 3 models, when the 4th is clicked, then the oldest selection is deselected (FIFO) or blocked with message

### US-3: Select Chairman Model
**As a** user configuring a deliberation
**I want to** select a chairman model from a curated list of powerful models
**So that** synthesis quality is ensured

**Acceptance Criteria:**
- Given I am selecting a chairman, when I view options, then I only see models marked as "powerful" (capable of complex synthesis)
- Given I select a non-powerful model, when I try to confirm, then I see a warning about potential synthesis issues
- Given I select a powerful model, when I confirm, then it's set as chairman without warning
- Edge case: If no powerful models are available, show clear error with guidance on which API keys to add

### US-4: Persist Model Preferences
**As a** returning user
**I want** my model selections to be remembered
**So that** I don't have to reconfigure every session

**Acceptance Criteria:**
- Given I have configured models, when I close and reopen the app, then my selections are preserved
- Given I want to reset to defaults, when I click "Reset to defaults", then hardcoded defaults are restored
- Given my saved model is no longer available (API key removed), when I load preferences, then I see a warning and graceful fallback

---

## Functional Requirements

### FR-1: Available Models Endpoint

**Endpoint**: `GET /api/models/available`

**Response Schema**:
```json
{
  "providers": {
    "openai": {
      "available": true,
      "models": [
        {
          "id": "openai/gpt-4o",
          "name": "GPT-4o",
          "tier": "powerful",
          "context_window": 128000
        },
        {
          "id": "openai/gpt-4o-mini",
          "name": "GPT-4o Mini",
          "tier": "standard",
          "context_window": 128000
        }
      ]
    },
    "anthropic": { ... },
    "google": { ... },
    "openrouter": { ... }
  },
  "mode": "direct"
}
```

**Model Tier Classification**:
- `powerful`: Suitable for chairman role (GPT-4o, Claude Sonnet/Opus, Gemini Pro/2.0)
- `standard`: Good for council members, not recommended as chairman
- `lightweight`: Fast/cheap, council only (GPT-4o-mini, Claude Haiku, Gemini Flash)

### FR-2: Model Selection State

**Frontend State**:
```typescript
interface ModelSelection {
  councilModels: string[];  // exactly 3 model IDs
  chairmanModel: string;    // 1 model ID, must be tier=powerful
}
```

**Validation Rules**:
- Council must have exactly 3 models
- Chairman must be from `powerful` tier (warning if not, not blocking)
- All selected models must be currently available
- Same model cannot be in council multiple times

### FR-3: Preferences Persistence

**Storage**: `localStorage` key `llm-council-preferences`

```json
{
  "version": 1,
  "councilModels": ["openai/gpt-4o", "anthropic/claude-sonnet-4-20250514", "google/gemini-2.5-pro"],
  "chairmanModel": "anthropic/claude-sonnet-4-20250514",
  "savedAt": "2026-01-03T17:00:00Z"
}
```

**Load Behavior**:
1. Load preferences from localStorage
2. Validate all models still available
3. If any unavailable, show warning and use defaults for those slots
4. Apply valid preferences

### FR-4: Model Registry

**Backend**: New module `backend/models_registry.py`

Defines known models with metadata:
```python
MODEL_REGISTRY = {
    "openai/gpt-4o": {
        "name": "GPT-4o",
        "provider": "openai",
        "tier": "powerful",
        "context_window": 128000,
    },
    "openai/gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "provider": "openai",
        "tier": "lightweight",
        "context_window": 128000,
    },
    # ... more models
}
```

### FR-5: UI Components

**Settings Panel** (collapsible, above query input):
- Section: "Council Models" with 3 selection slots
- Section: "Chairman Model" with 1 selection slot and tier badge
- Button: "Reset to Defaults"
- Visual: Provider icons/colors for quick identification

**Model Selector Component**:
- Dropdown or pill-selection interface
- Shows: Model name, provider badge, tier indicator
- Disabled state for unavailable models

---

## Non-Functional Requirements

### NFR-1: Performance
- Available models endpoint must respond in <100ms
- Model selection UI must be responsive (<16ms frame time)
- Preference save/load must complete in <50ms

### NFR-2: Reliability
- Graceful degradation if localStorage unavailable (session-only preferences)
- If model registry missing, fall back to allowing any model ID
- API key check must not cause startup delays (lazy evaluation)

### NFR-3: Usability
- First-time users see defaults pre-selected
- Model names must be human-readable, not raw IDs
- Tier badges use consistent color coding (powerful=green, standard=blue, lightweight=gray)

### NFR-4: Extensibility
- Model registry should be easy to update (single file)
- Adding new providers should not require UI changes
- Model tiers should be data-driven, not hardcoded in UI

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Configuration success rate | 100% | Users can select models without errors |
| Chairman synthesis success | 95%+ | No failures due to weak model selection |
| Preference persistence | 100% | Preferences survive browser refresh |
| Time to configure | <30s | From opening settings to starting query |

---

## Out of Scope (v1.0.0)

1. **Dynamic model discovery from APIs** - We use a static registry, not live API queries for available models
2. **Cost estimation** - No pricing display or cost predictions
3. **Model performance benchmarks** - No quality/speed comparisons in UI
4. **Multi-profile support** - Single preference set per browser
5. **Server-side preference persistence** - localStorage only, not synced to backend
6. **Custom model addition** - Users cannot add arbitrary model IDs not in registry
7. **A/B testing of model combinations** - No built-in experimentation framework

---

## Technical Notes

### Integration Points

**Backend Changes**:
1. New endpoint `GET /api/models/available`
2. New module `backend/models_registry.py`
3. Modify `POST /api/query` to accept `councilModels` and `chairmanModel` parameters (optional, defaults to config.py)

**Frontend Changes**:
1. New component `ModelSelector.jsx`
2. New component `SettingsPanel.jsx`
3. Update `App.jsx` to manage model selection state
4. Update `api.js` to pass model parameters to query endpoint

### Migration Path

- Existing users: Auto-load defaults on first visit
- Config.py models remain as fallback defaults
- Environment variable overrides continue to work for server-level defaults

---

## Appendix: Model Registry (Initial Set)

| Model ID | Name | Provider | Tier |
|----------|------|----------|------|
| `openai/gpt-4o` | GPT-4o | OpenAI | powerful |
| `openai/gpt-4o-mini` | GPT-4o Mini | OpenAI | lightweight |
| `openai/o1` | O1 | OpenAI | powerful |
| `openai/o1-mini` | O1 Mini | OpenAI | standard |
| `anthropic/claude-sonnet-4-20250514` | Claude Sonnet 4 | Anthropic | powerful |
| `anthropic/claude-3-5-haiku-latest` | Claude 3.5 Haiku | Anthropic | lightweight |
| `google/gemini-2.5-pro` | Gemini 2.5 Pro | Google | powerful |
| `google/gemini-2.5-flash` | Gemini 2.5 Flash | Google | lightweight |
| `x-ai/grok-2` | Grok 2 | xAI (OpenRouter) | powerful |

---

*End of PRD*
