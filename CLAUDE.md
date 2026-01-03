# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Install Dependencies
```bash
# Backend (from project root)
uv sync

# Frontend
cd frontend && npm install
```

### Run the Application
```bash
# Option 1: Both servers via start script
./start.sh

# Option 2: Run manually in separate terminals
# Terminal 1 - Backend:
uv run python -m backend.main

# Terminal 2 - Frontend:
cd frontend && npm run dev
```

### Lint
```bash
cd frontend && npm run lint
```

### Build Frontend
```bash
cd frontend && npm run build
```

## Ports
- Backend: **8001** (not 8000)
- Frontend: 5173 (Vite default)

## Architecture Overview

LLM Council is a 3-stage deliberation system where multiple LLMs collaboratively answer user questions through anonymized peer review.

### Data Flow
```
User Query
    ↓
Stage 1: Parallel queries to council models → [individual responses]
    ↓
Stage 2: Anonymize as "Response A, B, C..." → Parallel ranking queries → [evaluations + parsed rankings]
    ↓
Stage 3: Chairman synthesizes from all responses + rankings
    ↓
Return: {stage1, stage2, stage3, metadata}
```

### Backend (`backend/`)

| File | Purpose |
|------|---------|
| `config.py` | `COUNCIL_MODELS` list and `CHAIRMAN_MODEL` - uses `OPENROUTER_API_KEY` from `.env` |
| `openrouter.py` | Async model queries via OpenRouter API with graceful degradation |
| `council.py` | Core 3-stage logic: collect responses, anonymized rankings, synthesis |
| `storage.py` | JSON-based conversation persistence in `data/conversations/` |
| `main.py` | FastAPI app with CORS for localhost:5173 and localhost:3000 |

**Key function in `council.py`:**
- `stage2_collect_rankings()` returns `(rankings_list, label_to_model_dict)` - the mapping is used for client-side de-anonymization

### Frontend (`frontend/src/`)

- `App.jsx` - Main orchestration, manages conversations and metadata (metadata is NOT persisted to backend)
- `api.js` - API client targeting backend port 8001
- `components/Stage1.jsx` - Tab view of individual model responses
- `components/Stage2.jsx` - Shows raw evaluations with client-side de-anonymization, extracted rankings, and aggregate scores
- `components/Stage3.jsx` - Final synthesized answer (green background)

## Key Design Decisions

### Stage 2 Anonymization
Models receive "Response A", "Response B", etc. - never model names. Backend creates mapping for frontend to display model names in bold. This prevents bias while maintaining transparency.

### Stage 2 Prompt Format
Strict format ensures parseable output:
1. Evaluate each response individually
2. "FINAL RANKING:" header required
3. Numbered list: "1. Response C", "2. Response A"
4. No text after ranking section

`parse_ranking_from_text()` extracts this; fallback regex catches any "Response X" patterns.

### Error Handling
Graceful degradation - continues with successful responses if some models fail. Never fails entire request due to single model failure.

## Important Implementation Details

### Relative Imports (Critical)
All backend modules use relative imports (`from .config import ...`). Must run as `python -m backend.main` from project root, not from backend directory.

### Markdown Rendering
All ReactMarkdown components must wrap in `<div className="markdown-content">` for spacing. Class defined in `index.css`.

### Metadata Ephemeral
`label_to_model` and `aggregate_rankings` are returned via API but NOT persisted to storage JSON.

## Common Gotchas

1. **Module Import Errors**: Run backend as `python -m backend.main` from project root
2. **CORS Issues**: Frontend origin must match allowed origins in `main.py`
3. **Port Conflicts**: Backend uses 8001, not 8000 - update `backend/main.py` AND `frontend/src/api.js` if changing
