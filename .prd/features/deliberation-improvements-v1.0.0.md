# LLM Council - Deliberation Improvements PRD

**Version**: 1.0.0
**Created**: 2026-01-02 10:30:00
**Last Updated**: 2026-01-02 10:30:00
**Status**: DRAFT (2026-01-02)
**Supersedes**: N/A
**Related Docs**:
  - `/.archie-data/mock/scenarios/transcription-technical-jtbd-v1.2.1.md`
  - `/CLAUDE.md` (Technical Notes)
  - `/backend/council.py` (Current Implementation)
**Agent**: product-manager

---

## Executive Summary

- **Elevator Pitch**: Transform LLM Council from a single-pass voting system into an iterative deliberation platform that helps technical teams make evidence-based decisions with weighted criteria and refinement loops.

- **Problem Statement**: Technical decision-makers need to evaluate complex multi-criteria choices (API selection, architecture decisions, vendor comparisons) but the current system provides only superficial rankings without structured evaluation, iteration on critiques, or weighted scoring against specific requirements.

- **Target Audience**: Technical leads, architects, and product managers making decisions involving multiple options with competing trade-offs (e.g., choosing a transcription API based on 16 distinct requirements with different priorities).

- **Unique Selling Proposition**: The only AI deliberation platform that combines multi-model reasoning with structured evaluation criteria, iterative refinement based on peer feedback, and transparent evidence-based recommendations.

- **Success Metrics**:
  - Decision confidence: Users rate decisions as "well-supported" 80%+ of the time
  - Criterion coverage: 100% of user-defined criteria addressed in final recommendation
  - Iteration effectiveness: 70%+ of refined answers show measurable improvement
  - Time-to-decision: Complex technical decisions in <15 minutes vs. hours of manual research

---

## Problem Analysis

### What Specific Problem Are We Solving?

**Current State**: LLM Council collects independent answers, has models rank each other anonymously, then synthesizes a final answer. This works for simple questions but fails for:

1. **Complex multi-criteria decisions**: No structured way to evaluate options against specific weighted criteria
2. **Deep technical analysis**: Models provide surface-level answers without probing edge cases
3. **Iterative refinement**: Models cannot improve their answers based on peer critiques
4. **Evidence-based recommendations**: No mechanism for citations, benchmarks, or supporting data

**Example**: User needs to choose a transcription API based on 16 Jobs-To-Be-Done with varying importance (ODI scores from 4-17). Current system would give generic "this API is good because..." without systematic evaluation against each criterion.

### Who Experiences This Problem Most Acutely?

| Persona | Pain Level | Frequency | Current Workaround |
|---------|------------|-----------|-------------------|
| Technical Architects | High | Weekly | Manual multi-LLM queries, spreadsheet comparisons |
| Product Managers | High | Weekly | Separate research + stakeholder discussions |
| Senior Engineers | Medium | Monthly | Rely on personal experience + limited research |
| Procurement Teams | High | Quarterly | RFP processes + vendor demos |

### What's the Cost of Not Solving It?

- **Time**: 4-8 hours per complex decision vs. potential 15 minutes
- **Quality**: Decisions based on incomplete analysis, missed edge cases
- **Confidence**: Low confidence leads to delayed decisions or revisiting choices
- **Documentation**: No audit trail of reasoning for future reference

---

## User Personas

### Persona 1: Technical Architect (Primary)

**Name**: Sarah, Senior Platform Architect

**Demographics**:
- Age: 35-45
- Role: Staff/Principal Engineer or Technical Lead
- Tech-savvy: High
- Company size: Series B+ startup or mid-size enterprise

**Jobs-to-be-Done**:
- Primary: Make defensible technology decisions that balance constraints (cost, performance, compliance, maintainability)
- Secondary: Document decision rationale for team alignment
- Social: Be seen as thorough and evidence-based
- Emotional: Feel confident in recommendations to leadership

