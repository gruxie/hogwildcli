"""State I/O tools — submit/get insights, lock, finalize, reset."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import load_config, get_output_dir, get_participant, get_max_iterations
from ..errors import artifact_not_found, validation_error
from ..provenance import build_provenance
from ..state import PipelineState


def _stem(config: dict[str, Any], participant_id: str) -> str:
    p = get_participant(config, participant_id)
    if p:
        return Path(p["file"]).stem
    return participant_id


def start_participant(config_path: str, participant_id: str) -> dict[str, Any]:
    """Initialize extraction loop. Requires 'preprocessed' state."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    state = PipelineState(output_dir)

    error = state.require_state(participant_id, "preprocessed")
    if error:
        return error

    transition_error = state.transition(participant_id, "extracting")
    if transition_error:
        return transition_error

    return {
        "participant_id": participant_id,
        "state": "extracting",
        "iteration": state.get_iteration(participant_id),
        "max_iterations": get_max_iterations(config),
    }


def submit_insights(
    config_path: str, participant_id: str, insights: list[dict[str, Any]]
) -> dict[str, Any]:
    """Submit extracted insights. Validates and persists. Transitions to 'evaluating'."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    state = PipelineState(output_dir)

    error = state.require_state(participant_id, ["extracting", "in_revelation"])
    if error:
        return error

    if not insights or not isinstance(insights, list):
        return validation_error("insights must be a non-empty list")

    # Basic validation
    issues: list[str] = []
    for i, ins in enumerate(insights):
        if not isinstance(ins, dict):
            issues.append(f"insights[{i}] must be an object")
            continue
        if not ins.get("claim"):
            issues.append(f"insights[{i}] missing 'claim'")
        if not ins.get("evidence"):
            issues.append(f"insights[{i}] missing 'evidence'")

    if issues:
        return validation_error("Insight validation failed", issues)

    # Merge with locked insights if this is a revelation re-run
    stem = _stem(config, participant_id)
    iteration = state.get_iteration(participant_id)
    locked_path = output_dir / f"{stem}_insights_locked.json"
    locked: list[dict[str, Any]] = []
    if locked_path.exists():
        locked = json.loads(locked_path.read_text(encoding="utf-8"))

    # Save current submission
    current_path = output_dir / f"{stem}_insights_iter{iteration}.json"
    current_path.write_text(
        json.dumps(insights, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Transition to evaluating
    transition_error = state.transition(participant_id, "evaluating")
    if transition_error:
        return transition_error

    return {
        "participant_id": participant_id,
        "state": "evaluating",
        "iteration": iteration,
        "insights_submitted": len(insights),
        "locked_count": len(locked),
        "saved_to": str(current_path),
    }


def submit_evaluation(
    config_path: str, participant_id: str, evaluation: dict[str, Any]
) -> dict[str, Any]:
    """Submit evaluation results. Locks passing insights. Determines next step."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    state = PipelineState(output_dir)

    error = state.require_state(participant_id, "evaluating")
    if error:
        return error

    summary = evaluation.get("evaluation_summary", {})
    results = evaluation.get("results", [])

    if not results:
        return validation_error("evaluation must include 'results' array")

    stem = _stem(config, participant_id)
    iteration = state.get_iteration(participant_id)
    max_iter = get_max_iterations(config)

    # Save evaluation
    eval_path = output_dir / f"{stem}_evaluation_iter{iteration}.json"
    eval_path.write_text(
        json.dumps(evaluation, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Lock passing insights
    locked_path = output_dir / f"{stem}_insights_locked.json"
    locked: list[dict[str, Any]] = []
    if locked_path.exists():
        locked = json.loads(locked_path.read_text(encoding="utf-8"))

    # Load current insights
    current_path = output_dir / f"{stem}_insights_iter{iteration}.json"
    current_insights: list[dict[str, Any]] = []
    if current_path.exists():
        current_insights = json.loads(current_path.read_text(encoding="utf-8"))

    # Lock passed insights
    passed_ids = {r["insight_id"] for r in results if r.get("status") == "pass"}
    newly_locked = [ins for ins in current_insights if ins.get("insight_id") in passed_ids]
    locked.extend(newly_locked)
    locked_path.write_text(
        json.dumps(locked, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    state.set_locked_count(participant_id, len(locked))

    # Determine next step
    recommend_revelation = summary.get("recommend_revelation", False)
    can_loop = iteration < max_iter

    if recommend_revelation and can_loop:
        # Go to revelation
        state.transition(participant_id, "in_revelation")
        state.transition(participant_id, "extracting", increment_iteration=True)
        return {
            "participant_id": participant_id,
            "state": "extracting",
            "action": "revelation_loop",
            "iteration": state.get_iteration(participant_id),
            "max_iterations": max_iter,
            "locked_count": len(locked),
            "failed_count": summary.get("failed", 0),
        }
    else:
        # Finalize
        state.transition(participant_id, "finalized")
        # Write final artifacts
        final_insights = locked.copy()
        # Add any flagged insights from current iteration
        flagged_ids = {r["insight_id"] for r in results if r.get("status") == "flag"}
        flagged = [ins for ins in current_insights if ins.get("insight_id") in flagged_ids]
        final_insights.extend(flagged)

        # Mark remaining failed as insufficient_evidence if max iterations reached
        if iteration >= max_iter:
            failed_ids = {r["insight_id"] for r in results if r.get("status") == "fail"}
            for ins in current_insights:
                if ins.get("insight_id") in failed_ids:
                    ins["status"] = "insufficient_evidence"
                    final_insights.append(ins)

        final_path = output_dir / f"{stem}_insights_final.json"
        final_path.write_text(
            json.dumps(final_insights, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        eval_final_path = output_dir / f"{stem}_evaluation_final.json"
        eval_final_path.write_text(
            json.dumps(evaluation, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        provenance = build_provenance(
            config_hash=config["_config_hash"],
            participant_id=participant_id,
            iterations_used=iteration,
            skill_name="uxr-evaluator",
        )
        prov_path = output_dir / f"{stem}_provenance.json"
        prov_path.write_text(
            json.dumps(provenance, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        return {
            "participant_id": participant_id,
            "state": "finalized",
            "action": "finalized",
            "total_insights": len(final_insights),
            "locked_count": len(locked),
            "iterations_used": iteration,
            "final_path": str(final_path),
        }


def get_insights(config_path: str, participant_id: str) -> dict[str, Any]:
    """Get current insights for a participant (latest iteration or final)."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    stem = _stem(config, participant_id)

    # Check for final first
    final_path = output_dir / f"{stem}_insights_final.json"
    if final_path.exists():
        insights = json.loads(final_path.read_text(encoding="utf-8"))
        return {"participant_id": participant_id, "source": "final", "insights": insights}

    # Otherwise find latest iteration
    state = PipelineState(output_dir)
    iteration = state.get_iteration(participant_id)
    iter_path = output_dir / f"{stem}_insights_iter{iteration}.json"
    if iter_path.exists():
        insights = json.loads(iter_path.read_text(encoding="utf-8"))
        return {"participant_id": participant_id, "source": f"iter{iteration}", "insights": insights}

    return {"participant_id": participant_id, "source": "none", "insights": []}


def get_revelation_context(config_path: str, participant_id: str) -> dict[str, Any]:
    """Get failed issues for re-extraction in a revelation loop."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    state = PipelineState(output_dir)
    stem = _stem(config, participant_id)

    error = state.require_state(participant_id, "extracting")
    if error:
        return error

    iteration = state.get_iteration(participant_id)
    prev_eval_path = output_dir / f"{stem}_evaluation_iter{iteration - 1}.json"

    if not prev_eval_path.exists():
        return artifact_not_found(str(prev_eval_path), "previous evaluation")

    evaluation = json.loads(prev_eval_path.read_text(encoding="utf-8"))
    results = evaluation.get("results", [])
    failed = [r for r in results if r.get("status") == "fail"]

    # Load transcript for context
    md_path = output_dir / f"{stem}_converted.md"
    transcript_md = ""
    if md_path.exists():
        transcript_md = md_path.read_text(encoding="utf-8")

    return {
        "participant_id": participant_id,
        "iteration": iteration,
        "failed_issues": failed,
        "transcript_md": transcript_md,
        "research_question": config.get("research", {}).get("question", ""),
        "hypotheses": config.get("research", {}).get("hypotheses", []),
    }


def reset_participant(config_path: str, participant_id: str) -> dict[str, Any]:
    """Hard reset a participant to not_started."""
    config = load_config(config_path)
    if "error" in config:
        return config

    output_dir = get_output_dir(config)
    state = PipelineState(output_dir)
    state.reset(participant_id)

    return {"participant_id": participant_id, "state": "not_started", "action": "reset"}
