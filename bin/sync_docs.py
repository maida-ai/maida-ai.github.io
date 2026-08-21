#!/usr/bin/env python3
"""Pull the documentation content pages from the Maida core repository.

`maida/docs/` is the single source of truth for Maida's documentation: a page
ships in the same pull request as the behavior it describes. This repository
owns only the *presentation* of those pages -- the Sphinx configuration, the
theme, the docs landing page, and the static assets.

The engine reference is not `main`. It is the released `engine_ref` recorded in
`tests/contracts/current-main.json`, the same pin every other Maida repository
consumes, so the published docs describe the released engine rather than
whatever is currently on `main`.

Usage:

    python3 bin/sync_docs.py              # sync at the pinned engine_ref
    python3 bin/sync_docs.py --check      # fail if docs/ is out of sync
    MAIDA_DOCS_REF=main python3 bin/sync_docs.py
    MAIDA_DOCS_PATH=../maida python3 bin/sync_docs.py    # local checkout

Set `MAIDA_DOCS_PATH` to preview unreleased documentation against a local
`maida` checkout. Never commit a build that used it.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
CONTRACT = REPO_ROOT / "tests" / "contracts" / "current-main.json"

ENGINE_REPO = "https://github.com/maida-ai/maida.git"

# Owned by this repository. The sync never creates or overwrites these.
#
# `index.md` is the docs landing page: it is a designed hero, not documentation
# content, so it stays here next to the templates it shares its styling with.
SITE_OWNED = {
    "index.md",
    "conf.py",
    ".gitignore",
    "_static",
    "_templates",
    "assets",
}

# The runnable example scripts offered as downloads from the integration pages.
# These are the real files from the engine repo, not copies: the site used to
# carry its own forks, which drifted until the published pages described tools
# and call counts the actual examples never produced.
EXAMPLE_SOURCES = {
    "examples/langchain/minimal.py": "assets/examples/langchain-minimal.py",
    "examples/openai_agents/minimal.py": "assets/examples/openai-agents-minimal.py",
    "examples/crewai/minimal.py": "assets/examples/crewai-minimal.py",
}

# Present in the engine repo but deliberately not published: working notes and
# design drafts that would read as shipped behavior on maida.ai.
ENGINE_ONLY = {
    "index.md",
    "calibration-187.md",
    "design",
}


def engine_ref() -> str:
    if override := os.environ.get("MAIDA_DOCS_REF"):
        return override
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    return contract["engine_ref"]


def fetch_engine_docs(destination: Path) -> tuple[Path, str]:
    """Return the engine checkout root and a human-readable source label."""
    if local := os.environ.get("MAIDA_DOCS_PATH"):
        root = Path(local).expanduser().resolve()
        if not (root / "docs").is_dir():
            sys.exit(f"error: MAIDA_DOCS_PATH has no docs directory: {root / 'docs'}")
        return root, f"local checkout {root}"

    ref = engine_ref()
    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            ref,
            "--quiet",
            ENGINE_REPO,
            str(destination),
        ],
        check=True,
    )
    return destination, f"{ENGINE_REPO}@{ref}"


def synced_files(source: Path) -> list[Path]:
    """Content pages to copy, as paths relative to the engine docs root."""
    results: list[Path] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if relative.parts[0] in ENGINE_ONLY:
            continue
        if relative.parts[0] in SITE_OWNED:
            continue
        results.append(relative)
    return results


def sync_examples(engine_root: Path, check_only: bool) -> list[str]:
    """Copy the downloadable example scripts, or report which are stale."""
    stale: list[str] = []
    for relative_source, relative_target in EXAMPLE_SOURCES.items():
        origin = engine_root / relative_source
        target = DOCS_ROOT / relative_target
        if not origin.is_file():
            sys.exit(f"error: engine example missing: {relative_source}")
        if check_only:
            if not target.exists() or not filecmp.cmp(origin, target, shallow=False):
                stale.append(relative_target)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, target)
    return stale


def sync(engine_root: Path, check_only: bool) -> int:
    source = engine_root / "docs"
    files = synced_files(source)
    if not files:
        sys.exit(f"error: no documentation pages found under {source}")

    stale: list[str] = []
    copied = 0

    for relative in files:
        target = DOCS_ROOT / relative
        origin = source / relative
        if check_only:
            if not target.exists() or not filecmp.cmp(origin, target, shallow=False):
                stale.append(str(relative))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, target)
        copied += 1

    # A page deleted upstream must not linger in the built site.
    expected = {DOCS_ROOT / relative for relative in files}
    for path in sorted(DOCS_ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(DOCS_ROOT)
        if relative.parts[0] in SITE_OWNED:
            continue
        if path not in expected:
            if check_only:
                stale.append(f"{relative} (removed upstream)")
            else:
                path.unlink()
                print(f"  removed {relative}")

    stale.extend(sync_examples(engine_root, check_only))

    if check_only:
        if stale:
            print("docs/ is out of sync with the engine documentation:")
            for item in stale:
                print(f"  {item}")
            print("\nRun: python3 bin/sync_docs.py")
            return 1
        print(
            f"docs/ is in sync ({len(files)} pages, "
            f"{len(EXAMPLE_SOURCES)} example scripts)"
        )
        return 0

    print(f"synced {copied} pages and {len(EXAMPLE_SOURCES)} example scripts")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify docs/ matches the engine source instead of writing",
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        engine_root, label = fetch_engine_docs(Path(tmp) / "maida")
        print(f"documentation source: {label}")
        return sync(engine_root, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
