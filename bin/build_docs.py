#!/usr/bin/env python3
"""Build the pinned engine docs and main together without mixing sources."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
spec = importlib.util.spec_from_file_location("sync_docs", REPO_ROOT / "bin/sync_docs.py")
sync_docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_docs)


def pinned_engine_ref() -> str:
    """The release channel always uses the contract, never a preview override."""
    return json.loads(sync_docs.CONTRACT.read_text(encoding="utf-8"))["engine_ref"]


def build(output: Path) -> None:
    release = pinned_engine_ref()
    versions = [
        {"name": f"Release ({release})", "version": release, "url": "/docs/", "preferred": True},
        {"name": "main (unreleased)", "version": "main", "url": "/docs/main/"},
    ]
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Keep the old output until both strict builds succeed. Staging beside the
    # output also lets the final rename stay on the same filesystem.
    with tempfile.TemporaryDirectory(prefix=".docs-build-", dir=output.parent) as tmp:
        staging = Path(tmp)
        published = staging / "site"
        for channel, ref in (("release", release), ("main", "main")):
            engine, label = sync_docs.fetch_engine_docs(
                staging / f"engine-{channel}", ref=ref,
                local=os.environ.get("MAIDA_DOCS_PATH") if channel == "main" else None,
            )
            print(f"{channel} documentation source: {label}", flush=True)
            source = staging / f"source-{channel}"
            source.mkdir()
            for name in sorted(sync_docs.SITE_OWNED):
                origin = DOCS_ROOT / name
                if origin.is_dir():
                    shutil.copytree(
                        origin, source / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    )
                elif origin.is_file():
                    shutil.copy2(origin, source / name)
            # Generated downloads in the presentation tree must not leak into
            # a different engine version that no longer supplies them.
            for target in sync_docs.EXAMPLE_SOURCES.values():
                (source / target).unlink(missing_ok=True)
            sync_docs.sync(engine, False, source)
            env = os.environ.copy()
            env.update(MAIDA_DOCS_CHANNEL=channel, MAIDA_DOCS_VERSION=ref)
            destination = published if channel == "release" else published / "main"
            subprocess.run([
                sys.executable, "-m", "sphinx", "-W", "--keep-going", "-E",
                "-b", "dirhtml", "-d", str(staging / f"doctrees-{channel}"),
                str(source), str(destination),
            ], check=True, env=env)
        (published / "versions.json").write_text(
            json.dumps(versions, indent=2) + "\n", encoding="utf-8"
        )
        if output.exists():
            shutil.rmtree(output)
        published.rename(output)


if __name__ == "__main__":
    build(REPO_ROOT / "site")
