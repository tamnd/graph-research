#!/usr/bin/env python3
"""Validate local Markdown links, dossier length, Python syntax, and hygiene."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


def main() -> int:
    failures: list[str] = []

    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            failures.append(f"missing final newline: {path.relative_to(ROOT)}")

        for line_number, line in enumerate(text.splitlines(), 1):
            if line != line.rstrip():
                failures.append(
                    f"trailing whitespace: {path.relative_to(ROOT)}:{line_number}"
                )

        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            local = target.split("#", 1)[0]
            if not local:
                continue
            resolved = (path.parent / local).resolve()
            if not resolved.exists():
                failures.append(
                    f"broken link: {path.relative_to(ROOT)} -> {target}"
                )

        relative = path.relative_to(DOCS)
        if len(relative.parts) >= 3 and relative.parts[0] == "research":
            if len(text.splitlines()) < 500:
                failures.append(
                    f"dedicated spec below 500 lines: {path.relative_to(ROOT)}"
                )

    for path in sorted((ROOT / "src").rglob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as error:
            failures.append(f"Python syntax: {path.relative_to(ROOT)}: {error}")

    ignored_artifacts = list(ROOT.rglob("__pycache__")) + list(ROOT.rglob("*.pyc"))
    for path in ignored_artifacts:
        if ".git" not in path.parts:
            failures.append(f"generated artifact present: {path.relative_to(ROOT)}")

    if failures:
        print("repository validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
