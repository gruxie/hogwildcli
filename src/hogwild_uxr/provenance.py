"""Provenance tracking for pipeline artifacts."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__


def compute_file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_string_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_provenance(
    config_hash: str,
    participant_id: str,
    iterations_used: int,
    skill_name: str = "",
) -> dict[str, Any]:
    """Build a provenance record for a finalized artifact."""
    return {
        "provenance": {
            "config_hash": config_hash,
            "participant_id": participant_id,
            "iterations_used": iterations_used,
            "skill_name": skill_name,
            "server_version": __version__,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    }
