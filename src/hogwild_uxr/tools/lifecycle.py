"""Lifecycle tools — project init, config, status."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from ..config import load_config, get_output_dir, get_project_dir, get_transcripts_dir, get_participant
from ..errors import validation_error, config_invalid
from ..sandbox import resolve_safe
from ..state import PipelineState


def detect_speakers(docx_path: str) -> dict[str, Any]:
    """Scan a .docx transcript and return detected speaker names with turn counts."""
    import docx

    path = Path(docx_path)
    if not path.exists():
        return {"error": {"message": f"File not found: {docx_path}"}}

    try:
        doc = docx.Document(str(path))
    except Exception as e:
        return {"error": {"message": f"Cannot open docx: {e}"}}

    timestamp_re = re.compile(r"^\d{1,2}:\d{2}\s*[-\u2013]\s*\d{1,2}:\d{2}$")
    speakers: dict[str, int] = {}
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    i = 0
    while i < len(paragraphs) - 1:
        if i + 1 < len(paragraphs) and timestamp_re.match(paragraphs[i + 1]):
            speaker = paragraphs[i]
            speakers[speaker] = speakers.get(speaker, 0) + 1
            i += 3
        else:
            i += 1

    return {
        "file": path.name,
        "speakers": speakers,
        "total_turns": sum(speakers.values()),
    }


def scaffold_config(
    project_dir: str,
    title: str,
    description: str,
    research_question: str,
    hypotheses: list[str],
    participants: list[dict[str, str]],
    method: str = "Semi-structured interview",
    max_iterations: int = 3,
) -> dict[str, Any]:
    """Create a research_config.yaml for a new study."""
    project_path = Path(project_dir).resolve()
    project_path.mkdir(parents=True, exist_ok=True)

    config = {
        "study": {
            "title": title,
            "description": description,
            "method": method,
        },
        "research": {
            "question": research_question,
            "hypotheses": hypotheses,
        },
        "participants": participants,
        "transcripts_dir": "./transcripts",
        "output": {
            "dir": "./output",
            "max_iterations": max_iterations,
        },
    }

    config_path = project_path / "research_config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    (project_path / "transcripts").mkdir(exist_ok=True)
    (project_path / "output").mkdir(exist_ok=True)

    return {"config_path": str(config_path), "status": "created"}


def load_config_tool(config_path: str) -> dict[str, Any]:
    """Load and validate config."""
    return load_config(config_path)


def preflight_check(config_path: str) -> dict[str, Any]:
    """Validate project readiness."""
    config = load_config(config_path)
    if "error" in config:
        return config

    issues: list[str] = []
    project_dir = get_project_dir(config)
    transcripts_dir = get_transcripts_dir(config)
    output_dir = get_output_dir(config)

    if not transcripts_dir.exists():
        issues.append(f"Transcripts dir not found: {transcripts_dir}")

    for p in config.get("participants", []):
        f = transcripts_dir / p["file"]
        if not f.exists():
            issues.append(f"Transcript not found for {p['id']}: {f}")

    output_dir.mkdir(parents=True, exist_ok=True)

    if issues:
        return {"ready": False, "issues": issues}
    return {"ready": True, "participants": len(config["participants"])}


def get_project_status(config_path: str) -> dict[str, Any]:
    """Return per-participant pipeline state summary."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    state = PipelineState(output_dir)
    all_states = state.get_all_states()

    participants_status = []
    for p in config.get("participants", []):
        pid = p["id"]
        pstate = all_states.get(pid, {})
        participants_status.append({
            "id": pid,
            "state": pstate.get("state", "not_started"),
            "iteration": pstate.get("iteration", 0),
            "locked_count": pstate.get("locked_count", 0),
        })

    return {"participants": participants_status}
