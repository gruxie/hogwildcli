"""Pipeline state machine — enforces legal transitions at the tool boundary.

States:
    not_started -> preprocessed -> extracting -> evaluating ->
    in_revelation -> extracting (loop) OR finalized
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import state_violation

STATES = [
    "not_started",
    "preprocessed",
    "extracting",
    "evaluating",
    "in_revelation",
    "finalized",
]

TRANSITIONS: dict[str, list[str]] = {
    "not_started": ["preprocessed"],
    "preprocessed": ["extracting"],
    "extracting": ["evaluating"],
    "evaluating": ["in_revelation", "finalized"],
    "in_revelation": ["extracting"],
    "finalized": ["not_started"],
}

SUGGESTED_TOOLS: dict[str, str] = {
    "not_started": "parse_transcript",
    "preprocessed": "start_participant",
    "extracting": "submit_insights",
    "evaluating": "submit_evaluation or finalize_participant",
    "in_revelation": "submit_insights (re-extraction)",
    "finalized": "reset_participant (if re-running)",
}


class PipelineState:
    """Manages pipeline state for all participants in a project."""

    def __init__(self, output_dir: Path):
        self._state_file = output_dir / ".pipeline_state.json"
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self._state_file.exists():
            try:
                with open(self._state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("schema_version") == 1:
                    return data
            except (json.JSONDecodeError, KeyError):
                pass
        return {"schema_version": 1, "participants": {}}

    def _save(self) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def get_state(self, participant_id: str) -> str:
        entry = self._data["participants"].get(participant_id)
        if entry is None:
            return "not_started"
        return entry.get("state", "not_started")

    def get_iteration(self, participant_id: str) -> int:
        entry = self._data["participants"].get(participant_id, {})
        return entry.get("iteration", 0)

    def get_locked_count(self, participant_id: str) -> int:
        entry = self._data["participants"].get(participant_id, {})
        return entry.get("locked_count", 0)

    def set_locked_count(self, participant_id: str, count: int) -> None:
        if participant_id not in self._data["participants"]:
            self._data["participants"][participant_id] = {
                "state": "not_started", "iteration": 0, "locked_count": 0,
            }
        self._data["participants"][participant_id]["locked_count"] = count
        self._save()

    def transition(
        self, participant_id: str, to_state: str, increment_iteration: bool = False
    ) -> dict[str, Any] | None:
        current = self.get_state(participant_id)
        allowed = TRANSITIONS.get(current, [])
        if to_state not in allowed:
            return state_violation(
                current_state=current,
                required_state=allowed,
                suggested_tool=SUGGESTED_TOOLS.get(current),
            )

        if participant_id not in self._data["participants"]:
            self._data["participants"][participant_id] = {
                "state": "not_started", "iteration": 0, "locked_count": 0,
            }

        entry = self._data["participants"][participant_id]
        entry["state"] = to_state
        entry["last_transition"] = datetime.now(timezone.utc).isoformat()

        if increment_iteration:
            entry["iteration"] = entry.get("iteration", 0) + 1

        if to_state == "not_started":
            entry["iteration"] = 0
            entry["locked_count"] = 0

        if to_state == "extracting" and entry.get("iteration", 0) == 0:
            entry["iteration"] = 1

        self._save()
        return None

    def require_state(
        self, participant_id: str, required: str | list[str]
    ) -> dict[str, Any] | None:
        current = self.get_state(participant_id)
        if isinstance(required, str):
            required = [required]
        if current not in required:
            return state_violation(
                current_state=current,
                required_state=required,
                suggested_tool=SUGGESTED_TOOLS.get(current),
            )
        return None

    def get_all_states(self) -> dict[str, dict[str, Any]]:
        return self._data.get("participants", {})

    def reset(self, participant_id: str) -> None:
        self._data["participants"][participant_id] = {
            "state": "not_started",
            "iteration": 0,
            "locked_count": 0,
            "last_transition": datetime.now(timezone.utc).isoformat(),
        }
        self._save()
