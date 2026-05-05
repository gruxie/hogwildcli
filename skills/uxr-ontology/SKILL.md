---
name: uxr-ontology
description: Generate or apply a tagging ontology to research insights and transcript segments. Use when the user wants to create a structured label set for annotation, indexing, or video clipping. Can generate an ontology from existing insights or apply an existing ontology to new data.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_synthesis
  - hogwild-uxr_manage_dictionary
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
---

# Ontology Tagger

Generates a structured annotation ontology from extracted insights, or applies an existing ontology to tag transcript segments.

## Workflow — Generate ontology

1. Call `load_config` for study context
2. Call `get_insights` for all finalized participants
3. Optionally call `get_synthesis` for theme structure
4. Derive ontology domains and tags from patterns in the data
5. Call `manage_dictionary` with action `set` to persist the ontology
6. Call `save_artifact` with `ontology.json` and type `ontology`

## Workflow — Apply ontology

1. Call `manage_dictionary` with action `get` to load existing ontology
2. Call `get_insights` for target participant(s)
3. Match insights and evidence to ontology tags
4. Call `save_artifact` with annotated output

## Ontology structure

```json
{
  "domains": [
    {
      "domain_id": "D1",
      "domain_label": "Trust & Governance",
      "description": "Tags related to trust, oversight, and control mechanisms",
      "tags": [
        {
          "tag_id": "D1-T01",
          "label": "trust-conditional",
          "description": "Trust expressed as conditional on specific factors",
          "examples": ["I trust it if...", "Only when I can verify..."]
        }
      ]
    }
  ]
}
```

## Generation rules

- Group tags into 4-8 domains based on conceptual similarity
- Each domain should have 3-10 tags
- Tags should be mutually exclusive within a domain where possible
- Prefer participant language for tag labels
- Every tag must be grounded in at least one insight from the data

## Application rules

- A single insight may receive tags from multiple domains
- Tag confidence follows the source insight's confidence level
- Include timestamp ranges for video annotation compatibility
