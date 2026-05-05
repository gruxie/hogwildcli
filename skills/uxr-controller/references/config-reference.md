# Configuration Reference

## research_config.yaml

```yaml
study:
  title: "App Modernization UX Research"
  description: "Evaluative study of AI-assisted application modernization tooling"
  method: "Semi-structured interview"

research:
  question: "What are the organizational factors that drive or hinder AI adoption in app modernization?"
  hypotheses:
    - "H1: Top-down — driven by management incentives"
    - "H2: Bottom-up — driven by ICs own motivations"
    - "H3: Social proof — seeing others having success"

participants:
  - id: P1
    file: "Meeting_-_P1_Devon.docx"
    interviewee_speaker: "Smith, Devon P"
    alias: "Devon"
  - id: P2
    file: "Meeting_-_P2_Taylor.docx"
    interviewee_speaker: "Johnson, Taylor M"
    alias: "Taylor"

transcripts_dir: "./transcripts"

output:
  dir: "./output"
  max_iterations: 3
```

## Field reference

| Field | Required | Description |
|---|---|---|
| `study.title` | Yes | Study name |
| `study.description` | No | Brief description |
| `study.method` | No | Research method |
| `research.question` | Yes | Primary research question |
| `research.hypotheses` | Yes | List of hypothesis strings |
| `participants` | Yes | List of participant objects |
| `participants[].id` | Yes | Unique participant ID (e.g., P1) |
| `participants[].file` | Yes | Transcript filename in transcripts_dir |
| `participants[].interviewee_speaker` | Yes | Speaker name as it appears in transcript |
| `participants[].alias` | No | Display name for reports |
| `transcripts_dir` | No | Path to transcripts (default: ./transcripts) |
| `output.dir` | No | Output directory (default: ./output) |
| `output.max_iterations` | No | Revelation loop cap (default: 3) |

## Tuning behavior

### More insights (comprehensive)
Add to your prompt: "Extract every substantive claim, even at low confidence."

### Fewer insights (precise)
Add to your prompt: "Only extract insights where evidence is clear and unambiguous."

### Stricter evaluation
Add to your prompt: "Apply strict grounding — every word must trace to the participant's utterance."

### Lenient evaluation
Add to your prompt: "Prefer flag over fail for insights where inference is tight and evidence is solid."
