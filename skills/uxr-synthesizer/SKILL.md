---
name: uxr-synthesizer
description: Synthesize insights across multiple UX research participants into cross-session themes organized by hypothesis bucket. Use after insight extraction is complete for 2+ participants. Triggers on "synthesize across participants," "find patterns across sessions," "what themes emerged," "combine findings," or requests to aggregate insights from multiple interviews.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_submit_synthesis
  - hogwild-uxr_get_project_status
  - hogwild-uxr_load_config
---

# Cross-Participant Synthesizer

Takes per-participant finalized insight files and produces a structured cross-session synthesis: themes nested within hypothesis buckets, with participant counts and per-participant evidence anchors.

## Workflow

1. Call `load_config` to get research question, hypotheses, and participant manifest (including `tags` and `cohorts` fields)
2. Call `get_project_status` to confirm 2+ participants are finalized
3. Determine scope from the researcher's request:
   - **All participants** — include everyone
   - **Filter by cohort** — include only participants whose `cohorts` field contains the specified value
   - **Filter by tag** — include only participants whose `tags` field contains the specified value
   - **Compare two groups** — run synthesis for each group separately, then produce a cross-group delta section; if more than 2 groups are requested, surface the ambiguity and ask the researcher to clarify before proceeding
4. Call `get_insights` for each participant in scope
5. Perform synthesis reasoning (below)
6. Call `submit_synthesis` with the structured synthesis JSON

## Synthesis procedure

### Step 1 — Aggregate
Collect all per-participant insights. Only include insights with status `pass` or `flag` — exclude `insufficient_evidence` and `withdrawn`.

### Step 2 — Group into themes
Group conceptually similar findings into themes. Assign each theme to a hypothesis bucket (H1, H2, H3, or Novel).

### Step 3 — Count prevalence
Count how many distinct participants contributed evidence to each theme. A participant counts once per theme regardless of how many insights they contributed.

### Step 4 — Surface tensions
If participants have opposing experiences within a theme, surface as `tensions` — do not merge contradictions into a single view.

## Output schema

```json
{
  "meta": {
    "research_question": "...",
    "total_participants": 5,
    "participants_with_insights": 5,
    "generated_at": "ISO timestamp"
  },
  "hypothesis_buckets": [
    {
      "bucket_id": "H1",
      "hypothesis": "...",
      "themes": [
        {
          "theme_id": "H1-T1",
          "theme_label": "Short descriptive label",
          "theme_summary": "One declarative sentence.",
          "participant_count": 4,
          "total_participants": 5,
          "prevalence": "4 of 5 participants",
          "strength": "strong | moderate | weak",
          "participant_contributions": [
            {
              "participant_id": "P1",
              "insight_ids": ["P1_I001"],
              "supporting_claim": "One-line summary."
            }
          ],
          "tensions": "Optional within-theme contradictions.",
          "analyst_note": "Optional interpretive flag."
        }
      ]
    }
  ],
  "cross_bucket_patterns": []
}
```

### Strength calibration

| Strength | Criteria |
|---|---|
| **strong** | >50% of participants contributed evidence |
| **moderate** | 25–50% contributed |
| **weak** | <25% — present but not widespread |

## Quality rules

- Do not create themes blending different hypothesis buckets without flagging as cross-bucket pattern
- Do not overstate participant count
- Do not invent themes not grounded in per-participant insights
- Do not merge contradictions — surface as tensions
