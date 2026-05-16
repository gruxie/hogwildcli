---
name: uxr-cdnotes
description: Generate a CD Notes report — a concise, email-ready summary of research findings for wide distribution. Derived from a completed Standard Report. Written in plain, casual language for a broad internal audience. Triggers on "generate CD Notes," "write CD Notes," "create an email summary," "CD Notes report," or "email-ready research summary."
allowed-tools:
  - hogwild-uxr_load_config
  - hogwild-uxr_get_artifact
  - hogwild-uxr_list_artifacts
  - hogwild-uxr_save_artifact
---

# CD Notes Composer

Produces a concise, email-friendly version of the research findings for wide distribution. CD Notes are not a substitute for the full report — they are a communication artifact that leads with what matters and speaks to readers who may not have research context.

## Prerequisites

A completed Standard Report (`{Study Title} Report.md`) must exist in `./output/Summary/`. Run `uxr-narrator` or `uxr-debriefer` first if it doesn't.

## Workflow

### Step 1 — Load source material
1. Call `load_config` to get study title, participant aliases, roles, and companies
2. Call `list_artifacts` to find the Standard Report
3. Call `get_artifact` to load the Standard Report content

### Step 2 — Pre-output evaluation
Before writing, verify traceability:
- Every insight or finding you include must appear in the Standard Report
- Every quote you carry forward must have appeared with its source attribution in the Standard Report
- Do not introduce new claims that are not in the Standard Report

If anything cannot be traced, exclude it rather than generating new content.

### Step 3 — Compose CD Notes
Follow the section guidance below. Tone throughout: conversational, plain language, zero jargon. Write as if sending to a broad internal mailing list where most readers know the product but not the research.

**Sections to include:**

| Section | Guidance |
|---|---|
| Study Title | Same as Standard Report |
| Date | Date CD Notes are generated |
| Introduction | 2–3 sentences max. What was studied and why it matters. No methodology. Lead with the "so what." |
| Key Findings | Plain-language restatement of Standard Report Key Findings. One punchy sentence per finding. Use plain numbers ("4 of 9 participants") not research language ("prevalent across the cohort"). |
| Insights | Most significant insights only — condense ruthlessly. Group under plain-language theme labels, not hypothesis IDs. 1 supporting quote per insight maximum. |
| Recommendations | Same as Standard Report but phrased as clear action statements: "We should consider X" not "The data suggests a potential opportunity to explore X." |
| Participant Summary | Optional. Include only if the audience needs context on who was interviewed. One sentence per participant maximum. |

**Omit from CD Notes:** Report Version, Study Description, Methodology section.

### Step 4 — Quote handling
- Maximum 1 quote per insight (CD Notes are brief — more than 1 becomes a wall of text)
- Same attribution format as all other reports: `"Quote text." — First Name, Role at Company`
- Only carry forward quotes that appeared in the Standard Report — never introduce quotes directly from raw analysis

### Step 5 — Save
Call `save_artifact` with:
- `filename`: `"Summary/{study_title} CD Notes.md"` (use actual study title from config)
- `artifact_type`: `"cd-notes"`

## Tone guardrails

| Avoid | Use instead |
|---|---|
| "The data suggests..." | "We found that..." |
| "Participants exhibited a tendency to..." | "Most participants..." |
| Hypothesis IDs (H1, H2...) | Plain theme labels |
| Research methodology references | Nothing — just findings |
| Hedged recommendations | Direct action language |
