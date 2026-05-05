---
name: uxr-labeler
description: Apply qualitative labels to insights using a managed dictionary with confidence tiers. Use when the user wants to code or categorize insights, build a codebook, or apply thematic labels. Supports dictionary creation, merging, and application with confidence tracking.
allowed-tools:
  - hogwild-uxr_manage_dictionary
  - hogwild-uxr_apply_labels
  - hogwild-uxr_get_labels
  - hogwild-uxr_get_insights
  - hogwild-uxr_load_config
---

# Qualitative Labeler

Applies qualitative coding labels to insights using a managed dictionary. Supports iterative codebook development and multi-pass labeling.

## Workflow — Build dictionary

1. Call `load_config` for study context
2. Call `get_insights` for all participants
3. Derive initial labels from patterns in claims and evidence
4. Structure labels with confidence tiers
5. Call `manage_dictionary` with action `set` to persist

## Workflow — Apply labels

1. Call `manage_dictionary` with action `get` to load dictionary
2. Call `get_insights` for target participant
3. Match each insight to dictionary labels
4. Assign confidence tier per label application
5. Call `apply_labels` with the labeled insight array

## Workflow — Merge new labels

1. Call `manage_dictionary` with action `get` for current dictionary
2. Identify insights that don't fit existing labels
3. Create new label entries
4. Call `manage_dictionary` with action `merge` to add without overwriting

## Dictionary entry format

```json
{
  "id": "L001",
  "label": "trust-conditional",
  "description": "Trust expressed as dependent on specific conditions being met",
  "domain": "Trust & Governance",
  "examples": ["I trust it when...", "Only if I can verify..."],
  "created_from": "P1_I003"
}
```

## Confidence tiers for label application

| Tier | Criteria |
|---|---|
| **Direct** | The insight's claim explicitly matches the label's description |
| **Inferred** | The insight relates to the label through evidence context |
| **Weak** | Tentative association, may need review |

## Labeled insight format

```json
{
  "insight_id": "P1_I003",
  "labels": [
    {"label_id": "L001", "confidence": "direct"},
    {"label_id": "L015", "confidence": "inferred"}
  ]
}
```

## Quality rules

- Every label must trace to the dictionary
- A single insight can have multiple labels from different domains
- Do not force-fit labels — if nothing fits, flag for dictionary expansion
- Track which insights have no labels (potential gap in codebook)
