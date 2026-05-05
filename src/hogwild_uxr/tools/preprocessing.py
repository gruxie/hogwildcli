"""Preprocessing tools — deterministic transcript conversion."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..config import load_config, get_output_dir, get_transcripts_dir, get_participant
from ..errors import artifact_not_found, validation_error
from ..sandbox import ensure_parent_exists
from ..state import PipelineState


def parse_transcript(config_path: str, participant_id: str) -> dict[str, Any]:
    """Convert .docx transcript to .md + _turns.json. Transitions state to preprocessed."""
    import docx

    config = load_config(config_path)
    if "error" in config:
        return config

    participant = get_participant(config, participant_id)
    if not participant:
        return validation_error(f"Participant '{participant_id}' not found")

    transcripts_dir = get_transcripts_dir(config)
    output_dir = get_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=True)

    docx_path = transcripts_dir / participant["file"]
    if not docx_path.exists():
        return artifact_not_found(str(docx_path), "transcript file")

    # Parse .docx
    try:
        doc = docx.Document(str(docx_path))
    except Exception as e:
        return validation_error(f"Cannot open docx: {e}")

    timestamp_re = re.compile(r"^\d{1,2}:\d{2}\s*[-\u2013]\s*\d{1,2}:\d{2}$")
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    turns: list[dict[str, str]] = []
    i = 0
    while i < len(paragraphs):
        if i + 2 < len(paragraphs) and timestamp_re.match(paragraphs[i + 1]):
            speaker = paragraphs[i]
            timestamp = paragraphs[i + 1]
            utterance = paragraphs[i + 2]
            turns.append({
                "speaker": speaker,
                "timestamp": timestamp,
                "utterance": utterance,
            })
            i += 3
        else:
            # Continuation of previous turn or noise
            if turns:
                turns[-1]["utterance"] += " " + paragraphs[i]
            i += 1

    if not turns:
        return validation_error("No turns detected in transcript")

    stem = docx_path.stem

    # Write .md
    md_lines = [f"# Transcript: {stem}\n"]
    for turn in turns:
        md_lines.append(f"**{turn['speaker']}** `[{turn['timestamp']}]`")
        md_lines.append(f"{turn['utterance']}\n")

    md_path = output_dir / f"{stem}_converted.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # Write _turns.json
    turns_data = {"source": participant["file"], "turns": turns}
    turns_path = output_dir / f"{stem}_turns.json"
    turns_path.write_text(json.dumps(turns_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Transition state
    state = PipelineState(output_dir)
    error = state.transition(participant_id, "preprocessed")
    if error:
        return error

    # Collect speaker stats
    speakers: dict[str, int] = {}
    for t in turns:
        speakers[t["speaker"]] = speakers.get(t["speaker"], 0) + 1

    return {
        "participant_id": participant_id,
        "state": "preprocessed",
        "md_path": str(md_path),
        "turns_path": str(turns_path),
        "total_turns": len(turns),
        "speakers": speakers,
    }