**Current Solutions**:
- Tools: ChatGPT, Claude, Perplexity, manual research
- Workarounds: Query multiple LLMs separately, create comparison spreadsheets
- Satisfaction: 5/10 - "I get decent starting points but spend hours synthesizing"

**Pain Points**:
- Severity: High - "Each tool gives different answers, hard to reconcile"
- Frequency: Weekly
- Quote: "I wish I could have the models debate each other and refine their thinking based on counterarguments"

### Persona 2: Product Manager (Secondary)

**Name**: Marcus, Senior Product Manager

**Demographics**:
- Age: 28-38
- Role: Product Manager / Product Lead
- Tech-savvy: Medium-High
- Company size: Any

**Jobs-to-be-Done**:
- Primary: Evaluate build-vs-buy decisions and vendor selections
- Secondary: Create PRDs with justified technology choices
- Social: Be the voice of user needs in technical discussions
- Emotional: Bridge engineering and business perspectives confidently

**Current Solutions**:
- Tools: LLM assistants, G2 reviews, vendor docs
- Workarounds: Schedule multiple stakeholder meetings
- Satisfaction: 4/10 - "I get overwhelmed by technical details without guidance on trade-offs"

**Pain Points**:
- Severity: High - "I need weighted criteria analysis, not just pros/cons lists"
- Frequency: Bi-weekly
- Quote: "I want to input my requirements with priorities and get a recommendation that accounts for all of them"

---

## Feature Specifications

### F1: Structured Evaluation Criteria

#### Core Job Story
When **I'm making a technical decision with multiple competing options**
I want to **define specific evaluation criteria with importance weights**
So I can **get systematic analysis against each criterion, not generic comparisons**

#### User Story
As a **technical decision-maker**, I want to **input my evaluation criteria with priority scores (P0/P1/P2 or 1-10 weights)**, so that **the council evaluates each option against every criterion and produces a weighted recommendation**.

#### Acceptance Criteria
- Given **a user has defined 3+ criteria with weights**, when **the council deliberates**, then **each Stage 1 response must address every criterion explicitly**
- Given **criteria include "Table Stakes" (must-haves)**, when **an option fails a Table Stake**, then **it is flagged as disqualified regardless of other scores**
- Given **a completed deliberation**, when **viewing results**, then **a scoring matrix shows each option's score per criterion**
- Edge case: **User provides conflicting criteria** - system prompts for clarification
- Performance: **Criteria parsing** must complete in **<2 seconds**

#### Forces Analysis
- **Push** (away from current): Generic answers don't address specific requirements
- **Pull** (toward new): Structured analysis saves hours of manual synthesis
- **Anxiety** (resistance): "Will the AI understand my domain-specific criteria?"
- **Habit** (inertia): Used to free-form queries, adding structure feels like overhead

#### ODI Score: 16/20
- Importance: 9/10 (critical for complex decisions)
- Satisfaction: 2/10 (no existing tool does this well)
- Priority: P0 - Core differentiator

#### Dependencies
- Technical: JSON schema for criteria definition, prompt engineering for criterion-aware prompts
- Business: None
- External: None

#### Technical Constraints
- Platform: Web (desktop-first, responsive)
- Performance: Criteria input should not add >5s to total deliberation time
- Security: Criteria may contain confidential business requirements

#### UX Considerations
- Information Architecture: Criteria panel before query submission
- Interaction Patterns: Drag-to-reorder priorities, quick-add presets for common criteria types
- Accessibility: Full keyboard navigation, screen reader labels for weights

---

### F2: Iterative Refinement Loop (Stage 2.5)

#### Core Job Story
When **I see the initial responses from the council**
I want to **have models refine their answers based on peer critiques**
So I can **get deeper analysis that addresses counterarguments and edge cases**

#### User Story
As a **user seeking thorough analysis**, I want **models to see critiques of their answers and provide refined responses**, so that **I benefit from the adversarial improvement process**.

