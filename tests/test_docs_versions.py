"""Exercise versioned output and failures with small, offline engine fixtures."""

import importlib.util
from html import unescape
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "build_docs", REPO_ROOT / "bin/build_docs.py"
)
build_docs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_docs)


class VersionedDocsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.release = self.engine("release", "Released interface")
        self.main = self.engine("main", "Unreleased interface")
        self.output = self.root / "site"

    def engine(self, name, content):
        root = self.root / name
        (root / "docs").mkdir(parents=True)
        (root / "docs/getting-started.md").write_text(f"# {content}\n")
        (root / "examples/langchain").mkdir(parents=True)
        (root / "examples/langchain/minimal.py").write_text(f"print('{name}')\n")
        return root

    def fetch(self, destination, *, ref=None, local=None):
        return (self.release if ref == "v9.8.7" else self.main), ref

    def build(self):
        presentation = self.root / "presentation"
        presentation.mkdir(exist_ok=True)
        (presentation / "index.md").write_text(
            "# Docs\n\n{{ maida_install_command }}\n\n"
            "```{toctree}\ngetting-started\n```\n"
        )
        for name in ("conf.py", "_templates", "_static"):
            source = REPO_ROOT / "docs" / name
            if source.is_dir():
                build_docs.shutil.copytree(source, presentation / name, dirs_exist_ok=True)
            else:
                build_docs.shutil.copy2(source, presentation / name)
        (presentation / "assets").mkdir(exist_ok=True)
        build_docs.shutil.copy2(
            REPO_ROOT / "docs/assets/favicon.svg", presentation / "assets/favicon.svg"
        )
        with patch.object(build_docs, "DOCS_ROOT", presentation), patch.object(
            build_docs, "pinned_engine_ref", return_value="v9.8.7"
        ), patch.object(build_docs.sync_docs, "fetch_engine_docs", side_effect=self.fetch):
            build_docs.build(self.output)

    def test_versions_have_separate_content_assets_and_navigation(self):
        self.build()
        released = (self.output / "getting-started/index.html").read_text()
        main = (self.output / "main/getting-started/index.html").read_text()
        self.assertIn("Released interface", released)
        self.assertNotIn("Unreleased interface", released)
        self.assertIn("Unreleased interface", main)
        self.assertNotIn("Released interface", main)
        self.assertIn('href="/docs/"', released)
        self.assertIn('href="/docs/main/"', main)
        self.assertIn("main (unreleased)", main)
        self.assertIn("version-switcher__button", main)
        self.assertIn("theme_switcher_version_match = 'main'", main)
        self.assertIn("theme_switcher_version_match = 'v9.8.7'", released)
        self.assertIn("theme_switcher_json_url = '/docs/versions.json'", main)
        self.assertIn("https://maida.ai/docs/main/getting-started/", main)
        self.assertIn("https://maida.ai/docs/getting-started/", released)
        release_home = (self.output / "index.html").read_text()
        main_home = unescape((self.output / "main/index.html").read_text())
        self.assertIn('maida-ai==9.8.7', release_home)
        self.assertIn("git+https://github.com/maida-ai/maida.git@main", main_home)
        self.assertNotIn("maida-ai==9.8.7", main_home)
        self.assertEqual(
            (self.output / "assets/examples/langchain-minimal.py").read_text(),
            "print('release')\n",
        )
        self.assertEqual(
            (self.output / "main/assets/examples/langchain-minimal.py").read_text(),
            "print('main')\n",
        )
        for channel in (self.output, self.output / "main"):
            self.assertTrue((channel / "searchindex.js").is_file())
        self.assertEqual(json.loads((self.output / "versions.json").read_text()), [
            {"name": "Release (v9.8.7)", "version": "v9.8.7", "url": "/docs/", "preferred": True},
            {"name": "main (unreleased)", "version": "main", "url": "/docs/main/"},
        ])

    def test_failed_main_build_preserves_previously_built_site(self):
        self.output.mkdir()
        (self.output / "index.html").write_text("Previous site")
        (self.main / "docs/getting-started.md").write_text(
            "# Broken main\n\n[Missing page](missing.md)\n"
        )
        with self.assertRaises(build_docs.subprocess.CalledProcessError):
            self.build()
        self.assertEqual((self.output / "index.html").read_text(), "Previous site")
        self.assertFalse((self.output / "main").exists())

    def test_removed_upstream_pages_do_not_survive_a_rebuild(self):
        self.output.mkdir()
        (self.output / "obsolete.html").write_text("Old page")
        self.build()
        self.assertFalse((self.output / "obsolete.html").exists())

    def test_preview_overrides_cannot_replace_the_release_source(self):
        calls = []
        def fetch(destination, *, ref=None, local=None):
            calls.append((ref, local))
            return (self.release if ref == "v9.8.7" else self.main), ref
        with patch.dict(build_docs.os.environ, {
            "MAIDA_DOCS_REF": "some-other-release",
            "MAIDA_DOCS_PATH": str(self.main),
        }), patch.object(self, "fetch", side_effect=fetch):
            self.build()
        self.assertEqual(calls, [("v9.8.7", None), ("main", str(self.main))])

    def test_main_only_page_and_removed_download_do_not_leak_between_versions(self):
        (self.main / "docs/new-feature.md").write_text("# New feature\n")
        (self.main / "docs/getting-started.md").write_text(
            "# Unreleased interface\n\n```{toctree}\nnew-feature\n```\n"
        )
        (self.main / "examples/langchain/minimal.py").unlink()
        self.build()
        self.assertTrue((self.output / "main/new-feature/index.html").exists())
        self.assertFalse((self.output / "new-feature").exists())
        self.assertFalse((self.output / "main/assets/examples/langchain-minimal.py").exists())
        self.assertTrue((self.output / "assets/examples/langchain-minimal.py").exists())


class EngineSourceTests(unittest.TestCase):
    def test_explicit_release_ignores_preview_environment(self):
        destination = Path("/tmp/engine-release")
        with patch.dict(build_docs.os.environ, {
            "MAIDA_DOCS_REF": "main", "MAIDA_DOCS_PATH": "/tmp/local-preview",
        }), patch.object(build_docs.sync_docs.subprocess, "run") as clone:
            root, label = build_docs.sync_docs.fetch_engine_docs(destination, ref="v9.8.7")
        self.assertEqual(root, destination)
        self.assertIn("@v9.8.7", label)
        command = clone.call_args.args[0]
        self.assertEqual(command[command.index("--branch") + 1], "v9.8.7")
        self.assertTrue(clone.call_args.kwargs["check"])

    def test_local_preview_without_docs_is_rejected(self):
        with tempfile.TemporaryDirectory() as local:
            with self.assertRaisesRegex(SystemExit, "has no docs directory"):
                build_docs.sync_docs.fetch_engine_docs(Path(local) / "unused", ref="main", local=local)

    def test_fetch_failure_is_propagated(self):
        error = build_docs.subprocess.CalledProcessError(128, ["git", "clone"])
        with patch.object(build_docs.sync_docs.subprocess, "run", side_effect=error):
            with self.assertRaises(build_docs.subprocess.CalledProcessError):
                build_docs.sync_docs.fetch_engine_docs(Path("/tmp/unreachable-engine"), ref="main")


if __name__ == "__main__":
    unittest.main()
