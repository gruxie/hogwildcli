"""Structured error handling for MCP tool responses.

All tools return structured JSON. Errors are returned as tool results,
not raised as exceptions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


STATE_VIOLATION = -32001
CONFIG_INVALID = -32002
ARTIFACT_NOT_FOUND = -32003
VALIDATION_ERROR = -32004
GATE_NOT_MET = -32005
SANDBOX_VIOLATION = -32007


@dataclass
class MCPError:
    """Structured MCP error envelope."""

    code: int
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "data": self.data,
            }
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def state_violation(
    current_state: str,
    required_state: str | list[str],
    suggested_tool: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "current_state": current_state,
        "required_state": required_state,
    }
    if suggested_tool:
        data["suggested_tool"] = suggested_tool
    return MCPError(
        code=STATE_VIOLATION,
        message=f"Tool requires state '{required_state}' but participant is in '{current_state}'",
        data=data,
    ).to_dict()


def config_invalid(message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return MCPError(code=CONFIG_INVALID, message=message, data=details or {}).to_dict()


def artifact_not_found(path: str, context: str = "") -> dict[str, Any]:
    return MCPError(
        code=ARTIFACT_NOT_FOUND,
        message=f"Required artifact not found: {path}",
        data={"path": path, "context": context},
    ).to_dict()


def validation_error(message: str, issues: list[str] | None = None) -> dict[str, Any]:
    return MCPError(
        code=VALIDATION_ERROR, message=message, data={"issues": issues or []}
    ).to_dict()


def gate_not_met(message: str, requirement: str = "") -> dict[str, Any]:
    return MCPError(
        code=GATE_NOT_MET, message=message, data={"requirement": requirement}
    ).to_dict()


def sandbox_violation(path: str, project_dir: str) -> dict[str, Any]:
    return MCPError(
        code=SANDBOX_VIOLATION,
        message="Path resolves outside project directory",
        data={"attempted_path": path, "project_dir": project_dir},
    ).to_dict()