#### Acceptance Criteria
- Given **Stage 2 rankings contain critiques**, when **iteration is enabled**, then **Stage 2.5 shows each model's refined answer incorporating feedback**
- Given **a model's answer was critiqued for missing X**, when **it refines**, then **X is explicitly addressed in the refined answer**
- Given **configurable iteration depth**, when **set to N rounds**, then **the system performs N refinement cycles before synthesis**
- Edge case: **Model refuses to change position** - document "no revision, position maintained with justification"
- Performance: **Each iteration round** must complete in **<90 seconds**

#### Forces Analysis
- **Push**: Single-pass answers miss edge cases, critics raise valid points that go unaddressed
- **Pull**: Refined answers are demonstrably more thorough and nuanced
- **Anxiety**: "Will iteration just add time without improving quality?"
- **Habit**: Expect immediate answers, not deliberative process

#### ODI Score: 15/20
- Importance: 9/10 (key to better outcomes)
- Satisfaction: 1/10 (no existing system offers this)
- Priority: P0 - Core innovation

#### Dependencies
- Technical: Extended prompt context management, state preservation across iterations
- Business: Increased API costs per query (~2x per iteration round)
- External: Model context window limits

#### Technical Constraints
- Platform: Must handle long conversation contexts (potentially 50k+ tokens)
- Performance: Progress indication for multi-round iterations
- Security: Conversation state must not leak between users

#### UX Considerations
- Information Architecture: Collapsible "Iteration History" showing evolution of each answer
- Interaction Patterns: "Iterate" button after Stage 2, configurable auto-iteration
- Accessibility: Clear indication of current iteration round

---

### F3: Evidence Citations and Benchmarks

#### Core Job Story
When **I receive a recommendation from the council**
I want to **see supporting evidence, benchmarks, and citations**
So I can **verify claims and build confidence in the recommendation**

#### User Story
As a **decision-maker who needs to justify choices**, I want **responses to include citations and benchmark data**, so that **I can validate claims and share evidence with stakeholders**.

#### Acceptance Criteria
- Given **a claim about performance**, when **displayed**, then **it includes a source or "unverified - based on model training data" label**
- Given **the prompt requests benchmarks**, when **models respond**, then **they include quantitative comparisons where available**
- Given **a citation is provided**, when **clicked**, then **it either links to source or displays inline reference**
- Edge case: **Conflicting benchmarks from different models** - highlight discrepancy for user review
- Performance: **Citation rendering** must not add **>500ms latency**

#### Forces Analysis
- **Push**: Generic claims without evidence erode trust
- **Pull**: Evidence-based recommendations increase stakeholder buy-in
- **Anxiety**: "What if citations are hallucinated?"
- **Habit**: Accept LLM outputs at face value

#### ODI Score: 14/20
- Importance: 8/10 (essential for professional decisions)
- Satisfaction: 2/10 (LLMs often make unsourced claims)
- Priority: P1 - Important but secondary to core flow

#### Dependencies
- Technical: Citation extraction from model outputs, verification layer (optional)
- Business: May require search/RAG integration for live data
- External: Web search API for citation verification (optional enhancement)

#### Technical Constraints
- Platform: Rich text rendering for inline citations
- Performance: Optional async citation verification
- Security: External link safety (open in new tab, warn on external)

#### UX Considerations
- Information Architecture: Citations as footnotes or inline expandable
- Interaction Patterns: Hover to preview citation, click to expand
- Accessibility: Citations announced to screen readers

---

### F4: Decision Mode Templates

#### Core Job Story
When **I start a technical evaluation**
I want to **select from pre-configured decision templates**
So I can **quickly set up appropriate criteria and evaluation structure for common decision types**

#### User Story
As a **user making a common decision type** (API selection, vendor comparison, architecture choice), I want **pre-built templates with relevant criteria**, so that **I don't start from scratch every time**.

