#!/usr/bin/env python3
"""Execute numbered notebooks without crossing the manual-review gate."""

from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parent
NOTEBOOKS = sorted((ROOT / "notebooks").glob("[0-1][0-9]_*.ipynb"))


def execute(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=1800, kernel_name="python3", allow_errors=False)
    client.execute(cwd=str(ROOT))
    nbformat.write(notebook, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--until", choices=["manual_review"])
    mode.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    selected = [p for p in NOTEBOOKS if int(p.name[:2]) <= 9] if args.until else [p for p in NOTEBOOKS if int(p.name[:2]) >= 10]
    for notebook in selected:
        print(f"RUNNING {notebook.name}")
        execute(notebook)
    if args.until:
        print("MANUAL REVIEW REQUIRED")
        print("Edit: review/HUMAN_REVIEW_PACKAGE.tsv")
    else:
        print("RESUME COMPLETE")


if __name__ == "__main__":
    main()
