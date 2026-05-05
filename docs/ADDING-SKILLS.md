# Adding New Skills to Hogwild UXR

This guide explains how to extend the pipeline with new skills. Skills are the extensibility mechanism — you can add new analytical capabilities without modifying the MCP server.

---

## What is a skill?

A Copilot CLI skill is a folder containing a `SKILL.md` file that tells Copilot:
- **When** to activate (via the `description` in YAML frontmatter)
- **What tools** it can use (via `allowed-tools` in frontmatter)
- **How to reason** about the domain (the Markdown body — instructions, rules, output formats)

Copilot auto-discovers skills and loads them when the user's request matches the skill's description.

---

## Quick start

### 1. Create the folder

```
skills/uxr-{your-skill-name}/
├── SKILL.md              ← Required
└── references/           ← Optional supporting docs
    └── guide.md
```

### 2. Write SKILL.md

```markdown
---
name: uxr-my-new-skill
description: One paragraph describing exactly when this skill should activate. Be specific about trigger phrases, prerequisites, and what it produces. Copilot uses this text to decide whether to load the skill — vague descriptions lead to false matches or missed activations.
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
---

# My New Skill

Brief description of purpose and value.

## Workflow

1. Call `load_config` to get study context
2. Call `get_insights` for target participants
3. Apply your reasoning logic (described below)
4. Call `save_artifact` with the output

## Reasoning instructions

(Domain-specific rules, quality checks, output format requirements)

## Output format

(Define exactly what this skill produces — schema, structure, examples)
```

### 3. Deploy

Copy to your Copilot skills directory:

```cmd
xcopy skills\uxr-my-new-skill "%USERPROFILE%\.copilot\skills\uxr-my-new-skill\" /E /I /Y
```

Or re-run the installer:
```cmd
install.bat
```

### 4. Reload and test

```
/skills reload
/skills info uxr-my-new-skill
```

Then invoke it:
```
Use the uxr-my-new-skill skill on my research data
```

---

## SKILL.md anatomy

### Frontmatter (YAML)

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Unique skill identifier (kebab-case, prefixed `uxr-`) |
| `description` | Yes | When to activate — Copilot matches user intent against this |
| `allowed-tools` | Yes | Which MCP tools this skill can call (prefix: `hogwild-uxr_`) |

### Body (Markdown)

The body is free-form Markdown injected into Copilot's context when the skill activates. Structure it for clarity:

1. **Title and purpose** — What this skill does in 1–2 sentences
2. **Workflow** — Step-by-step tool call sequence
3. **Reasoning instructions** — Domain rules Copilot must follow
4. **Output format** — Exact schema or structure to produce
5. **Quality rules** — What NOT to do, guardrails, edge cases

---

## Writing effective descriptions

The `description` field is the most important part — it determines when your skill activates.

**Good description:**
```yaml
description: Identify terminology confusion, mismatches, and alternative vocabulary usage across participant transcripts. Use after all participants are processed. Triggers on "terminology audit," "where were users confused," "labeling friction," or any request about product naming issues.
```

**Bad description:**
```yaml
description: Analyze terminology.
```

**Tips:**
- Include 3–5 trigger phrases users might actually say
- State prerequisites ("Use after all participants are processed")
- State what it produces ("Produces a term-by-term report")
- Be specific about scope to prevent false matches

---

## Available MCP tools

All tools are prefixed with `hogwild-uxr_` in the `allowed-tools` list.

### Reading data
| Tool | What it provides |
|------|-----------------|
| `load_config` | Study config (question, hypotheses, participants) |
| `get_project_status` | Which participants are in which state |
| `get_insights` | Insights for a specific participant |
| `get_synthesis` | Cross-participant synthesis |
| `get_artifact` | Content of any saved artifact |
| `list_artifacts` | List of all generated artifacts |
| `manage_dictionary` (action: get) | Current labeling dictionary |
| `get_labels` | Applied labels for a participant |

### Writing data
| Tool | What it saves |
|------|--------------|
| `save_artifact` | Any generated output (report, analysis, etc.) |
| `submit_insights` | Extracted insights (transitions state) |
| `submit_evaluation` | Evaluation results (transitions state) |
| `submit_synthesis` | Synthesis data |
| `manage_dictionary` (action: set/merge) | Dictionary updates |
| `apply_labels` | Label assignments |

### State management
| Tool | What it does |
|------|-------------|
| `start_participant` | Begin extraction loop |
| `reset_participant` | Reset to not_started |

**Important:** If your skill needs data operations not covered by these tools, you'll need to add a new tool to the MCP server (see below).

---

## When the MCP needs updating

Most new skills only need existing tools. But if you need new I/O operations:

### 1. Add tool function

Create or extend a file in `src/hogwild_uxr/tools/`:

```python
# src/hogwild_uxr/tools/my_new_io.py

from ..config import load_config, get_output_dir

def my_new_operation(config_path: str, some_data: dict) -> dict:
    """Do something with data and persist it."""
    config = load_config(config_path)
    if "error" in config:
        return config
    # ... your logic ...
    return {"status": "done"}
```

### 2. Register in server.py

```python
from .tools import my_new_io

@mcp.tool()
def my_new_operation(config_path: str, some_data: dict) -> str:
    """Brief description for Copilot tool discovery."""
    return json.dumps(my_new_io.my_new_operation(config_path, some_data), indent=2)
```