#### Acceptance Criteria
- Given **template library available**, when **user selects "API Selection"**, then **criteria like "Pricing", "Performance", "Documentation", "Support" are pre-populated**
- Given **a template is applied**, when **user reviews criteria**, then **they can customize/add/remove criteria before submission**
- Given **custom criteria created**, when **user saves as template**, then **it becomes available for future use**
- Edge case: **Template doesn't fit use case** - allow full custom mode
- Performance: **Template loading** must complete in **<500ms**

#### Forces Analysis
- **Push**: Starting from blank criteria is time-consuming
- **Pull**: Templates encode best practices for decision types
- **Anxiety**: "Will templates limit my flexibility?"
- **Habit**: Type free-form questions without structure

#### ODI Score: 12/20
- Importance: 7/10 (convenience, not critical)
- Satisfaction: 3/10 (some templates exist in other tools)
- Priority: P1 - Enhances adoption and UX

#### Dependencies
- Technical: Template storage, versioning
- Business: Initial template library creation
- External: None

#### Technical Constraints
- Platform: JSON-based template format for easy sharing
- Performance: Templates should load instantly from cache
- Security: User templates are private by default

#### UX Considerations
- Information Architecture: Template selector as first step of new deliberation
- Interaction Patterns: "Quick start" vs "Custom criteria" paths
- Accessibility: Template preview before selection

---

### F5: Aggregate Scoring Matrix

#### Core Job Story
When **the council completes deliberation**
I want to **see a visual scoring matrix of options vs. criteria**
So I can **quickly understand trade-offs and identify the best fit for my priorities**

#### User Story
As a **decision-maker reviewing results**, I want **a scoring matrix showing each option's rating per criterion**, so that **I can see exactly where options excel or fall short**.

#### Acceptance Criteria
- Given **deliberation with 3+ options and 5+ criteria**, when **completed**, then **scoring matrix displays with color-coded cells (green/yellow/red)**
- Given **criteria have weights**, when **viewing matrix**, then **weighted total score is calculated and shown**
- Given **a cell in the matrix**, when **clicked**, then **relevant excerpt from model analysis is displayed**
- Edge case: **Insufficient data to score a criterion** - display "N/A" with explanation
- Performance: **Matrix rendering** must complete in **<1 second**

#### Forces Analysis
- **Push**: Wall of text is hard to scan for comparisons
- **Pull**: Visual matrix enables rapid trade-off analysis
- **Anxiety**: "How reliable are the scores?"
- **Habit**: Read full responses rather than summary views

#### ODI Score: 13/20
- Importance: 8/10 (transforms usability)
- Satisfaction: 3/10 (some tools have basic comparisons)
- Priority: P1 - High-impact UX improvement

#### Dependencies
- Technical: Score extraction from model outputs, matrix UI component
- Business: Define scoring methodology (1-5, 1-10, qualitative)
- External: None

#### Technical Constraints
- Platform: Responsive table design, mobile-friendly alternative view
- Performance: Real-time filtering/sorting
- Security: None specific

#### UX Considerations
- Information Architecture: Matrix as primary view of Stage 3, with drill-down capability
- Interaction Patterns: Column sort, row highlight on hover, filter by score threshold
- Accessibility: Data table semantics, high-contrast color scheme

---

### F6: Disqualification Logic for Table Stakes

#### Core Job Story
When **I define must-have requirements (Table Stakes)**
I want to **options that fail them to be automatically disqualified**
So I can **focus analysis on viable options only**

#### User Story
As a **decision-maker with non-negotiable requirements**, I want **options that don't meet Table Stakes to be flagged and excluded from weighted scoring**, so that **I don't waste time analyzing unsuitable options**.

#### Acceptance Criteria
- Given **Table Stake criteria defined**, when **an option fails one**, then **it is marked "DISQUALIFIED" with reason**
- Given **disqualified options**, when **viewing matrix**, then **they appear greyed out below viable options**
- Given **all options fail a Table Stake**, when **viewing results**, then **system alerts user to reconsider criteria or options**
- Edge case: **Partial compliance with Table Stake** - prompt for manual override or clarification
- Performance: **Disqualification check** must complete in **<1 second**

