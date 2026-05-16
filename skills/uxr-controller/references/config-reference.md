# Configuration Reference

## research_config.yaml

```yaml
study:
  title: "App Modernization UX Research"
  description: "Evaluative study of AI-assisted application modernization tooling"
  method: "Semi-structured interview"
  motivations: >
    Why this study was approved — context, history, or stakeholder need.
  goals: >
    Outcomes, learnings, and work products the researcher hopes to accomplish.
  intended_impacts: >
    How the research will affect the product, customer experience, or other outcomes.

research:
  question: "What are the organizational factors that drive or hinder AI adoption in app modernization?"
  hypotheses:
    - "H1: Top-down — driven by management incentives"
    - "H2: Bottom-up — driven by ICs own motivations"
    - "H3: Social proof — seeing others having success"

grounding:
  additional_context: ""   # Optional researcher note — not written by the system

participants:
  - id: P1
    file: "Meeting_-_P1_Devon.docx"
    interviewee_speaker: "Smith, Devon P"
    alias: "Devon"           # First name only — used in quote attribution
    role: "VP of Product"    # Used in quote attribution: "Quote." — Devon, VP of Product at Acme
    company: "Acme Corp"     # Used in quote attribution and learnings tagging
    tags: "seg_1, enterprise"
    cohorts: "[wave1]"
    profile: ""              # AI-populated during analysis
    memo: ""                 # Optional researcher note about this participant
  - id: P2
    file: "Meeting_-_P2_Taylor.docx"
    interviewee_speaker: "Johnson, Taylor M"
    alias: "Taylor"
    role: "Product Manager"
    company: "Beta Inc"
    tags: "seg_2"
    cohorts: "[wave1]"

transcripts_dir: "./transcripts"

output:
  dir: "./output"
  max_iterations: 3
  generate_cohort_delta: false
  cohort_delta_participants: []
  generate_terminology_audit: false
```

## Field reference

### study

| Field | Required | Description |
|---|---|---|
| `study.title` | Yes | Study name — used in report filenames |
| `study.description` | No | Brief description |
| `study.method` | No | Research method (e.g., "Semi-structured interview") |
| `study.motivations` | No | Why this study was approved — default grounding context |
| `study.goals` | No | Outcomes and work products — default grounding context |
| `study.intended_impacts` | No | How findings will be applied — default grounding context |

### research

| Field | Required | Description |
|---|---|---|
| `research.question` | Yes | Primary research question — guides extraction |
| `research.hypotheses` | Yes | List of hypothesis strings — attention scaffolds |

### grounding

| Field | Required | Description |
|---|---|---|
| `grounding.additional_context` | No | Researcher-authored scope note; read during Mode 0 |

> Grounding run history is tracked in `./grounding/grounding_log.json` — not in this file.

### participants

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Unique participant ID (e.g., P1) |
| `file` | Yes | Transcript filename in `transcripts_dir` |
| `interviewee_speaker` | Yes | Speaker name exactly as it appears in the transcript |
| `alias` | No | First name only — used in quote attribution (never last name) |
| `role` | No | Participant's role/title — used in quote attribution |
| `company` | No | Participant's company — used in attribution and learnings tagging |
| `tags` | No | Comma-separated segment labels for filtering analysis |
| `cohorts` | No | Bracket-wrapped group labels for cohort comparison |
| `profile` | No | AI-populated participant summary |
| `memo` | No | Researcher-authored note about this participant |

### output

| Field | Required | Description |
|---|---|---|
| `output.dir` | No | Output directory (default: `./output`) |
| `output.max_iterations` | No | Revelation loop cap (default: 3) |
| `output.generate_cohort_delta` | No | Run cohort delta after synthesis |
| `output.cohort_delta_participants` | No | Participant IDs to compare against full synthesis |
| `output.generate_terminology_audit` | No | Run terminology audit after synthesis |

## Grounding context fields

`study.motivations`, `study.goals`, and `study.intended_impacts` are read by `uxr-grounding` (Mode 0) alongside `research.question` and `research.hypotheses` to build the focus memo. Together these fields are the **default grounding** — they shape analysis before the researcher has added any optional grounding artifacts.

## Participant tags and cohorts

- **`tags`** — free-form labels, comma-separated. Use to group participants by any attribute. Example: `"enterprise, seg_1, high_tenure"`
- **`cohorts`** — bracket-wrapped categorical labels. Use for defined study waves or segments. Example: `"[wave1],[pilot]"`

Use these fields to filter synthesis: "Synthesize only seg_1 participants" or "Compare wave1 and wave2."

## Tuning behavior

### More insights (comprehensive)
Add to your prompt: "Extract every substantive claim, even at low confidence."

### Fewer insights (precise)
Add to your prompt: "Only extract insights where evidence is clear and unambiguous."

### Stricter evaluation
Add to your prompt: "Apply strict grounding — every word must trace to the participant's utterance."

### Lenient evaluation
Add to your prompt: "Prefer flag over fail for insights where inference is tight and evidence is solid."
