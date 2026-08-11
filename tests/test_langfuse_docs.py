import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class LangfuseDocsTests(unittest.TestCase):
    def test_dedicated_guide_documents_import_mapping_privacy_and_ci(self) -> None:
        guide = (REPO_ROOT / "docs" / "langfuse.md").read_text(encoding="utf-8")

        for expected in (
            "maida import langfuse --trace-id",
            "GET /api/public/v2/observations",
            "LANGFUSE_PUBLIC_KEY",
            "LANGFUSE_SECRET_KEY",
            "read-only",
            "local Maida storage",
            'uv tool install "maida-ai>=0.5"',
            "GENERATION",
            "TOOL",
            "trace-command:",
            "maida-ai/maida-assert@v5",
            "fixed one-trial gate",
            "maida-tutorials/tree/main/demos/langfuse_import",
        ):
            self.assertIn(expected, guide)

    def test_navigation_index_integrations_and_cli_link_the_importer(self) -> None:
        nav = (REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        index = (REPO_ROOT / "docs" / "index.md").read_text(encoding="utf-8")
        integrations = (REPO_ROOT / "docs" / "integrations.md").read_text(
            encoding="utf-8"
        )
        cli = (REPO_ROOT / "docs" / "cli.md").read_text(encoding="utf-8")

        self.assertIn("Import Langfuse traces: langfuse.md", nav)
        self.assertIn("[Import Langfuse traces](langfuse.md)", index)
        self.assertIn("Langfuse trace import", integrations)
        self.assertIn("[Langfuse import guide](langfuse.md)", integrations)
        self.assertIn("## `maida import langfuse`", cli)
        self.assertIn("[Importing Langfuse traces](langfuse.md)", cli)

    def test_public_examples_reference_current_unreleased_action(self) -> None:
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for root in (REPO_ROOT / "docs", REPO_ROOT / "templates")
            for path in root.rglob("*")
            if path.suffix in {".md", ".html", ".yml", ".yaml"}
        )

        self.assertIn("maida-ai/maida-assert@v5", public_text)
        self.assertNotIn("maida-ai/maida-assert@V4", public_text)
        self.assertNotIn("maida-ai/maida-assert@V5", public_text)


if __name__ == "__main__":
    unittest.main()
