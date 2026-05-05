"""Artifact I/O tools — save/list/get generic artifacts (reports, narratives, debriefs)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import load_config, get_output_dir
from ..errors import artifact_not_found, validation_error
from ..sandbox import ensure_parent_exists


def save_artifact(
    config_path: str,
    filename: str,
    content: str,
    artifact_type: str = "report",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Save a generated artifact (report, narrative, debrief, etc.) to the output directory."""
    config = load_config(config_path)
    if "error" in config:
        return config

    if not filename:
        return validation_error("filename is required")
    if not content:
        return validation_error("content is required")

    output_dir = get_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=True)

    artifact_path = output_dir / filename
    ensure_parent_exists(artifact_path)
    artifact_path.write_text(content, encoding="utf-8")

    # Write metadata sidecar
    meta = {
        "artifact_type": artifact_type,
        "filename": filename,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "size_bytes": len(content.encode("utf-8")),
    }
    if metadata:
        meta.update(metadata)

    meta_path = output_dir / f"{filename}.meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return {"status": "saved", "path": str(artifact_path), "artifact_type": artifact_type}


def list_artifacts(config_path: str, artifact_type: str | None = None) -> dict[str, Any]:
    """List all generated artifacts in the output directory."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    if not output_dir.exists():
        return {"artifacts": []}

    artifacts = []
    for meta_file in output_dir.glob("*.meta.json"):
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            if artifact_type and meta.get("artifact_type") != artifact_type:
                continue
            artifacts.append(meta)
        except (json.JSONDecodeError, OSError):
            continue

    return {"artifacts": artifacts, "count": len(artifacts)}


def get_artifact(config_path: str, filename: str) -> dict[str, Any]:
    """Get the content of a specific artifact."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    artifact_path = output_dir / filename

    if not artifact_path.exists():
        return artifact_not_found(str(artifact_path), "artifact")

    content = artifact_path.read_text(encoding="utf-8")
    return {"filename": filename, "content": content}
