from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class WorkflowContext:
    root: Path
    project: dict[str, Any]
    thresholds: dict[str, Any]
    media: dict[str, Any]

    def path(self, value: str | None) -> Path | None:
        if value in (None, ""):
            return None
        candidate = Path(value)
        if candidate.is_absolute():
            raise ValueError(f"Absolute path forbidden in config: {value}")
        return (self.root / candidate).resolve()


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_context(root: str | Path | None = None) -> WorkflowContext:
    base = Path(root).resolve() if root else Path(__file__).resolve().parents[1]
    return WorkflowContext(
        root=base,
        project=_read_yaml(base / "config" / "project.yaml"),
        thresholds=_read_yaml(base / "config" / "thresholds.yaml"),
        media=_read_yaml(base / "config" / "media.yaml"),
    )
