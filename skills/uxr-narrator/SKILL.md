---
name: uxr-narrator
description: Generate an audience-ready narrative artifact from completed pipeline synthesis. Use when transforming research findings into polished communication for a specific audience (pm, designer, engineer, executive) and format (report, slides, memo, hybrid). Requires completed synthesis outputs. Produces the artifact plus a mandatory integrity review.
allowed-tools:
  - hogwild-uxr_get_synthesis
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_artifact
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
---

# Narrative Composer

Transforms completed UX research synthesis into audience-ready communication artifacts while preserving fidelity to source data.

## Workflow

1. Call `load_config` to get study metadata and participant aliases
2. Call `get_synthesis` to load structured synthesis data
3. Call `get_insights` for each participant to get quotes and evidence
4. Ask the user for audience and format (if not specified)
5. Apply narrative framework below to compose the artifact
6. Run integrity audit (MANDATORY)
7. Call `save_artifact` with filename `narrative_report_{audience}.md`

## Audience behavior

| Audience | Lead with | Organize around | Recommendation framing |
|---|---|---|---|
| `pm` | Prioritization and tradeoffs | Hypotheses as decision gates | "The data suggests we should..." |
| `designer` | Unmet needs and experience breakdowns | User moments | "Participants need..." |
| `engineer` | System implications and failure modes | Workflows and constraints | Precision over motivation |
| `executive` | Single most important tension | 3–5 findings max | Risk/opportunity language |

## Narrative framework

Each finding follows: **Context → Tension → Insight → Implication → Resolution**

## Quote usage rules

- Use participant aliases (from config), not full names
- **Minimum 2, maximum 3 direct quotes per finding**
- Format as blockquote with participant alias in bold
- Never edit a quote for flow; use ellipsis to condense
- A quote can illustrate a theme; it cannot establish one

| Confidence | Usage |
|---|---|
| **High** | Use freely as illustrative anchors |
| **Medium** | Use with hedge: "one participant noted..." |
| **Low** | Only in minority view sections, explicitly labeled |

## Integrity audit (MANDATORY)

Every run includes a narrative integrity audit checking for transformation risks:

| Risk | Guardrail |
|---|---|
| **Prevalence inflation** | "Participants felt" requires 4+/6; "some" for 2–3/6 |
| **Confidence laundering** | Match claim language to confidence level |
| **Anecdote elevation** | A quote illustrates; it cannot establish |
| **Hypothesis suppression** | Every hypothesis outcome must appear |
| **Causality overreach** | Use "associated with" not "because of" |
| **Minority view flattening** | Label and include; never silently drop |

## Output

The artifact always includes:
- **Part 1:** The narrative artifact (audience-ready)
- **Part 2:** Integrity review (status, issues found, revisions made, decisions needed)

See `references/narrative-framework.md` for the complete workflow details.
