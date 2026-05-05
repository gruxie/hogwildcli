"""Config loader and validator for research_config.yaml."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from .errors import config_invalid
from .sandbox import resolve_safe


REQUIRED_FIELDS = {
    "study": ["title"],
    "research": ["question", "hypotheses"],
    "participants": None,
}


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load and validate research_config.yaml."""
    config_path = Path(config_path).resolve()

    if not config_path.exists():
        return config_invalid(
            f"Config file not found: {config_path}",
            {"path": str(config_path)},
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = f.read()
            config = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        return config_invalid(f"YAML parse error: {e}")

    if not isinstance(config, dict):
        return config_invalid("Config must be a YAML mapping")

    errors: list[str] = []

    study = config.get("study")
    if not isinstance(study, dict):
        errors.append("Missing 'study' section")
    elif not study.get("title"):
        errors.append("Missing 'study.title'")

    research = config.get("research")
    if not isinstance(research, dict):
        errors.append("Missing 'research' section")
    else:
        if not research.get("question"):
            errors.append("Missing 'research.question'")
        hypotheses = research.get("hypotheses")
        if not isinstance(hypotheses, list) or len(hypotheses) == 0:
            errors.append("'research.hypotheses' must be a non-empty list")

    participants = config.get("participants")
    if not isinstance(participants, list) or len(participants) == 0:
        errors.append("'participants' must be a non-empty list")
    else:
        seen_ids: set[str] = set()
        for i, p in enumerate(participants):
            if not isinstance(p, dict):
                errors.append(f"participants[{i}] must be a mapping")
                continue
            pid = p.get("id")
            if not pid:
                errors.append(f"participants[{i}] missing 'id'")
            elif pid in seen_ids:
                errors.append(f"Duplicate participant id: '{pid}'")
            else:
                seen_ids.add(pid)
            if not p.get("file"):
                errors.append(f"participants[{i}] ('{pid}') missing 'file'")
            if not p.get("interviewee_speaker"):
                errors.append(f"participants[{i}] ('{pid}') missing 'interviewee_speaker'")

    if errors:
        return config_invalid("Config validation failed", {"issues": errors})

    config_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    config["_config_hash"] = config_hash
    config["_config_path"] = str(config_path)

    config.setdefault("transcripts_dir", "./transcripts")
    output = config.setdefault("output", {})
    output.setdefault("dir", "./output")
    output.setdefault("max_iterations", 3)

    return config


def get_project_dir(config: dict[str, Any]) -> Path:
    return Path(config["_config_path"]).parent


def get_transcripts_dir(config: dict[str, Any]) -> Path:
    return resolve_safe(config["transcripts_dir"], get_project_dir(config))


def get_output_dir(config: dict[str, Any]) -> Path:
    return resolve_safe(config["output"]["dir"], get_project_dir(config))


def get_participant(config: dict[str, Any], participant_id: str) -> dict[str, Any] | None:
    for p in config.get("participants", []):
        if p.get("id") == participant_id:
            return p
    return None


def get_max_iterations(config: dict[str, Any]) -> int:
    return config.get("output", {}).get("max_iterations", 3)
