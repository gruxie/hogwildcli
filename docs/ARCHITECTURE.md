# Architecture

## Overview

Hogwild UXR uses a two-layer architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Copilot CLI                                │
│                  (LLM reasoning engine)                       │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ User prompt │→ │ Skill match  │→ │ Execute workflow   │  │
│  │             │  │ (by desc)    │  │ (call MCP tools)   │  │
│  └─────────────┘  └──────────────┘  └───────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ MCP tool calls (stdio)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  hogwild-uxr MCP Server                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │Lifecycle │  │State I/O │  │Synthesis │  │Artifact   │  │
│  │  tools   │  │  tools   │  │  I/O     │  │  I/O      │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────┘  │
│  ┌──────────┐  ┌──────────────────────────────────────┐    │
│  │Labeling  │  │  Preprocessing                       │    │
│  │  I/O     │  │  (parse_transcript)                  │    │
│  └──────────┘  └──────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  State Machine  │  Config  │  Sandbox  │  Provenance │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    File System (output/)
```

## How it works

### 1. User speaks naturally
```
"Analyze my transcripts and generate a report for PMs"
```

### 2. Copilot CLI matches skills
Based on the `description` field in each SKILL.md, Copilot identifies which skills are relevant (e.g., `uxr-controller` for full pipeline, `uxr-narrator` for reports).

### 3. Skill provides reasoning instructions
The SKILL.md body tells Copilot:
- What MCP tools to call and in what order
- How to reason about the domain (extraction rules, evaluation checks, etc.)
- What output format to produce

### 4. Copilot calls MCP tools
Via stdio transport, Copilot invokes `hogwild-uxr` tools to:
- Read/write state
- Load/save artifacts
- Transition the pipeline state machine

### 5. MCP handles I/O deterministically
The MCP server is pure state + I/O — no LLM reasoning. It:
- Validates inputs (schema, state transitions)
- Persists data to disk
- Returns structured JSON responses
- Tracks provenance

## Tool modules

The MCP server organizes its 19 tools into 5 modules:

| Module | Tools | Responsibility |
|--------|-------|---------------|
| `lifecycle` | detect_speakers, scaffold_config, load_config, preflight_check, get_project_status | Project setup and status |
| `preprocessing` | parse_transcript | .docx → .md + .json conversion |
| `state_io` | start_participant, submit_insights, submit_evaluation, get_insights, get_revelation_context, reset_participant | Pipeline state transitions |
| `synthesis_io` | submit_synthesis, get_synthesis | Cross-participant synthesis |
| `artifact_io` | save_artifact, list_artifacts, get_artifact | Generic output persistence |
| `labeling_io` | manage_dictionary, apply_labels, get_labels | Qualitative coding support |

## Skills inventory

14 skills ship with the package:

| Skill | Role | Category |
|-------|------|----------|
| `uxr-controller` | Full pipeline orchestrator | Orchestration |
| `uxr-preprocessor` | .docx → structured transcript | Preprocessing |
| `uxr-extractor` | Evidence-grounded insight extraction | Core pipeline |
| `uxr-evaluator` | 5-check insight verification | Core pipeline |
| `uxr-synthesizer` | Cross-participant theme building | Core pipeline |
| `uxr-narrator` | Audience-tailored narrative reports | Reporting |
| `uxr-debriefer` | Stakeholder debrief generation | Reporting |
| `uxr-contradiction` | Intra/inter-participant conflict detection | Analysis |
| `uxr-ontology` | Structured tagging taxonomy | Analysis |
| `uxr-annotator` | Transcript annotation with tags/insights | Analysis |
| `uxr-delta` | Run-over-run change tracking | Analysis |
| `uxr-cohort-delta` | Subset-vs-synthesis comparison | Analysis |
| `uxr-terminology` | Terminology confusion audit | Analysis |
| `uxr-labeler` | Qualitative coding with managed dictionary | Labeling |

## Core infrastructure

| Module | Purpose |
|--------|---------|
| `state.py` | State machine (transitions, persistence, schema versioning) |
| `config.py` | YAML config loading, validation, path resolution |
| `sandbox.py` | Path sandboxing — all writes constrained to `output/` |
| `provenance.py` | Artifact metadata sidecars (creator, timestamp, lineage) |
| `errors.py` | Structured JSON error responses with error codes |

## Why this architecture?

| Concern | Monolith (v3) | Skills-based (v4) |
|---------|--------------|-------------------|
| **Reasoning** | Embedded in tool returns as system_prompt | Lives in SKILL.md files |
| **Extensibility** | Add tool → modify server.py | Add folder → auto-discovered |
| **Tool count** | 46 (overwhelming) | 19 (focused I/O) |
| **API key** | Not needed (but prompts were bulky) | Not needed (clean separation) |
| **Testing** | Test tools individually | Test MCP I/O + skills independently |

## State machine

```
not_started → preprocessed → extracting → evaluating →
                                  ↑              |
                                  |   (loop)     |
                                  └──────────────┘
                                                 |
                              in_revelation → extracting (next iter)
                                                 OR
                                              finalized
```

Each participant moves through this independently. The state machine enforces valid transitions and prevents out-of-order operations.

## File layout (output/)

```
output/
├── .pipeline_state.json           ← State machine persistence
├── {stem}_converted.md            ← Preprocessed transcript
├── {stem}_turns.json              ← Structured turns for evaluator
├── {stem}_insights_iter1.json     ← Per-iteration insights
├── {stem}_insights_locked.json    ← Passed insights (accumulated)
├── {stem}_insights_final.json     ← Final insight set
├── {stem}_evaluation_final.json   ← Final evaluation
├── {stem}_provenance.json         ← Provenance record
├── synthesis.json                 ← Cross-participant synthesis
├── labels/                        ← Qualitative coding outputs
│   ├── dictionary.json            ← Managed label dictionary
│   └── {participant}_labels.json  ← Applied labels per participant
├── *.meta.json                    ← Artifact metadata sidecars
└── (generated reports/narratives)
```

## Deployment model

```
~/.copilot/
├── mcp-config.json              ← Registers the MCP server
└── skills/
    ├── uxr-controller/SKILL.md  ← Auto-discovered by Copilot CLI
    ├── uxr-preprocessor/SKILL.md
    ├── uxr-extractor/SKILL.md
    ├── uxr-evaluator/SKILL.md
    ├── uxr-synthesizer/SKILL.md
    ├── uxr-narrator/SKILL.md
    ├── uxr-debriefer/SKILL.md
    └── ... (14 total)

project-folder/
├── research_config.yaml         ← User creates per-study
├── transcripts/                 ← Input .docx files
└── output/                      ← All generated artifacts (sandboxed)
```

The MCP server runs as a subprocess spawned by Copilot CLI via stdio transport. No network, no API keys, no containers.

## Design principles

1. **Skills carry reasoning, tools carry state** — The MCP server never returns system prompts or reasoning instructions. All domain logic lives in SKILL.md files.
2. **Path sandboxing** — All write operations are confined to the project's `output/` directory. The server rejects attempts to escape.
3. **Provenance by default** — Every artifact gets a `.meta.json` sidecar tracking creator, timestamp, and lineage.
4. **Idempotent tools** — Tools can be re-called safely. State transitions are validated (invalid transitions return errors, not corruption).
5. **Extensible without server changes** — New analytical capabilities are added as SKILL.md files that compose existing tools. No code changes needed.
