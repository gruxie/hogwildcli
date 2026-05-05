"""Smoke tests for Hogwild UXR MCP server."""

import json
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """All modules import without error."""
    from hogwild_uxr import __version__
    from hogwild_uxr.state import PipelineState, STATES, TRANSITIONS
    from hogwild_uxr.config import load_config
    from hogwild_uxr.errors import MCPError, state_violation, validation_error
    from hogwild_uxr.sandbox import resolve_safe
    from hogwild_uxr.provenance import build_provenance
    from hogwild_uxr.tools import lifecycle, preprocessing, state_io, synthesis_io, artifact_io, labeling_io
    assert __version__ == "4.0.0"
    print("  [PASS] All imports OK")


def test_state_machine():
    """State transitions work correctly."""
    from hogwild_uxr.state import PipelineState

    with tempfile.TemporaryDirectory() as tmp:
        state = PipelineState(Path(tmp))

        assert state.get_state("P1") == "not_started"

        # Valid transition
        err = state.transition("P1", "preprocessed")
        assert err is None
        assert state.get_state("P1") == "preprocessed"

        # Invalid transition
        err = state.transition("P1", "finalized")
        assert err is not None
        assert "error" in err

        # Continue valid path
        state.transition("P1", "extracting")
        assert state.get_iteration("P1") == 1

        state.transition("P1", "evaluating")
        state.transition("P1", "finalized")
        assert state.get_state("P1") == "finalized"

    print("  [PASS] State machine transitions")


def test_config_validation():
    """Config loader validates correctly."""
    from hogwild_uxr.config import load_config

    # Non-existent file
    result = load_config("/nonexistent/path.yaml")
    assert "error" in result

    # Valid config
    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "research_config.yaml"
        config_path.write_text("""
study:
  title: "Test Study"
research:
  question: "What happens?"
  hypotheses:
    - "H1: Something"
participants:
  - id: P1
    file: "test.docx"
    interviewee_speaker: "Test Person"
""")
        result = load_config(str(config_path))
        assert "error" not in result
        assert result["_config_hash"]
        assert result["study"]["title"] == "Test Study"

    print("  [PASS] Config validation")


def test_sandbox():
    """Path sandboxing prevents escape."""
    from hogwild_uxr.sandbox import resolve_safe

    with tempfile.TemporaryDirectory() as tmp:
        # Valid path
        result = resolve_safe("output/file.json", tmp)
        assert str(tmp) in str(result)

        # Escape attempt
        try:
            resolve_safe("../../etc/passwd", tmp)
            assert False, "Should have raised"
        except ValueError:
            pass

    print("  [PASS] Sandbox enforcement")


def test_server_registration():
    """FastMCP server registers all tools."""
    from hogwild_uxr.server import mcp

    # Get registered tools
    tools = mcp._tool_manager._tools
    tool_names = set(tools.keys())

    expected = {
        "detect_speakers", "scaffold_config", "load_config", "preflight_check",
        "get_project_status", "parse_transcript", "start_participant",
        "submit_insights", "submit_evaluation", "get_insights",
        "get_revelation_context", "reset_participant", "submit_synthesis",
        "get_synthesis", "save_artifact", "list_artifacts", "get_artifact",
        "manage_dictionary", "apply_labels", "get_labels",
    }

    missing = expected - tool_names
    assert not missing, f"Missing tools: {missing}"
    print(f"  [PASS] Server registers {len(tool_names)} tools (expected {len(expected)})")


def test_lifecycle_tools():
    """Lifecycle tools work with valid config."""
    from hogwild_uxr.tools import lifecycle

    with tempfile.TemporaryDirectory() as tmp:
        # Scaffold config
        result = lifecycle.scaffold_config(
            project_dir=tmp,
            title="Test",
            description="Test study",
            research_question="What?",
            hypotheses=["H1: yes"],
            participants=[{"id": "P1", "file": "t.docx", "interviewee_speaker": "Test"}],
        )
        assert result["status"] == "created"

        # Load config
        result = lifecycle.load_config_tool(result["config_path"])
        assert "error" not in result

        # Preflight (will fail since no transcript exists)
        result = lifecycle.preflight_check(result["_config_path"])
        assert result["ready"] is False

    print("  [PASS] Lifecycle tools")


def test_artifact_io():
    """Artifact save/list/get cycle works."""
    from hogwild_uxr.tools import artifact_io, lifecycle

    with tempfile.TemporaryDirectory() as tmp:
        # Setup config
        result = lifecycle.scaffold_config(
            project_dir=tmp, title="T", description="", research_question="?",
            hypotheses=["H1"], participants=[{"id": "P1", "file": "t.docx", "interviewee_speaker": "X"}],
        )
        config_path = result["config_path"]

        # Save
        save_result = artifact_io.save_artifact(config_path, "test_report.md", "# Report\nContent here", "report")
        assert save_result["status"] == "saved"

        # List
        list_result = artifact_io.list_artifacts(config_path)
        assert list_result["count"] == 1

        # Get
        get_result = artifact_io.get_artifact(config_path, "test_report.md")
        assert "# Report" in get_result["content"]

    print("  [PASS] Artifact I/O cycle")


def test_labeling_io():
    """Labeling dictionary and label application works."""
    from hogwild_uxr.tools import labeling_io, lifecycle

    with tempfile.TemporaryDirectory() as tmp:
        result = lifecycle.scaffold_config(
            project_dir=tmp, title="T", description="", research_question="?",
            hypotheses=["H1"], participants=[{"id": "P1", "file": "t.docx", "interviewee_speaker": "X"}],
        )
        config_path = result["config_path"]

        # Set dictionary
        labels = [{"id": "L1", "label": "trust", "domain": "Governance"}]
        r = labeling_io.manage_dictionary(config_path, "set", labels)
        assert r["count"] == 1

        # Get dictionary
        r = labeling_io.manage_dictionary(config_path, "get")
        assert r["count"] == 1

        # Merge
        new_labels = [{"id": "L2", "label": "cost", "domain": "Business"}]
        r = labeling_io.manage_dictionary(config_path, "merge", new_labels)
        assert r["total"] == 2

    print("  [PASS] Labeling I/O")


if __name__ == "__main__":
    print("Hogwild UXR v4 — Smoke Tests")
    print("=" * 40)
    test_imports()
    test_state_machine()
    test_config_validation()
    test_sandbox()
    test_server_registration()
    test_lifecycle_tools()
    test_artifact_io()
    test_labeling_io()
    print("=" * 40)
    print(f"All tests passed!")
