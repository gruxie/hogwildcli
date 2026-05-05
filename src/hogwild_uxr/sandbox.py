"""Path sandboxing — ensures all file I/O stays within the project directory."""

from __future__ import annotations

from pathlib import Path

from .errors import sandbox_violation


def resolve_safe(path: str | Path, project_dir: str | Path) -> Path:
    """Resolve a path and verify it's within the project directory."""
    project_dir = Path(project_dir).resolve()
    target = Path(path)
    if not target.is_absolute():
        target = project_dir / target
    target = target.resolve()

    try:
        target.relative_to(project_dir)
    except ValueError:
        raise ValueError(sandbox_violation(str(path), str(project_dir)))

    return target


def ensure_parent_exists(path: Path) -> None:
    """Create parent directories for a path if they don't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
