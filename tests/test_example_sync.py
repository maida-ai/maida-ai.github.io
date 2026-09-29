"""Keep released downloads while allowing examples to move to tutorials."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "sync_docs", Path(__file__).parents[1] / "bin/sync_docs.py"
)
sync_docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_docs)


class ExampleSyncTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.engine = root / "engine"
        (self.engine / "docs").mkdir(parents=True)
        self.site = root / "site"
        self.enterContext(patch.object(sync_docs, "DOCS_ROOT", self.site))
        self.enterContext(patch.object(sync_docs, "EXAMPLE_SOURCES", {
            "examples/minimal.py": "assets/examples/minimal.py",
        }))

    def test_released_engine_download_is_copied(self):
        (self.engine / "examples").mkdir()
        (self.engine / "examples/minimal.py").write_text("print('released example')\n")
        sync_docs.sync_examples(self.engine, False)
        self.assertEqual((self.site / "assets/examples/minimal.py").read_bytes(),
                         (self.engine / "examples/minimal.py").read_bytes())
        self.assertEqual(sync_docs.sync_examples(self.engine, True), [])

    def test_migrated_engine_uses_tutorial_link_without_missing_download(self):
        (self.engine / "docs/integrations.md").write_text(
            "[Example](https://github.com/maida-ai/maida-tutorials/tree/main/examples)\n"
        )
        self.assertEqual(sync_docs.sync_examples(self.engine, False), [])
        self.assertEqual(sync_docs.sync_examples(self.engine, True), [])

    def test_missing_still_referenced_download_is_an_error(self):
        (self.engine / "docs/integrations.md").write_text(
            "[Download](/docs/assets/examples/minimal.py)\n"
        )
        with self.assertRaisesRegex(SystemExit, "missing"):
            sync_docs.sync_examples(self.engine, False)


if __name__ == "__main__":
    unittest.main()
