---
name: uxr-evaluator
description: Evaluate whether insights extracted from UX research transcripts are accurately grounded in the source material. Use this skill after insight extraction to verify findings, check for hallucination or over-interpretation. Triggers on "check these insights," "verify the findings," "are these accurate," or "evaluate the analysis." Requires insights JSON and _turns.json files.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_submit_evaluation
  - hogwild-uxr_get_artifact
---

# Insight Evaluator

Assesses whether each insight accurately reflects the transcript content — not whether it's interesting or strategically valuable. Scope is strictly: **does this insight faithfully represent what the interviewee said?**

## Required inputs

| Input | Format | Source |
|---|---|---|
| Insights | JSON array | Output of uxr-extractor (via `get_insights`) |
| `_turns.json` | JSON | Output of uxr-preprocessor (in output dir) |
| Research question | Plain text | From config |
| Hypotheses | Plain text | From config |

## What this evaluation is NOT

- Not an assessment of insight quality or strategic value
- Not a check on research methodology
- Not a judgment on whether research questions were answered

If a claim is factually accurate to the transcript but uninteresting, it passes. If interesting but overstated, it fails.

## Workflow

1. Call `get_insights` to retrieve the current insights for the participant
2. Read the `{stem}_turns.json` file from the output directory
3. Run the 5 evaluation checks below on each insight
4. Call `submit_evaluation` with the evaluation result JSON

## Evaluation procedure

For each insight, run these checks in order. Stop at the first failure.

### Check 1: Quote verification

Look up each `evidence` block in `_turns.json`:
- Find the turn with matching `speaker` and `timestamp`
- Check whether the `quote` appears in the turn's `utterance`
- Acceptable: minor omission of filler words
- Not acceptable: paraphrasing, reordering, added words

**Fail type:** `quote-distortion`

### Check 2: Attribution check

- Confirm evidence `speaker` is the interviewee, not the moderator
- Confirm claim is scoped to this individual, not generalized

**Fail type:** `attribution-bleed`

### Check 3: Claim-to-evidence alignment

Does the claim say exactly what the quotes say, or more?
- Uses language the participant didn't use?
- Implies frequency the evidence doesn't support?
- Mirrors hypothesis language rather than participant's framing?

**Fail types:** `extrapolation`, `frequency-distortion`, `hypothesis-projection`

### Check 4: Moderator contamination

If the quoted turn responds to a direct moderator prompt:
- Is the response substantive (elaborated, unprompted extension)?
- Or minimal agreement ("Yeah," "Exactly," "Right")?

Minimal agreement alone does not constitute evidence.

**Fail type:** `moderator-contamination`

### Check 5: Unsupported claims

If a claim has no evidence block, or all evidence failed Check 1, it has no grounding.

**Fail type:** `unsupported`

## Output format

```json
{
  "evaluation_summary": {
    "total_insights": 12,
    "passed": 8,
    "flagged": 2,
    "failed": 2,
    "recommend_revelation": true
  },
  "results": [
    {
      "insight_id": "P1_I001",
      "status": "pass | flag | fail",
      "issue_type": null,
      "explanation": "Brief explanation.",
      "transcript_ref": {
        "speaker": "Smith, Devon P",
        "timestamp": "01:26 - 02:48",
        "actual_utterance_excerpt": "What the transcript actually says."
      },
      "revelation_instruction": null
    }
  ]
}
```

### Status definitions

| Status | Meaning |
|---|---|
| `pass` | All checks passed. Insight is faithfully grounded. |
| `flag` | Minor issue that weakens confidence. Revelation optional. |
| `fail` | Misrepresents transcript. Must go through Revelation. |

### `recommend_revelation`

Set `true` if any insight has `status: fail`. Set `false` if all are `pass` or `flag`.

## Revelation instructions

Write `revelation_instruction` as a direct, specific instruction to the extractor:
- Be concrete: "Narrow the claim to X" not "reconsider the evidence"
- Include actual transcript text in `transcript_ref`
- State what's wrong and what to do

## Reference files

- `references/failure-taxonomy.md` — Full definitions of each issue type
- `references/pass-criteria.md` — Guidance on borderline cases
