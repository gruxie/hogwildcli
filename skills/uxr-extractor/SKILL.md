---
name: uxr-extractor
description: Extract grounded insights from UX research transcripts. Use this skill whenever the user wants to analyze interview transcripts, surface findings from qualitative sessions, identify themes or patterns from participant responses, or generate insights to test against research hypotheses. Requires preprocessed transcripts from the uxr-preprocessor skill. Triggers on phrases like "extract insights," "analyze this transcript," "what did we learn," or "what are the key findings."
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_submit_insights
  - hogwild-uxr_start_participant
  - hogwild-uxr_get_revelation_context
  - hogwild-uxr_get_artifact
---

# Insight Extractor

Extracts structured, evidence-grounded insights from preprocessed UX research transcripts.

## Required inputs

| Input | Format | Notes |
|---|---|---|
| Transcript | `{stem}_converted.md` from preprocessor | Read from output dir |
| Turns JSON | `{stem}_turns.json` from preprocessor | Required for evidence traceability |
| Research question | From `research_config.yaml` | The guiding question |
| Hypotheses | From `research_config.yaml` | Attention scaffolds, not filters |
| Issues list | From evaluator (optional) | Only on Revelation re-runs |

## Workflow

1. Call `start_participant` to transition state to 'extracting'
2. Read the `{stem}_converted.md` transcript from the output directory
3. Apply the extraction rules below to produce insight JSON
4. Call `submit_insights` with the structured insight array

On **Revelation re-runs** (iteration > 1):
1. Call `get_revelation_context` to get failed issues + transcript
2. Revise only the failed insights per the revelation rules below
3. Call `submit_insights` with the full revised array

## Who counts as a participant

Extract insights **only from the interviewee's turns** — not the moderator/interviewer. The interviewee speaker name is provided in the research config.

Do not quote or attribute the moderator.

## Core extraction rules

**Grounding over interpretation.** Every insight must be traceable to specific utterance(s). If you cannot identify the turn(s) that support a claim, do not make the claim.

**Quote before you claim.** Locate the supporting evidence first, then state the insight. Never work in reverse.

**Frequency matters for accuracy.** If something was said once, the insight should reflect that. Do not use "participants consistently noted" unless evidence supports it across multiple turns.

**Hypotheses are a lens, not a leash.** Let them direct your attention but surface all substantive insights, including those that contradict or are unrelated to hypotheses. Mark the relationship explicitly.

**Moderator questions are context, not evidence.** Never treat the moderator's framing as confirmation of the participant's view.

## Output format

Return a JSON array of insight objects:

```json
[
  {
    "insight_id": "P1_I001",
    "claim": "One clear declarative sentence stating the insight.",
    "evidence": [
      {
        "speaker": "Smith, Devon P",
        "timestamp": "01:26 - 02:48",
        "source_file": "Meeting_-_P1_Devon",
        "quote": "Near-verbatim or verbatim excerpt supporting the claim."
      }
    ],
    "hypothesis_relation": "supports | contradicts | complicates | novel",
    "hypothesis_ref": "Which hypothesis this relates to, or null if novel",
    "confidence": "high | medium | low",
    "confidence_rationale": "Brief explanation",
    "notes": "Optional: anything ambiguous or worth flagging"
  }
]
```

### Confidence calibration

| Level | Criteria |
|---|---|
| **High** | Explicitly stated, unprompted or elaborated across multiple turns, unambiguous |
| **Medium** | Stated once clearly, or implied across multiple turns but not explicit |
| **Low** | Implied or inferred from indirect language; participant hedged or was uncertain |

## Revelation mode (re-run with issues)

When failed issues are provided:

1. Read the full issues list before re-extracting.
2. For each flagged insight:
   - **Extrapolation:** Return to transcript. Produce a corrected insight with tighter scope, or withdraw.
   - **Attribution bleed:** Restrict claim to the specific speaker whose turns support it.
   - **Frequency distortion:** Revise language to reflect actual frequency.
   - **Unsupported:** Find genuine supporting evidence or withdraw the insight.
3. Do not revise insights that passed — only process failed ones.
4. Return the full list: passed insights unchanged + revised/withdrawn insights marked.

Add `"revelation_revision"` to any revised insight:
```json
"revelation_revision": {
  "previous_issue": "extrapolation",
  "change_made": "Narrowed claim from general preference to specific tool context"
}
```

## What not to include

- Moderator speech or paraphrases of participant views
- Insights based solely on participant agreement with moderator framing
- Claims about what participants "would" do unless stated directly
- Demographic/background facts (these are context, not insights)

## Before extracting

Read `references/failure-taxonomy.md` to know what the evaluator will flag.
Then proceed turn by turn through the interviewee's utterances.
