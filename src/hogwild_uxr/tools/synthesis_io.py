"""Synthesis I/O tools — submit/get cross-participant synthesis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import load_config, get_output_dir
from ..errors import validation_error, artifact_not_found


def submit_synthesis(config_path: str, synthesis: dict[str, Any]) -> dict[str, Any]:
    """Submit cross-participant synthesis data. Validates and persists."""
    config = load_config(config_path)
    if "error" in config:
        return config

    if not synthesis or not isinstance(synthesis, dict):
        return validation_error("synthesis must be a non-empty object")

    if "hypothesis_buckets" not in synthesis:
        return validation_error("synthesis must include 'hypothesis_buckets'")

    output_dir = get_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=True)

    synth_path = output_dir / "synthesis.json"
    synth_path.write_text(
        json.dumps(synthesis, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return {
        "status": "saved",
        "path": str(synth_path),
        "buckets": len(synthesis.get("hypothesis_buckets", [])),
    }


def get_synthesis(config_path: str) -> dict[str, Any]:
    """Get the cross-participant synthesis data."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    synth_path = output_dir / "synthesis.json"

    if not synth_path.exists():
        return artifact_not_found(str(synth_path), "synthesis not yet generated")

    synthesis = json.loads(synth_path.read_text(encoding="utf-8"))
    return {"status": "found", "synthesis": synthesis}
