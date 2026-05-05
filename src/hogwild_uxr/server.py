"""Hogwild UXR — Slim Orchestrator MCP Server.

This server provides state management and I/O tools only.
All reasoning is handled by Copilot CLI skills (SKILL.md files).

Transport: stdio
Command: uv run hogwild-uxr
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .tools import lifecycle, preprocessing, state_io, synthesis_io, artifact_io, labeling_io

mcp = FastMCP("hogwild-uxr")


# ─── Lifecycle Tools ───────────────────────────────────────────────────────────


@mcp.tool()
def detect_speakers(docx_path: str) -> str:
    """Scan a .docx transcript and return detected speaker names with turn counts."""
    return json.dumps(lifecycle.detect_speakers(docx_path), indent=2)


@mcp.tool()
def scaffold_config(
    project_dir: str,
    title: str,
    description: str,
    research_question: str,
    hypotheses: list[str],
    participants: list[dict[str, str]],
    method: str = "Semi-structured interview",
    max_iterations: int = 3,
) -> str:
    """Create a research_config.yaml for a new study project."""
    return json.dumps(
        lifecycle.scaffold_config(
            project_dir, title, description, research_question,
            hypotheses, participants, method, max_iterations,
        ),
        indent=2,
    )


@mcp.tool()
def load_config(config_path: str) -> str:
    """Load and validate research_config.yaml. Returns full config as JSON."""
    return json.dumps(lifecycle.load_config_tool(config_path), indent=2)


@mcp.tool()
def preflight_check(config_path: str) -> str:
    """Validate project readiness: transcripts exist, output dir writable."""
    return json.dumps(lifecycle.preflight_check(config_path), indent=2)


@mcp.tool()
def get_project_status(config_path: str) -> str:
    """Return per-participant pipeline state and overall project summary."""
    return json.dumps(lifecycle.get_project_status(config_path), indent=2)


# ─── Preprocessing Tools ──────────────────────────────────────────────────────


@mcp.tool()
def parse_transcript(config_path: str, participant_id: str) -> str:
    """Convert .docx transcript to .md + _turns.json. Deterministic, no LLM needed."""
    return json.dumps(preprocessing.parse_transcript(config_path, participant_id), indent=2)


# ─── State I/O Tools ──────────────────────────────────────────────────────────


@mcp.tool()
def start_participant(config_path: str, participant_id: str) -> str:
    """Initialize extraction loop for a participant. Requires 'preprocessed' state."""
    return json.dumps(state_io.start_participant(config_path, participant_id), indent=2)


@mcp.tool()
def submit_insights(
    config_path: str, participant_id: str, insights: list[dict[str, Any]]
) -> str:
    """Submit extracted insights JSON. Validates, persists, transitions to 'evaluating'."""
    return json.dumps(
        state_io.submit_insights(config_path, participant_id, insights), indent=2
    )


@mcp.tool()
def submit_evaluation(
    config_path: str, participant_id: str, evaluation: dict[str, Any]
) -> str:
    """Submit evaluation results. Locks passing insights, determines revelation or finalization."""
    return json.dumps(
        state_io.submit_evaluation(config_path, participant_id, evaluation), indent=2
    )


@mcp.tool()
def get_insights(config_path: str, participant_id: str) -> str:
    """Get current insights for a participant (final or latest iteration)."""
    return json.dumps(state_io.get_insights(config_path, participant_id), indent=2)


@mcp.tool()
def get_revelation_context(config_path: str, participant_id: str) -> str:
    """Get failed issues + transcript for re-extraction in a revelation loop."""
    return json.dumps(
        state_io.get_revelation_context(config_path, participant_id), indent=2
    )


@mcp.tool()
def reset_participant(config_path: str, participant_id: str) -> str:
    """Hard reset a participant to not_started state."""
    return json.dumps(state_io.reset_participant(config_path, participant_id), indent=2)


# ─── Synthesis I/O Tools ──────────────────────────────────────────────────────


@mcp.tool()
def submit_synthesis(config_path: str, synthesis: dict[str, Any]) -> str:
    """Submit cross-participant synthesis data."""
    return json.dumps(synthesis_io.submit_synthesis(config_path, synthesis), indent=2)


@mcp.tool()
def get_synthesis(config_path: str) -> str:
    """Get the cross-participant synthesis data."""
    return json.dumps(synthesis_io.get_synthesis(config_path), indent=2)


# ─── Artifact I/O Tools ──────────────────────────────────────────────────────


@mcp.tool()
def save_artifact(
    config_path: str,
    filename: str,
    content: str,
    artifact_type: str = "report",
    metadata: dict[str, Any] | None = None,
) -> str:
    """Save a generated artifact (report, narrative, debrief) to output directory."""
    return json.dumps(
        artifact_io.save_artifact(config_path, filename, content, artifact_type, metadata),
        indent=2,
    )


@mcp.tool()
def list_artifacts(config_path: str, artifact_type: str | None = None) -> str:
    """List all generated artifacts in the output directory."""
    return json.dumps(artifact_io.list_artifacts(config_path, artifact_type), indent=2)


@mcp.tool()
def get_artifact(config_path: str, filename: str) -> str:
    """Get the content of a specific artifact."""
    return json.dumps(artifact_io.get_artifact(config_path, filename), indent=2)


# ─── Labeling I/O Tools ──────────────────────────────────────────────────────


@mcp.tool()
def manage_dictionary(
    config_path: str, action: str = "get", labels: list[dict[str, Any]] | None = None
) -> str:
    """Manage the labeling dictionary. Actions: get, set, merge."""
    return json.dumps(
        labeling_io.manage_dictionary(config_path, action, labels), indent=2
    )


@mcp.tool()
def apply_labels(
    config_path: str, participant_id: str, labeled_insights: list[dict[str, Any]]
) -> str:
    """Save labeled insights for a participant."""
    return json.dumps(
        labeling_io.apply_labels(config_path, participant_id, labeled_insights), indent=2
    )


@mcp.tool()
def get_labels(config_path: str, participant_id: str) -> str:
    """Get applied labels for a participant."""
    return json.dumps(labeling_io.get_labels(config_path, participant_id), indent=2)


# ─── Entry Point ──────────────────────────────────────────────────────────────


def main():
    """Run the MCP server via stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
