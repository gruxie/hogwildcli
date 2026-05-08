# Hogwild UXR

A UX research sense-making pipeline that turns interview transcripts into grounded, verified insights. Built on GitHub Copilot CLI with 14 specialized skills and a lightweight MCP server. No API keys required.

---

## Overview

Hogwild UXR automates the labor-intensive parts of qualitative research analysis while enforcing methodological rigor:

| Phase | What happens | Skill responsible |
|-------|-------------|-------------------|
| **Preprocess** | .docx → structured Markdown + JSON turns | `uxr-preprocessor` |
| **Extract** | Surface evidence-grounded insights from participant utterances | `uxr-extractor` |
| **Evaluate** | Verify every insight against the source transcript (5-check process) | `uxr-evaluator` |
| **Revelation** | Re-extract failed insights with targeted correction instructions | `uxr-extractor` (loop) |
| **Synthesize** | Build cross-participant themes organized by hypothesis | `uxr-synthesizer` |
| **Report** | Generate audience-tailored narratives with integrity audits | `uxr-narrator` / `uxr-debriefer` |

The pipeline prevents hallucination, extrapolation, and frequency distortion through a structured evaluation loop — every insight must trace to verbatim evidence in the transcript.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Copilot CLI                        │
│               (LLM reasoning engine — no API key)           │
├─────────────────────────────────────────────────────────────┤
│  14 Skills (SKILL.md)           │  Orchestrator MCP         │
│  • Reasoning instructions       │  • State management       │
│  • Domain knowledge             │  • File I/O + validation  │
│  • Workflow sequences           │  • Provenance tracking    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Project folder (output/)
```

**Skills** contain all the reasoning: extraction rules, evaluation checks, narrative frameworks, quality guardrails.  
**MCP tools** are pure state + I/O: accept data, validate it, persist to disk, manage transitions.

See `docs/ARCHITECTURE.md` for the full technical design.

---

## Prerequisites

- **Python 3.10+**
- **uv** — Python package manager (`pip install uv` or [install guide](https://docs.astral.sh/uv/getting-started/installation/))
- **GitHub Copilot CLI** — Copilot in the terminal (requires GitHub Copilot subscription)

---

## Installation

### Step 1: Clone the repo

```bash
git clone https://github.com/gruxie/hogwildcli.git
cd hogwildcli
```

### Step 2: Install dependencies

```bash
uv sync
```

### Step 3: Copy skills to Copilot CLI

Copy the entire `skills/` directory contents to your Copilot skills folder:

**Windows (cmd.exe):**
```cmd
xcopy skills\uxr-* "%USERPROFILE%\.copilot\skills\" /E /I /Y
```

**macOS/Linux:**
```bash
cp -r skills/uxr-* ~/.copilot/skills/
```

### Step 4: Register the MCP server

Add this entry to `~/.copilot/mcp-config.json` (create the file if it doesn't exist):

```json
{
  "mcpServers": {
    "hogwild-uxr": {
      "command": "/full/path/to/uv",
      "args": ["run", "--project", "/full/path/to/hogwildcli", "hogwild-uxr"]
    }
  }
}
```

> **Note:** Replace both paths with your actual locations. On Windows use double backslashes (e.g., `C:\\Users\\you\\hogwildcli`). Find your `uv` path with `where uv` (Windows) or `which uv` (macOS/Linux).

### Step 5: Restart Copilot CLI and verify

```
/skills list
```

You should see all `uxr-*` skills listed. If not, check that the skills were copied to the correct location and restart.

### Shortcut: install.bat / install.sh

For convenience, an installer script is included that does steps 2–4 automatically:

```cmd
install.bat          (Windows)
./install.sh         (macOS/Linux)
```

> **Caution:** The installer overwrites `~/.copilot/mcp-config.json`. If you have other MCP servers registered, merge manually instead.

---

## Setting Up a Research Project

### 1. Create a project folder

```
my-study/
├── research_config.yaml
├── transcripts/
│   ├── Meeting_-_P1_Devon.docx
│   ├── Meeting_-_P2_Taylor.docx
│   └── Meeting_-_P3_Jordan.docx
└── output/                        ← created automatically
```

### 2. Write research_config.yaml

```yaml
study:
  title: "AI-Assisted App Modernization — Evaluative Research"
  description: "Semi-structured interviews exploring developer experience with AI tooling"
  method: "Semi-structured interview"

