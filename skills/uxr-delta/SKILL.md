---
name: uxr-delta
description: Track changes between pipeline runs to identify what shifted after re-extraction, new transcripts, or config changes. Use when the user re-runs the pipeline and wants to understand what changed. Compares two sets of pipeline outputs.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_synthesis
  - hogwild-uxr_get_artifact
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
---

# Delta Tracker

Compares two pipeline output sets and reports what changed.

## Workflow

1. Call `load_config` for current project
2. Call `get_insights` for current results
3. Load previous results (user provides path or previous run is archived)
4. Compute deltas using the framework below
5. Call `save_artifact` with `delta_report.md` and type `delta`

## Delta categories

| Category | Description |
|---|---|
| **New** | Insight exists in current but not previous |
| **Removed** | Insight existed in previous but not current |
| **Modified** | Same insight_id but claim or confidence changed |
| **Confidence shift** | Same claim, different confidence level |
| **Status change** | Evaluation status changed (pass→fail, etc.) |
| **Hypothesis shift** | hypothesis_relation changed |

## Output structure

```markdown
# Delta Report: {participant_id}
## Run comparison: {previous_date} → {current_date}

### Summary
- New insights: 3
- Removed insights: 1
- Modified claims: 2
- Confidence changes: 1

### New insights
| ID | Claim | Confidence |
|---|---|---|

### Removed insights
| ID | Previous claim | Reason |
|---|---|---|

### Modified
| ID | Before | After | Change type |
|---|---|---|---|
```

## When to use

- After adding a new participant and re-running synthesis
- After config changes (different hypotheses, different interviewee_speaker)
- After revelation loops to see what was revised
- Comparing two research rounds on the same topic
