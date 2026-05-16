---
name: uxr-controller
description: Orchestrate the full UX research sense-making pipeline end-to-end. Use whenever the user wants to run the complete analysis on one or more transcripts — convert, extract, evaluate, loop, and synthesize. Triggers on "run the full analysis," "analyze these transcripts," "extract and verify insights," "run all participants," "analyze participant 1 and 2," or whenever transcript files, research questions, and hypotheses are all present.
allowed-tools:
  - hogwild-uxr_load_config
  - hogwild-uxr_preflight_check
  - hogwild-uxr_parse_transcript
  - hogwild-uxr_start_participant
  - hogwild-uxr_submit_insights
  - hogwild-uxr_submit_evaluation
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_revelation_context
  - hogwild-uxr_get_project_status
  - hogwild-uxr_submit_synthesis
  - hogwild-uxr_save_artifact
  - hogwild-uxr_detect_speakers
  - hogwild-uxr_scaffold_config
  - hogwild-uxr_reset_participant
  - hogwild-uxr_list_grounding_artifacts
  - hogwild-uxr_get_grounding_artifact
---

# Sense-Making Controller

Orchestrates the full pipeline. This skill coordinates the other skills in sequence:

```
[uxr-grounding]  ← Mode 0: run once before first analysis (or skip)
      ↓
[uxr-preprocessor] → [uxr-extractor] → [uxr-evaluator]
                           ↑                    |
                           |  (Revelation loop) |
                           └────────────────────┘
                                                |
                             (all participants complete)
                                                ↓
                              [uxr-synthesizer]
                          (themes × hypothesis buckets)
                                                ↓
                     [uxr-narrator] / [uxr-debriefer] / [uxr-cdnotes]
```

## Workflow

### Phase 0: Setup
1. Call `load_config` with `research_config.yaml`
2. Call `preflight_check` to verify all transcripts exist
3. If issues found, report to user and stop

### Phase 0.5: Grounding check
1. Call `list_grounding_artifacts` to check if grounding has been initialized
2. If `focus_memo.md` is absent and this is the first analysis run, offer to run `uxr-grounding` before proceeding
3. If the researcher declines or grounding already exists, continue
4. If grounding exists, call `get_grounding_artifact` for `focus_memo.md` and hold it in context — it will be passed to extraction in Phase 2

### Phase 1: Preprocessing (per participant)
1. Call `parse_transcript` for each participant
2. Confirm speaker lists look correct with the user
3. Participants transition to `preprocessed` state

### Phase 2: Extraction (per participant)
1. Call `start_participant` to begin extraction loop
2. Read the converted transcript from output directory
3. If a `focus_memo.md` was loaded in Phase 0.5, include it as context when applying uxr-extractor reasoning — the extractor uses it to orient attention
4. Apply uxr-extractor reasoning to produce insight JSON
5. Call `submit_insights` with the structured array

### Phase 3: Evaluation (per participant)
1. Read the submitted insights and `_turns.json`
2. Apply uxr-evaluator reasoning (5-check process)
3. Call `submit_evaluation` with evaluation JSON
4. The MCP automatically handles:
   - Locking passed insights
   - Triggering revelation loop if needed
   - Finalizing when evaluation passes or max iterations reached

### Phase 4: Revelation Loop (if triggered)
1. Call `get_revelation_context` to get failed issues
2. Apply uxr-extractor revelation reasoning
3. Call `submit_insights` with revised array
4. Return to Phase 3 evaluation
5. Loop up to `max_iterations` times

### Phase 5: Synthesis (after all participants finalized)
1. Call `get_project_status` to confirm all participants are finalized
2. Call `get_insights` for each participant
3. Determine synthesis scope from the researcher's request:
   - "All participants" → include everyone, no comparison
   - "Only [cohort/tag]" → filter `participants[]` by matching `cohorts` or `tags` fields
   - "Compare [group A] and [group B]" → run synthesis for each group then produce a delta; max 2 groups — if more are implied, ask the researcher to clarify before running
4. Apply uxr-synthesizer reasoning
5. Call `submit_synthesis` with structured synthesis

### Phase 6: Reporting (optional)
1. Apply uxr-narrator, uxr-debriefer, or uxr-cdnotes reasoning as appropriate
2. Call `save_artifact` with the generated report

## Progress reporting

After each participant completes, report:
```
═══════════════════════════════════
 {participant_id} — COMPLETE
 Insights: {count} | Iterations: {n} | Pass: {p} Flag: {f} Fail: {f}
═══════════════════════════════════
```

## Configuration

All settings come from `research_config.yaml`:
- `output.max_iterations` — Revelation loop cap (default: 3)
- `participants[].interviewee_speaker` — Who to extract from
- `participants[].tags` — Free-form segment labels for filtering
- `participants[].cohorts` — Categorical group labels for filtering and comparison
- `research.question` — Guides extraction focus
- `research.hypotheses` — Attention scaffolds
- `study.motivations`, `study.goals`, `study.intended_impacts` — Default grounding context

See `references/config-reference.md` for full configuration options.