### 3. Reference in your skill

```yaml
allowed-tools:
  - hogwild-uxr_my_new_operation
```

### 4. Re-install

```cmd
uv sync
```

Restart Copilot CLI to pick up the new tool.

---

## Including reference files

For complex skills, put supporting documentation in `references/`:

```
skills/uxr-my-skill/
├── SKILL.md
└── references/
    ├── quality-guide.md
    └── schema.md
```

In your SKILL.md, instruct Copilot to read them:

```markdown
## Before starting

Read `references/quality-guide.md` for the full quality framework.
```

Copilot will load reference files when the skill activates.

---

## Testing a new skill

1. Start Copilot CLI: `copilot --allow-all-tools`
2. Invoke directly: "Use the uxr-my-skill skill to analyze my data"
3. Verify:
   - Correct MCP tools called in the right order
   - Output matches your defined format
   - Edge cases handled (empty data, single participant, etc.)
4. Check artifact: Look in the `output/` folder for the saved file

---

## Examples

### Simple analysis skill (read-only)

A skill that reads existing data and produces a report — no state changes:

```yaml
allowed-tools:
  - hogwild-uxr_get_insights
  - hogwild-uxr_get_synthesis
  - hogwild-uxr_save_artifact
  - hogwild-uxr_load_config
```

### Pipeline skill (writes state)

A skill that participates in the extraction-evaluation pipeline:

```yaml
allowed-tools:
  - hogwild-uxr_start_participant
  - hogwild-uxr_submit_insights
  - hogwild-uxr_get_revelation_context
  - hogwild-uxr_load_config
```

### Dictionary/labeling skill

A skill that manages structured vocabularies:

```yaml
allowed-tools:
  - hogwild-uxr_manage_dictionary
  - hogwild-uxr_apply_labels
  - hogwild-uxr_get_insights
  - hogwild-uxr_load_config
```

---

## Naming conventions

- Skill folder: `uxr-{name}` (kebab-case, always prefixed)
- Skill name in frontmatter: matches folder name
- Output files: descriptive, lowercase, underscores: `terminology_audit.md`
- Artifact type: matches the skill category: `report`, `analysis`, `debrief`, `ontology`, etc.

---

## Checklist

Before shipping a new skill:

- [ ] `SKILL.md` has valid YAML frontmatter (name, description, allowed-tools)
- [ ] Description includes trigger phrases AND prerequisites
- [ ] Workflow section lists exact tool calls in order
- [ ] Output format is fully defined (schema or structure)
- [ ] Quality rules state what NOT to do
- [ ] Tested with `--allow-all-tools` against real data
- [ ] Reference files included if reasoning is complex
- [ ] Added to README.md skills table

## SKILL.md template

```markdown
---
name: uxr-{your-skill-name}
description: One paragraph describing when this skill should activate. Be specific about trigger phrases and conditions. Copilot uses this to decide when to load the skill automatically.
allowed-tools:
  - hogwild-uxr_tool_name_1
  - hogwild-uxr_tool_name_2
---

# Skill Title

Brief description of what this skill does.

## Workflow

1. Call `tool_name_1` to get data
2. Apply reasoning (described below)
3. Call `tool_name_2` to save results

## Reasoning instructions

(Your domain-specific instructions go here)

## Output format

(Define what the skill produces)
```

## Key principles

### 1. Skills carry reasoning, MCP carries state

Your skill should tell Copilot *how to think* about the domain. The MCP tools handle reading/writing data. Never put reasoning logic in MCP tools.

### 2. Be specific in descriptions

The `description` field determines when Copilot auto-activates your skill. Include:
- Specific trigger phrases users might say
- Prerequisites (what must be true before this skill runs)
- Clear scope (what this skill does and doesn't do)

### 3. Reference existing MCP tools

Available tools (prefix with `hogwild-uxr_`):
- `load_config` — Load project configuration
- `get_project_status` — Check participant states
- `get_insights` — Read insights for a participant
- `get_synthesis` — Read cross-participant synthesis
- `get_artifact` — Read any saved artifact
- `save_artifact` — Write an artifact to output
- `submit_insights` — Submit extracted insights
- `submit_evaluation` — Submit evaluation results
- `submit_synthesis` — Submit synthesis data
- `manage_dictionary` — Read/write labeling dictionary
- `apply_labels` — Save labeled insights

### 4. If you need new I/O

If your skill needs data operations not covered by existing tools:
1. Add a new tool function in `src/hogwild_uxr/tools/`
2. Register it in `server.py`
3. Reference it in your skill's `allowed-tools`

### 5. Include reference files

For complex skills, put supporting documentation in a `references/` subfolder. Your SKILL.md can instruct Copilot to "Read `references/guide.md` before proceeding."

## Deploying

After creating your skill:

1. Place it in the `skills/` directory of the repo
2. Re-run `install.bat` or `install.sh` to copy to `~/.copilot/skills/`
3. Restart Copilot CLI
4. Verify with `/skills list`

Or manually copy the folder to `~/.copilot/skills/uxr-{name}/`.

## Testing

To test a new skill:
1. Start Copilot CLI with `--allow-all-tools`
2. Invoke your skill directly: "Use the uxr-{name} skill to..."
3. Verify it calls the correct MCP tools
4. Check that output artifacts are well-formed