#### Forces Analysis
- **Push**: Time wasted analyzing options that don't meet basic requirements
- **Pull**: Clear pass/fail for must-haves focuses analysis on viable candidates
- **Anxiety**: "What if the AI incorrectly disqualifies a good option?"
- **Habit**: Review all options regardless of fit

#### ODI Score: 11/20
- Importance: 7/10 (important for efficiency)
- Satisfaction: 4/10 (manual process works, just slow)
- Priority: P1 - Logical extension of F1

#### Dependencies
- Technical: Boolean/threshold evaluation for Table Stakes
- Business: Clear definition of pass/fail vs. scored criteria
- External: None

#### Technical Constraints
- Platform: Clear visual distinction for disqualified options
- Performance: Real-time disqualification during deliberation display
- Security: None specific

#### UX Considerations
- Information Architecture: Separate "Disqualified" section in results
- Interaction Patterns: Click to see disqualification reason, option to override
- Accessibility: Semantic indication of disqualified status

---

### F7: Confidence Scores and Uncertainty Indicators

#### Core Job Story
When **I see a recommendation score**
I want to **understand how confident the council is in that assessment**
So I can **know where to dig deeper or accept the analysis as-is**

#### User Story
As a **user interpreting council output**, I want **confidence scores showing agreement/disagreement among models**, so that **I can identify areas of consensus vs. uncertainty**.

#### Acceptance Criteria
- Given **models provide scores for a criterion**, when **displayed**, then **consensus indicator shows (high/medium/low agreement)**
- Given **low confidence on a criterion**, when **viewing**, then **divergent opinions are summarized**
- Given **overall recommendation**, when **displayed**, then **aggregate confidence based on model agreement is shown**
- Edge case: **Tie between options** - explicitly state tie and contributing factors
- Performance: **Confidence calculation** must complete in **<500ms**

#### Forces Analysis
- **Push**: Blind trust in AI scores without understanding certainty
- **Pull**: Knowing where models agree/disagree builds appropriate trust
- **Anxiety**: "Will this just add noise to the output?"
- **Habit**: Take scores at face value

#### ODI Score: 10/20
- Importance: 6/10 (nice-to-have for sophistication)
- Satisfaction: 4/10 (some awareness of model disagreement in current Stage 2)
- Priority: P2 - Enhancement after core features

#### Dependencies
- Technical: Statistical analysis of cross-model scores
- Business: None
- External: None

#### Technical Constraints
- Platform: Subtle UI indicators (icons, colors)
- Performance: Calculated during existing aggregation
- Security: None specific

#### UX Considerations
- Information Architecture: Inline confidence indicators, optional detail expansion
- Interaction Patterns: Toggle confidence overlay
- Accessibility: Text alternative for visual confidence indicators

---

### F8: Decision Export and Audit Trail

#### Core Job Story
When **I've completed a deliberation**
I want to **export the full analysis with reasoning trail**
So I can **share with stakeholders, document decisions, and reference later**

#### User Story
As a **professional making accountable decisions**, I want **to export deliberation results as a formatted document**, so that **I can share analysis with my team and maintain decision records**.

#### Acceptance Criteria
- Given **completed deliberation**, when **export requested**, then **PDF/Markdown generated with: question, criteria, options, scoring matrix, key insights, final recommendation**
- Given **iteration enabled**, when **exporting**, then **evolution of answers is documented**
- Given **export format selected**, when **generating**, then **format is appropriate (PDF for sharing, Markdown for documentation, JSON for data)**
- Edge case: **Very long deliberation** - pagination and table of contents
- Performance: **Export generation** must complete in **<10 seconds**

#### Forces Analysis
- **Push**: Screenshots and copy-paste are unprofessional, lose context
- **Pull**: Professional exports enable stakeholder alignment
- **Anxiety**: "Will the export include everything I need?"
- **Habit**: Copy-paste into docs manually

