---
name: uxr-annotator
description: Annotate preprocessed transcripts with ontology tags, insight references, and hypothesis markers. Use when creating an annotated version of a transcript for review, video clipping, or stakeholder sharing. Requires preprocessed transcripts, extracted insights, and an annotation ontology.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_artifact
  - hogwild-uxr_manage_dictionary
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
---

# Transcript Annotator

Produces annotated transcript files with inline tags, insight references, and exportable timestamp ranges.

## Workflow

1. Call `load_config` for participant info
2. Call `get_insights` for the target participant
3. Call `manage_dictionary` to load the ontology (if available)
4. Read the `{stem}_converted.md` from output directory via `get_artifact`
5. Walk through the transcript turn by turn, applying annotations
6. Call `save_artifact` with `{participant_id}_annotated.md` and type `annotated-transcript`

## Annotation types

### Insight references
Mark turns that serve as evidence for insights:
```markdown
**Smith, Devon P** `[01:26 - 02:48]` 📌 P1_I001, P1_I003
Devon's response about using VS Code specifically for AI tasks...
```

### Ontology tags
Apply domain tags to relevant turns:
```markdown
**Smith, Devon P** `[04:41 - 05:26]` 🏷️ trust-conditional, tool-preference
I prefer the other one. I know exactly what to do...
```

### Hypothesis markers
Flag turns relevant to specific hypotheses:
```markdown
**Smith, Devon P** `[08:12 - 09:30]` 🎯 H2-supports
I started using it because I wanted to learn...
```

## Output format

The annotated transcript preserves the original structure with inline annotations added after timestamps. A summary table at the top shows:
- Total annotated turns / total turns
- Tags applied (with counts)
- Insights referenced
- Timestamp ranges for video clipping

## Video clipping export

Include a section at the bottom:
```json
{
  "clips": [
    {
      "start": "01:26",
      "end": "02:48",
      "tags": ["trust-conditional"],
      "insight_ids": ["P1_I001"],
      "speaker": "Smith, Devon P"
    }
  ]
}
```
