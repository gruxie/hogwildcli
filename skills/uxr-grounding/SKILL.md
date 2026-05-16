---
name: uxr-grounding
description: Run grounding analysis (Mode 0) to build or update the focus memo and grounding artifacts for a research project. Use before running participant analysis on a new project, or to refresh grounding after adding new transcripts or memos. Triggers on "run grounding," "build grounding," "bootstrap grounding," "set up grounding," "generate focus memo," "ground this project," or "initialize grounding."
allowed-tools:
  - hogwild-uxr_load_config
  - hogwild-uxr_get_grounding_artifact
  - hogwild-uxr_save_grounding_artifact
  - hogwild-uxr_list_grounding_artifacts
  - hogwild-uxr_get_artifact
  - hogwild-uxr_get_project_status
---

# Grounding Analyst (Mode 0)

Builds or updates the grounding artifacts that shape all subsequent participant analysis. This skill runs before extraction — its outputs are read by `uxr-extractor` and `uxr-controller` to orient analysis toward what matters for this study.

## When to run

- **First time:** automatically suggested by `uxr-controller` before the first participant analysis
- **Re-run:** any time the researcher wants to refresh grounding (new memos added, more participants available, focus has shifted)

## Workflow

### Step 1 — Check prior grounding
1. Call `list_grounding_artifacts` to check if `./grounding/` exists and what's already there
2. Call `get_grounding_artifact` for `grounding_log.json` if it exists — report when grounding was last run and which participants were used
3. If re-running, confirm with the researcher before proceeding

### Step 2 — Load study context
1. Call `load_config` to read:
   - `study.motivations`, `study.goals`, `study.intended_impacts`
   - `research.question`, `research.hypotheses`
   - `grounding.additional_context` if present
2. Call `get_project_status` to show which participants have preprocessed transcripts available

### Step 3 — Select grounding sources
Ask the researcher which 1–3 participants to use as grounding sources. Recommend preprocessed participants. If not specified, use the first 1–2 available.

Also read `./grounding/memos.md` if it exists — backchannel chat, team notes, and debrief content count as grounding sources.

### Step 4 — Analyze
For each selected participant, call `get_artifact` to load their `{stem}_converted.md` transcript. Read the full transcript but focus on:
- What domain language does the participant use?
- What problems, needs, and outcomes do they describe?
- What solutions excite or concern them?
- What is ambiguous or potentially off-topic?

Cross-reference findings with study.motivations, study.goals, research.question, and hypotheses to score relevance.

### Step 5 — Write focus_memo.md
Call `save_grounding_artifact` with `filename: "focus_memo.md"` and the content below.

**focus_memo.md format:**
```markdown
# Focus Memo
Generated: {date}
Participants used: {P1, P2, ...}

## Domain
{Terms and phrases that best capture the study domain — drawn from participant language}

## Project Summary
{What is this project about at the intersection of the research question, hypotheses, and the sources used?}

## Participant POV
Statements drawn from transcripts. Scored for relevance to the project.
Scores: 0 = extremely relevant | 1 = relevant | 2 = ambiguous | 3 = not relevant | 4 = counterproductive

### Customer
- {Statement about who the participant is and what's relevant for profiling} — Score: {0-4}

### Problem
- {Statement about needs, outcomes, fears, or uncertainties participants express} — Score: {0-4}

### Solution
- {Statement about what participants are satisfied or dissatisfied with} — Score: {0-4}

## Researcher POV
> Edit this section to course-correct AI interpretation. Defaults are NA (system ignores NA entries).

### On-topic
NA

### Interesting
NA

### Off-topic
NA
```

### Step 6 — Update grounding log
Call `save_grounding_artifact` with `filename: "grounding_log.json"`. Load existing log first (if any) and append a new entry — do not overwrite prior entries.

```json
[
  {
    "date": "{ISO date}",
    "participants_used": ["{P1}", "{P2}"],
    "notes": ""
  }
]
```

### Step 7 — Create stubs (first run only)
If `definitions.md`, `sample_analysis.md`, or `memos.md` are not present in `./grounding/`, create them via `save_grounding_artifact` using the starter content from the scaffolded stubs. Skip any that already exist.

## Isolation rule

Grounding analysis must not produce or modify any file in `./output/`. Grounding artifacts live exclusively in `./grounding/`. This isolation ensures grounding does not contaminate participant analysis.

## Progress report

After completing, report:
```
═══════════════════════════════════
 GROUNDING COMPLETE
 Sources: {participants used} {+ memos if used}
 Focus memo: ./grounding/focus_memo.md
 Next: run participant analysis — grounding will be applied automatically
═══════════════════════════════════
```