#### ODI Score: 11/20
- Importance: 7/10 (essential for professional use)
- Satisfaction: 3/10 (basic chat export exists)
- Priority: P1 - Required for enterprise adoption

#### Dependencies
- Technical: PDF generation library, Markdown formatter
- Business: Branded export templates
- External: None

#### Technical Constraints
- Platform: Server-side generation for PDF, client-side for Markdown
- Performance: Progress indicator for large exports
- Security: Exports contain only user's data

#### UX Considerations
- Information Architecture: Export button in results view
- Interaction Patterns: Format selector, preview before download
- Accessibility: Export contains accessible document structure

---

## Requirements Summary

### Functional Requirements

```yaml
functional_requirements:
  user_flows:
    - flow_name: "Structured Technical Decision"
      steps:
        - action: "User selects decision template or creates custom criteria"
          system_response: "Display criteria editor with weights"
          decision_points: ["Template", "Custom", "Hybrid"]
        - action: "User inputs question and options to evaluate"
          system_response: "Validate inputs, show preview"
        - action: "User initiates deliberation"
          system_response: "Run Stage 1 with criterion-aware prompts"
        - action: "System displays Stage 1 results"
          system_response: "Show responses organized by criterion coverage"
        - action: "User enables iteration (optional)"
          system_response: "Run Stage 2.5 refinement loop"
        - action: "System completes deliberation"
          system_response: "Display scoring matrix, recommendation, confidence"
        - action: "User exports results"
          system_response: "Generate formatted document"

  state_management:
    - states: ["criteria_input", "deliberating_stage1", "deliberating_stage2", "iterating", "synthesizing", "complete", "exporting", "error"]
    - transitions: "Linear with optional iteration loops"

  data_validation:
    - field: "criteria"
      rules: ["minimum 1 criterion", "weights sum validation", "unique names"]
      error_messages: "Please add at least one evaluation criterion"
    - field: "options"
      rules: ["minimum 2 options for comparison"]
      error_messages: "Please provide at least 2 options to compare"

  integration_points:
    - api: "OpenRouter"
      purpose: "Multi-model querying"
      fallback: "Graceful degradation if models fail"
```

### Non-Functional Requirements

```yaml
non_functional_requirements:
  performance:
    - stage1_completion: "<60 seconds for 4 models"
    - iteration_round: "<90 seconds"
    - total_deliberation: "<5 minutes (2 iteration rounds)"
    - ui_response: "<200ms for interactions"

  scalability:
    - concurrent_deliberations: "100 simultaneous"
    - criteria_limit: "20 per deliberation"
    - options_limit: "10 per deliberation"

  security:
    - authentication: "Required for saving deliberations"
    - data_isolation: "User data never shared between accounts"
    - api_keys: "Server-side only, never exposed to client"

  accessibility:
    - standard: "WCAG 2.1 AA"
    - keyboard: "Full keyboard navigation"
    - screen_readers: "Semantic HTML, ARIA labels"
```

---

## Prioritized Backlog

### P0 - MVP (Core Differentiators)

| Feature | Description | ODI | Effort | Value |
|---------|-------------|-----|--------|-------|
| F1 | Structured Evaluation Criteria | 16 | M | Critical - enables all other features |
| F2 | Iterative Refinement Loop | 15 | L | Critical - key innovation |

**Rationale**: These two features transform the system from a simple voting tool into a structured deliberation platform. Without F1, users can't define what matters. Without F2, responses remain shallow.

### P1 - Core Experience

| Feature | Description | ODI | Effort | Value |
|---------|-------------|-----|--------|-------|
| F5 | Aggregate Scoring Matrix | 13 | M | High - transforms output usability |
| F4 | Decision Mode Templates | 12 | S | High - accelerates adoption |
| F8 | Decision Export | 11 | M | High - required for professional use |
| F6 | Table Stakes Disqualification | 11 | S | Medium - efficiency gain |

**Rationale**: F5 makes results actionable. F4 reduces friction. F8 enables enterprise use. F6 prevents wasted analysis.

### P2 - Enhancement

