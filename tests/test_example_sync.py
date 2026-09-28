"""Keep released downloads while allowing examples to move to tutorials."""
import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "sync_docs", Path(__file__).parents[1] / "bin/sync_docs.py"
)
sync_docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_docs)


def setup_source(tmp_path, monkeypatch):
    engine = tmp_path / "engine"
    (engine / "docs").mkdir(parents=True)
    site = tmp_path / "site"
    monkeypatch.setattr(sync_docs, "DOCS_ROOT", site)
    monkeypatch.setattr(sync_docs, "EXAMPLE_SOURCES", {
        "examples/minimal.py": "assets/examples/minimal.py",
    })
    return engine, site


def test_released_engine_download_is_copied(tmp_path, monkeypatch):
    engine, site = setup_source(tmp_path, monkeypatch)
    (engine / "examples").mkdir()
    (engine / "examples/minimal.py").write_text("print('released example')\n")
    sync_docs.sync_examples(engine, False)
    assert (site / "assets/examples/minimal.py").read_bytes() == (
        engine / "examples/minimal.py"
    ).read_bytes()
    assert sync_docs.sync_examples(engine, True) == []


def test_migrated_engine_uses_tutorial_link_without_missing_download(tmp_path, monkeypatch):
    engine, _ = setup_source(tmp_path, monkeypatch)
    (engine / "docs/integrations.md").write_text(
        "[Example](https://github.com/maida-ai/maida-tutorials/tree/main/examples)\n"
    )
    assert sync_docs.sync_examples(engine, False) == []
    assert sync_docs.sync_examples(engine, True) == []


def test_missing_still_referenced_download_is_an_error(tmp_path, monkeypatch):
    engine, _ = setup_source(tmp_path, monkeypatch)
    (engine / "docs/integrations.md").write_text(
        "[Download](/docs/assets/examples/minimal.py)\n"
    )
    with pytest.raises(SystemExit, match="missing"):
        sync_docs.sync_examples(engine, False)
