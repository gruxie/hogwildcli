---
name: uxr-cohort-delta
description: Compare a subset of participants (a new cohort) against an existing synthesis to identify how they confirm, amplify, diverge from, or add novel findings. Use when new participants have been added and you want their specific contribution without re-doing full synthesis. Produces an addendum, not a replacement.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_synthesis
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
---

# Cohort Delta

Produces a structured comparison of a specified participant subset against the full synthesis. Designed for ad hoc group analysis — e.g., how a second wave of participants relates to themes established by the first wave.

## Design intent

- **Addendum only:** synthesis is the primary document; this is supplementary
- **Ad hoc grouping:** any set of participant IDs can be the cohort
- **No re-synthesis:** reads existing insight files + synthesis — no new extraction

## Workflow

1. Call `load_config` to get participant aliases and cohort IDs
2. Call `get_synthesis` for established themes
3. Call `get_insights` for each cohort participant
4. Classify each cohort insight against existing themes
5. Call `save_artifact` with `cohort_delta_{ids}.md` and type `cohort-delta`

## Classification categories

| Category | Meaning |
|---|---|
| **Confirms** | New participant adds a data point to an established theme |
| **Amplifies** | Adds new texture or nuance without contradicting |
| **Diverges** | Contradicts or complicates an established theme |
| **Novel** | No mapping to any existing theme |

## Output structure

1. Header: cohort IDs and aliases, date, total insights analyzed
2. Alignment summary table: theme label | category | new participant(s)
3. Per-category sections (Confirms / Amplifies / Diverges / Novel)
4. Implications: how the cohort's addition changes or reinforces the synthesis

## When to use

- A second wave of participants has been processed
- Comparing a demographic subgroup against the whole
- Assessing whether new data changes the synthesis picture