research:
  question: "What organizational and individual factors drive or hinder AI adoption in application modernization?"
  hypotheses:
    - "H1: Top-down — adoption is driven by management mandates and incentives"
    - "H2: Bottom-up — adoption is driven by individual developer motivations"
    - "H3: Social proof — adoption accelerates when peers demonstrate success"

participants:
  - id: P1
    file: "Meeting_-_P1_Devon.docx"
    interviewee_speaker: "Smith, Devon P"
    alias: "Devon"
  - id: P2
    file: "Meeting_-_P2_Taylor.docx"
    interviewee_speaker: "Johnson, Taylor M"
    alias: "Taylor"
  - id: P3
    file: "Meeting_-_P3_Jordan.docx"
    interviewee_speaker: "Lee, Jordan K"
    alias: "Jordan"

transcripts_dir: "./transcripts"

output:
  dir: "./output"
  max_iterations: 3       # Revelation loop cap
```

### 3. Place .docx transcripts

Put your transcript files in the `transcripts/` folder. Expected format:

```
Speaker Name
HH:MM - HH:MM
Utterance text goes here...

Speaker Name
HH:MM - HH:MM
Next utterance...
```

### 4. Run the analysis

Open Copilot CLI (with `--allow-all-tools` to skip per-tool confirmations):

```
copilot --allow-all-tools
```

Then:
```
Run the full analysis on my research project at C:\projects\my-study
```

---

## Usage Examples

### Full pipeline
```
Analyze all transcripts in C:\projects\my-study using research_config.yaml
```

### Individual operations
```
Extract insights from P1's transcript
Evaluate the insights for P1
Synthesize findings across all participants
Generate a narrative report for designers
Create a stakeholder debrief for leadership
```

### Post-analysis
```
Run a terminology audit across all participants
Find contradictions in the data
Compare P4, P5, P6 against the existing synthesis
Build a qualitative codebook from the insights
Annotate P1's transcript for video clipping
```

### Project setup help
```
Help me set up a new research project in C:\projects\new-study with 5 participants
```

---

## What's in the box

### 14 Skills

| Skill | Purpose | When to use |
|-------|---------|-------------|
| `uxr-controller` | Orchestrate full pipeline | "Run the full analysis" |
| `uxr-preprocessor` | .docx → .md + _turns.json | "Convert my transcripts" |
| `uxr-extractor` | Extract grounded insights | "What did participants say?" |
| `uxr-evaluator` | Verify against transcript | "Are these insights accurate?" |
| `uxr-synthesizer` | Cross-participant themes | "Find patterns across sessions" |
| `uxr-narrator` | Audience-tailored reports | "Generate a PM report" |
| `uxr-debriefer` | Stakeholder summaries | "Summarize for leadership" |
| `uxr-contradiction` | Find conflicts in data | "What contradictions exist?" |
| `uxr-ontology` | Tagging taxonomy | "Create an annotation ontology" |
| `uxr-annotator` | Mark up transcripts | "Annotate for video clips" |
| `uxr-delta` | Track run-to-run changes | "What changed since last time?" |
| `uxr-cohort-delta` | Compare subgroups | "How does wave 2 differ?" |
| `uxr-terminology` | Terminology friction | "Where were users confused?" |
| `uxr-labeler` | Qualitative coding | "Build a codebook" |

### 19 MCP Tools

See `docs/COMMANDS.md` for the complete reference.

---

## Documentation

| Document | Contents |
|----------|----------|
| `docs/COMMANDS.md` | Complete tool and skill reference |
| `docs/ARCHITECTURE.md` | Technical design and data flow |
| `docs/ADDING-SKILLS.md` | Guide for creating new skills |
| `skills/README.md` | Skills directory overview |

---

## Updating

```bash
cd hogwild-uxr
git pull
uv sync
# Re-copy skills if any changed:
xcopy skills\uxr-* "%USERPROFILE%\.copilot\skills\" /E /I /Y
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Skills don't appear in `/skills list` | Verify files are in `~/.copilot/skills/uxr-*/SKILL.md` and restart CLI |
| MCP server not loading | Check `~/.copilot/mcp-config.json` has correct `uv` path and `--project` path |
| `uv` not found | Use full path to `uv.exe` in mcp-config.json |
| Tool confirmation prompts | Use `copilot --allow-all-tools` or `/allow-all` |
| Transcript parse fails | Verify .docx uses Speaker/Timestamp/Utterance format (no tables) |

---

## License

MIT
