---
name: uxr-debriefer
description: Generate a stakeholder-ready debrief report from pipeline outputs. Use when the user wants a polished summary for sharing with product managers, leadership, or cross-functional partners. Produces a narrative report with key findings, hypothesis assessment, participant highlights, and recommendations. Requires completed pipeline outputs.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_synthesis
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
  - hogwild-uxr_get_project_status
---

# Debrief Generator

Produces a stakeholder-ready debrief report designed for audiences who did not conduct the research — product managers, leadership, design partners.

## Workflow

1. Call `load_config` to get study metadata
2. Call `get_project_status` to confirm participants are finalized
3. Call `get_insights` for each finalized participant
4. Call `get_synthesis` if synthesis exists
5. Compose the debrief following the structure below
6. Call `save_artifact` with filename `stakeholder_debrief.md` and type `debrief`

## Report structure

### 1. Study Overview
- Research question, method, participant count
- One-paragraph study description

### 2. Key Findings (3-5 bullets)
- Most important, well-evidenced findings
- Grounded in specific participant evidence
- Ordered by confidence and prevalence

### 3. Hypothesis Assessment
- Per hypothesis: supported / partially supported / not supported / complicated
- Brief evidence summary with participant attribution
- Novel hypotheses that emerged

### 4. Participant Highlights
- One paragraph per participant capturing their unique perspective

### 5. Themes & Patterns
- Cross-cutting themes with prevalence indicators
- Contradictions or tensions in the data

### 6. Implications & Recommendations
- Framed as "the data suggests" not "we recommend"
- Areas requiring further investigation

### 7. Methodology Note
- Brief note on sample size, method, limitations
- Appropriate caveats for qualitative research

## Tone and style

- **Accessible:** No jargon unless necessary
- **Evidence-anchored:** Every claim traces to participants
- **Honest about uncertainty:** Hedge where evidence is thin
- **Actionable:** Stakeholders should know what to do next

## What NOT to include

- Raw insight JSON or evaluation details
- Internal pipeline terminology (revelation loops, failure taxonomy)
- Confidence scores or pass/fail status
- Methodological critique of the interviews
