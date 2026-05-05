---
name: uxr-preprocessor
description: Convert UX research transcript .docx files into structured Markdown and JSON before insight extraction. Use this skill whenever the user provides .docx transcript files and wants to analyze, extract insights from, or evaluate them. Always run this skill FIRST before extraction or evaluation. Triggers on mentions of .docx transcripts, interview files, or batch transcript conversion.
allowed-tools:
  - hogwild-uxr_parse_transcript
  - hogwild-uxr_detect_speakers
  - hogwild-uxr_load_config
  - hogwild-uxr_preflight_check
---

# Transcript Preprocessor

Converts `.docx` research transcripts to clean Markdown + structured JSON before insight extraction.

## Why this step exists

The insight-extractor and insight-evaluator skills work on plain text. `.docx` files are binary and need parsing. This step:
- Normalizes speaker attribution (critical for evaluator accuracy checks)
- Produces a `_turns.json` file — the evaluator uses this for precise quote verification
- Detects structural anomalies (missing utterances, malformed timestamps)
- Tags every utterance with its source file for multi-file evidence tracking

## Expected .docx format

Transcripts with this repeating structure:

```
Speaker Name
HH:MM - HH:MM
Utterance text

Speaker Name
HH:MM - HH:MM
Utterance text
```

## Workflow

1. Call `load_config` with the project's `research_config.yaml` path
2. Call `preflight_check` to verify transcripts exist
3. For each participant, call `parse_transcript` with the config path and participant ID
4. Review the returned speaker list and turn count
5. Confirm with the user that the interviewee speaker was correctly identified

## After conversion

The skill produces two files per transcript in the output directory:
- `{stem}_converted.md` — Human-readable Markdown
- `{stem}_turns.json` — Structured turn data for the evaluator

Pass these to the **uxr-extractor** skill next.

## Warnings to surface

- If speakers appear only once (possible label inconsistency)
- If 10+ unique speaker names detected (labels not normalized)
- If any turn has no utterance text
- If the file uses a non-standard format

Always show the speaker list and turn count to the user after conversion.
