---
name: uxr-contradiction
description: Identify contradictions and tensions within and across participant transcripts. Use when the user wants to find conflicting statements, paradoxes, or disagreements in the data. Operates on extracted insights and optionally on raw transcript turns.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_synthesis
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
  - hogwild-uxr_get_project_status
---

# Contradiction Detector

Surfaces contradictions at two levels:
- **Intra-participant:** A single participant says contradictory things at different points
- **Inter-participant:** Different participants have opposing experiences or views

## Workflow

1. Call `load_config` to get study context
2. Call `get_insights` for each participant
3. Optionally call `get_synthesis` for theme-level analysis
4. Analyze insights for contradictions using the framework below
5. Call `save_artifact` with filename `contradiction_analysis.md` and type `analysis`

## Detection framework

### Intra-participant contradictions
For each participant's insight set:
- Compare claims that reference the same topic or concept
- Flag pairs where one claim asserts X and another asserts not-X or a conflicting position
- Check if temporal context explains the difference (e.g., "before" vs "after")

### Inter-participant contradictions
Across all participants:
- Find insights with the same hypothesis_ref but opposing hypothesis_relation
- Find themes where participant contributions conflict
- Surface experiences that diverge from the majority pattern

## Output structure

For each contradiction:
```json
{
  "contradiction_id": "C001",
  "type": "intra | inter",
  "participants": ["P1"] or ["P1", "P3"],
  "side_a": {
    "insight_id": "P1_I003",
    "claim": "...",
    "evidence_summary": "..."
  },
  "side_b": {
    "insight_id": "P1_I008",
    "claim": "...",
    "evidence_summary": "..."
  },
  "interpretation": "Suggested explanation for the contradiction",
  "severity": "high | medium | low",
  "implication": "What this means for the research"
}
```

## Severity calibration

| Severity | Criteria |
|---|---|
| **High** | Directly contradicts a key finding or hypothesis assessment |
| **Medium** | Complicates interpretation but doesn't invalidate findings |
| **Low** | Minor inconsistency, likely contextual |