| Feature | Description | ODI | Effort | Value |
|---------|-------------|-----|--------|-------|
| F3 | Evidence Citations | 14 | L | Medium - builds trust but complex |
| F7 | Confidence Scores | 10 | S | Low - nice-to-have sophistication |

**Rationale**: F3 is valuable but requires significant work (RAG, verification). F7 adds polish but core flow works without it.

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- F1: Criteria input UI and schema
- Backend: Criterion-aware prompt generation
- Backend: Score extraction from model outputs

### Phase 2: Core Innovation (Weeks 3-4)
- F2: Iteration loop (Stage 2.5)
- Backend: Context management for multi-round
- UI: Iteration history display

### Phase 3: Visualization (Weeks 5-6)
- F5: Scoring matrix component
- F6: Table Stakes logic
- UI: Comparison and drill-down views

### Phase 4: Polish (Weeks 7-8)
- F4: Template library
- F8: Export functionality
- UX refinements based on testing

### Phase 5: Enhancement (Post-MVP)
- F3: Citation extraction and verification
- F7: Confidence scoring
- Performance optimization

---

## Success Criteria

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User decision confidence | 80%+ rate "well-supported" | Post-deliberation survey |
| Criterion coverage | 100% criteria addressed | Automated content analysis |
| Iteration improvement | 70%+ show measurable improvement | Before/after comparison |
| Time-to-decision | <15 min for complex decisions | Session timing |
| Export utilization | 40%+ deliberations exported | Usage analytics |

### Qualitative Indicators

- Users report reduced need for follow-up research
- Stakeholder meetings reference council exports
- Return usage for similar decision types
- Organic recommendations to colleagues

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Increased API costs | High | Medium | Iteration is optional, smart token management |
| Context window limits | Medium | High | Chunking strategy, model selection |
| Criteria misinterpretation | Medium | Medium | Validation UI, examples in prompts |
| Export quality variance | Low | Medium | Structured templates, human review option |
| Adoption friction | Medium | Medium | Progressive disclosure, templates for quick start |

---

## Appendix: Technical Decision Use Case Analysis

Based on the transcription API JTBD document (16 jobs, ODI 4-17), here's how the improved council would handle such a decision:

### Current System Limitations

1. **No criterion input**: User types "Which transcription API should I use?" - gets generic comparison
2. **No weighting**: J4 (Sovereignty, ODI 17) weighted equally with J6 (Formats, ODI 4)
3. **No Table Stakes logic**: Option failing J5 (Quality) not disqualified
4. **No iteration**: Surface analysis of each API without depth
5. **No structured output**: Wall of text, not actionable matrix

### Improved System Flow

1. **Criteria Input** (F1):
   - User imports JTBD list or selects "API Selection" template
   - Assigns weights: J4=17, J14=13, J10=12... J6=4
   - Marks J5, J1, J2, J3, J6, J7 as "Table Stakes"

2. **Stage 1** (Enhanced):
   - Prompt includes: "Evaluate each option against these 16 criteria..."
   - Each model provides structured assessment per criterion

3. **Stage 2** (Unchanged):
   - Anonymous ranking continues as-is for overall quality

4. **Stage 2.5** (F2):
   - Model A critiqued for missing J14 (Accents) analysis
   - Model A refines: "Regarding Quebec French accent support..."
   - 1-2 iteration rounds based on critique quality

5. **Stage 3** (Enhanced):
   - Chairman receives structured inputs
   - Produces scoring matrix + recommendation
   - Disqualifies options failing Table Stakes

6. **Output** (F5, F8):
   - Visual matrix: Options vs. Criteria with color-coded scores
   - "Whisper self-hosted: RECOMMENDED (Score: 142/170)"
   - Exportable PDF for architecture review meeting

---

## Changelog

### v1.0.0 (2026-01-02)
- Initial PRD creation
- 8 features defined with full specifications
- Prioritized backlog established
- Implementation roadmap drafted
- Technical use case analysis included
