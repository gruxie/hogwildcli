"""Labeling I/O tools — dictionary management and label application."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import load_config, get_output_dir
from ..errors import artifact_not_found, validation_error


def manage_dictionary(
    config_path: str,
    action: str = "get",
    labels: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Manage the labeling dictionary. Actions: get, set, merge."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=True)
    dict_path = output_dir / "labeling_dictionary.json"

    if action == "get":
        if not dict_path.exists():
            return {"labels": [], "count": 0}
        data = json.loads(dict_path.read_text(encoding="utf-8"))
        return {"labels": data, "count": len(data)}

    elif action == "set":
        if not labels or not isinstance(labels, list):
            return validation_error("labels must be a non-empty list for 'set'")
        dict_path.write_text(
            json.dumps(labels, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return {"status": "saved", "count": len(labels)}

    elif action == "merge":
        if not labels or not isinstance(labels, list):
            return validation_error("labels must be a non-empty list for 'merge'")
        existing: list[dict[str, Any]] = []
        if dict_path.exists():
            existing = json.loads(dict_path.read_text(encoding="utf-8"))
        existing_ids = {l.get("id") for l in existing}
        new_labels = [l for l in labels if l.get("id") not in existing_ids]
        existing.extend(new_labels)
        dict_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return {"status": "merged", "added": len(new_labels), "total": len(existing)}

    return validation_error(f"Unknown action: {action}")


def apply_labels(
    config_path: str,
    participant_id: str,
    labeled_insights: list[dict[str, Any]],
) -> dict[str, Any]:
    """Save labeled insights for a participant."""
    config = load_config(config_path)
    if "error" in config:
        return config

    if not labeled_insights:
        return validation_error("labeled_insights must be non-empty")

    output_dir = get_output_dir(config)
    output_dir.mkdir(parents=True, exist_ok=True)

    labels_path = output_dir / f"{participant_id}_labels.json"
    labels_path.write_text(
        json.dumps(labeled_insights, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return {
        "participant_id": participant_id,
        "status": "saved",
        "label_count": len(labeled_insights),
        "path": str(labels_path),
    }


def get_labels(config_path: str, participant_id: str) -> dict[str, Any]:
    """Get labels for a participant."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    labels_path = output_dir / f"{participant_id}_labels.json"

    if not labels_path.exists():
        return {"participant_id": participant_id, "labels": []}

    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    return {"participant_id": participant_id, "labels": labels}
