# Hogwild UXR — Command Reference

Complete reference for all skills and MCP tools in the Hogwild UXR pipeline.

---

## Table of Contents

1. [Skills](#skills)
2. [MCP Tools](#mcp-tools)
3. [Copilot CLI Commands](#copilot-cli-commands)
4. [State Machine](#state-machine-reference)

---

## Skills

Skills are invoked by natural language. Copilot auto-matches your request to the appropriate skill based on its description.

---

### uxr-controller

**Purpose:** Orchestrate the full pipeline end-to-end.

**Trigger phrases:**
- "Run the full analysis"
- "Analyze these transcripts"
- "Extract and verify insights"
- "Process all participants"

**What it does:**
1. Loads and validates config
2. Preprocesses all transcripts (.docx → .md + .json)
3. Extracts insights per participant
4. Evaluates each insight set (5-check process)
5. Runs revelation loops on failures (up to `max_iterations`)
6. Synthesizes across participants
7. Optionally generates reports

**Prerequisites:** Valid `research_config.yaml` with transcript files in place.

**Example:**
```
Run the full analysis on my research project at C:\projects\ai-study
```

---

### uxr-preprocessor

**Purpose:** Convert .docx transcripts to structured Markdown + JSON.

**Trigger phrases:**
- "Convert this transcript"
- "Preprocess the docx files"
- "Parse the interview recording"

**What it does:**
1. Reads .docx and detects Speaker/Timestamp/Utterance blocks
2. Produces `{stem}_converted.md` (human-readable)
3. Produces `{stem}_turns.json` (machine-readable for evaluator)
4. Reports speaker list and turn count for user confirmation

**Outputs:**

| File | Purpose |
|------|---------|
| `{stem}_converted.md` | Formatted transcript |
| `{stem}_turns.json` | Structured turn data for quote verification |

---

### uxr-extractor

**Purpose:** Extract evidence-grounded insights from preprocessed transcripts.

**Trigger phrases:**
- "Extract insights from P1"
- "What did we learn from this transcript?"
- "What are the key findings?"
- "Analyze this session"

**What it does:**
1. Reads preprocessed transcript
2. Applies extraction rules (grounding, quote-first, frequency accuracy)
3. Produces structured insight JSON with evidence traceability
4. Handles revelation re-runs with targeted corrections

**Output format:** JSON array of insight objects, each with:
- `insight_id`, `claim`, `evidence[]`, `hypothesis_relation`, `confidence`, `confidence_rationale`

**Key rules:**
- Only extract from interviewee turns (never the moderator)
- Quote before you claim (locate evidence first)
- Hypotheses are a lens, not a leash (surface novel findings too)

---

### uxr-evaluator

**Purpose:** Verify insights against source transcript material.

**Trigger phrases:**
- "Check these insights"
- "Verify the findings"
- "Are these insights accurate?"
- "Evaluate the extraction"

**5-check process:**

| Check | Detects |
|-------|---------|
| 1. Quote verification | `quote-distortion` — quote doesn't match `_turns.json` |
| 2. Attribution check | `attribution-bleed` — evidence from moderator or over-generalized |
| 3. Claim-to-evidence | `extrapolation`, `frequency-distortion`, `hypothesis-projection` |
| 4. Moderator contamination | `moderator-contamination` — minimal agreement only |
| 5. Unsupported claims | `unsupported` — no valid evidence exists |

**Output:** Evaluation JSON with per-insight `pass`, `flag`, or `fail` status.

---

### uxr-synthesizer

**Purpose:** Build cross-participant themes organized by hypothesis bucket.

**Trigger phrases:**
- "Synthesize across participants"
- "Find patterns across sessions"
- "What themes emerged?"
- "Combine findings from all interviews"

**Prerequisites:** 2+ participants must be `finalized`.

**Output:** `synthesis.json` with hypothesis buckets → themes → participant contributions.

**Strength ratings:**

| Rating | Criteria |
|--------|----------|
| Strong | >50% of participants contributed evidence |
| Moderate | 25–50% |
| Weak | <25% |

---

### uxr-narrator

**Purpose:** Generate audience-tailored narrative reports with integrity audits.

**Trigger phrases:**
- "Generate a report for PMs"
- "Create an executive narrative"
- "Write a designer-focused report"
- "Produce a slides outline"

**Audiences:**

| Audience | Lead with | Organize around |
|----------|-----------|-----------------|
| `pm` | Prioritization and tradeoffs | Hypotheses as decision gates |
| `designer` | Unmet needs and breakdowns | User moments |
| `engineer` | System implications | Workflows and constraints |
| `executive` | Single key tension | 3–5 findings max |

**Formats:** `report`, `slides`, `memo`, `hybrid`

**Mandatory integrity audit checks:**
- Prevalence inflation
- Confidence laundering
- Anecdote elevation
- Hypothesis suppression
- Causality overreach
- Minority view flattening

**Output:** `narrative_report_{audience}.md` (artifact + integrity review)

---

### uxr-debriefer

**Purpose:** Generate stakeholder-ready debrief reports.

**Trigger phrases:**
- "Create a stakeholder debrief"
- "Summarize for leadership"
- "Write a report for the product team"

**Report structure:**
1. Study overview
2. Key findings (3–5 bullets)
3. Hypothesis assessment
4. Participant highlights
5. Themes & patterns
6. Implications & recommendations
7. Methodology note

**Output:** `stakeholder_debrief.md`

---

### uxr-contradiction

**Purpose:** Detect contradictions within and across participants.

**Trigger phrases:**
- "Find contradictions in the data"
- "What conflicts exist?"
- "Where do participants disagree?"

**Detection levels:**
- **Intra-participant:** Same person says conflicting things at different points
- **Inter-participant:** Different people have opposing views

**Severity:** High (contradicts key finding), medium (complicates), low (minor/contextual)

**Output:** `contradiction_analysis.md`

---

### uxr-ontology

**Purpose:** Generate or apply a structured tagging taxonomy.

**Trigger phrases:**
- "Create a tagging ontology"
- "Generate annotation labels"
- "Build a taxonomy from the data"

**Modes:** Generate (derive from insights) or apply (tag insights with existing ontology)

**Output:** `ontology.json` with domains (4–8) containing tags (3–10 each)

---

### uxr-annotator

**Purpose:** Annotate transcripts with tags, insight refs, and hypothesis markers.

**Trigger phrases:**
- "Annotate the transcript"
- "Mark up for video clipping"
- "Tag the transcript with insights"

**Annotation types:** Insight references (📌), ontology tags (🏷️), hypothesis markers (🎯)

**Output:** `{participant_id}_annotated.md` with video clip timestamp export

---

### uxr-delta

**Purpose:** Track what changed between pipeline runs.

**Trigger phrases:**
- "What changed since last run?"
- "Compare before and after"
- "Show me the diff"

**Categories:** New, removed, modified, confidence shift, status change, hypothesis shift

**Output:** `delta_report.md`

---

### uxr-cohort-delta

**Purpose:** Compare a participant subset against existing synthesis.

**Trigger phrases:**
- "How do P8-P10 differ from the first wave?"
- "Compare the new cohort"
- "What does wave 2 add?"

**Classification:** Confirms, amplifies, diverges, novel

**Output:** `cohort_delta_{ids}.md`

---

### uxr-terminology

**Purpose:** Identify terminology confusion and mismatches.

**Trigger phrases:**
- "Run a terminology audit"
- "Where were users confused by terminology?"
- "Find labeling friction"

**Confusion types:** Confusion (doesn't know term), mismatch (wrong mental model), alternative (uses different word)

**Severity:** High (3+ participants), medium (2), low (1)

**Output:** `terminology_audit.md`

---

### uxr-labeler

**Purpose:** Qualitative coding with a managed dictionary.

**Trigger phrases:**
- "Apply qualitative labels"
- "Build a codebook"
- "Code these insights"

**Confidence tiers:** Direct (explicit match), inferred (contextual), weak (tentative)

**Modes:** Build dictionary, apply labels, merge new labels

---

## MCP Tools

These are called by skills internally. They handle state and I/O only — no reasoning.

### Lifecycle

| Tool | Parameters | Returns |
|------|-----------|---------|
| `detect_speakers` | `docx_path` | Speaker names + turn counts |
| `scaffold_config` | `project_dir`, `title`, `description`, `research_question`, `hypotheses`, `participants` | Config file path |
| `load_config` | `config_path` | Full validated config JSON |
| `preflight_check` | `config_path` | Ready status + issues list |
| `get_project_status` | `config_path` | Per-participant state array |

### Pipeline State

| Tool | Parameters | Returns |
|------|-----------|---------|
| `parse_transcript` | `config_path`, `participant_id` | MD path, turns path, speakers |
| `start_participant` | `config_path`, `participant_id` | State, iteration, max_iterations |
| `submit_insights` | `config_path`, `participant_id`, `insights[]` | Save path + counts |
| `submit_evaluation` | `config_path`, `participant_id`, `evaluation{}` | Next action (revelation/finalized) |
| `get_insights` | `config_path`, `participant_id` | Insights (final or latest iter) |
| `get_revelation_context` | `config_path`, `participant_id` | Failed issues + transcript |
| `reset_participant` | `config_path`, `participant_id` | Reset confirmation |

### Synthesis & Artifacts

| Tool | Parameters | Returns |
|------|-----------|---------|
| `submit_synthesis` | `config_path`, `synthesis{}` | Save confirmation |
| `get_synthesis` | `config_path` | Synthesis JSON |
| `save_artifact` | `config_path`, `filename`, `content`, `artifact_type` | Save path |
| `list_artifacts` | `config_path`, `artifact_type?` | Metadata list |
| `get_artifact` | `config_path`, `filename` | File content |

### Labeling

| Tool | Parameters | Returns |
|------|-----------|---------|
| `manage_dictionary` | `config_path`, `action` (get/set/merge), `labels?` | Dictionary state |
| `apply_labels` | `config_path`, `participant_id`, `labeled_insights[]` | Save confirmation |
| `get_labels` | `config_path`, `participant_id` | Labels array |

---

## Copilot CLI Commands

| Command | Purpose |
|---------|---------|
| `/skills list` | Show all installed skills |
| `/skills info uxr-controller` | Details on a specific skill |
| `/skills reload` | Reload after adding/changing skills |
| `--allow-all-tools` | Launch flag to skip per-tool confirmations |

---

## State Machine Reference

Each participant moves through these states independently:

```
not_started ──→ preprocessed ──→ extracting ──→ evaluating ──→ finalized
                                      ↑              │
                                      │   (fail)     ▼
                                      └──── in_revelation
```

| State | Meaning | Next tool |
|-------|---------|-----------|
| `not_started` | No processing done | `parse_transcript` |
| `preprocessed` | .docx converted successfully | `start_participant` |
| `extracting` | Awaiting insight submission | `submit_insights` |
| `evaluating` | Awaiting evaluation results | `submit_evaluation` |
| `in_revelation` | Failed evaluation, needs re-extraction | `submit_insights` (revised) |
| `finalized` | Complete — insights locked | `reset_participant` (to re-run) |
