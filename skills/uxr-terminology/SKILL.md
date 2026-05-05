---
name: uxr-terminology
description: Scan all participant transcripts and insights to identify terminology confusion, mismatches, and alternative vocabulary usage. Use after all participants are processed. Produces a term-by-term report with evidence and design implications.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_artifact
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
  - hogwild-uxr_get_project_status
---

# Terminology Audit

Identifies terminology friction across participant transcripts — where product labels confused participants, didn't match mental models, or prompted different vocabulary.

## Workflow

1. Call `load_config` for study context
2. Call `get_project_status` to confirm all participants are finalized
3. Call `get_insights` for each participant
4. For each participant, read `{stem}_turns.json` via `get_artifact`
5. Scan turns for confusion signals (keywords below)
6. Cross-reference with insights that mention terminology
7. Call `save_artifact` with `terminology_audit.md` and type `terminology-audit`

## Confusion signal keywords

Scan interviewee turns for:
- "what do you mean", "what is", "what does", "I don't understand"
- "confused", "confusing", "clarify", "explain"
- "you mean", "so you're saying", "in other words"
- "what you call", "what we call", "is that what"
- "not clear", "unclear", "don't follow"

## Confusion types

| Type | Definition |
|---|---|
| **Confusion** | Participant doesn't know the term or asks what it means |
| **Mismatch** | Participant uses term but has different mental model |
| **Alternative** | Participant uses a different word unprompted for the same concept |

## Output structure

1. Header: study title, participants analyzed, scope note
2. Summary table: term | confusion type(s) | participant count | severity
3. Per-term sections: type, participant evidence (alias, timestamp, quote, interpretation), design implication
4. Cross-cutting observations
5. Recommendations: high-priority terminology changes with rationale

## Severity

| Level | Criteria |
|---|---|
| **High** | 3+ participants confused |
| **Medium** | 2 participants |
| **Low** | 1 participant |

## Scope limitation

This is a targeted signal, not exhaustive. Implicit alternative vocabulary not caught by keywords won't appear.
