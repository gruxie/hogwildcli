---
name: uxr-controller
description: Orchestrate the full UX research sense-making pipeline end-to-end. Use whenever the user wants to run the complete analysis on one or more transcripts — convert, extract, evaluate, loop, and synthesize. Triggers on "run the full analysis," "analyze these transcripts," "extract and verify insights," or whenever transcript files, research questions, and hypotheses are all present.
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
---

# Sense-Making Controller

Orchestrates the full pipeline. This skill coordinates the other skills in sequence:

```
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
                     [uxr-narrator] / [uxr-debriefer]
```

## Workflow

### Phase 0: Setup
1. Call `load_config` with `research_config.yaml`
2. Call `preflight_check` to verify all transcripts exist
3. If issues found, report to user and stop

### Phase 1: Preprocessing (per participant)
1. Call `parse_transcript` for each participant
2. Confirm speaker lists look correct with the user
3. Participants transition to `preprocessed` state

### Phase 2: Extraction (per participant)
1. Call `start_participant` to begin extraction loop
2. Read the converted transcript from output directory
3. Apply uxr-extractor reasoning to produce insight JSON
4. Call `submit_insights` with the structured array

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
3. Apply uxr-synthesizer reasoning
4. Call `submit_synthesis` with structured synthesis

### Phase 6: Reporting (optional)
1. Apply uxr-narrator or uxr-debriefer reasoning
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
- `research.question` — Guides extraction focus
- `research.hypotheses` — Attention scaffolds

See `references/config-reference.md` for full configuration options.
