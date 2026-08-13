import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"

CLI_COMMAND_PAGES = (
    "validate-trace",
    "capture-claude-code",
    "capture-claude-hook",
    "import-claude-code",
    "scenario-run",
    "demo",
    "init",
    "import-langfuse",
    "list",
    "view",
    "export",
    "baseline",
    "accept",
    "run",
    "extract",
    "drift",
    "assert",
    "diff",
)

INTEGRATION_PAGES = (
    "langchain-langgraph",
    "openai-agents",
    "crewai",
)


class DocumentationSiteTests(unittest.TestCase):
    def test_sphinx_pydata_replaces_mkdocs(self) -> None:
        project = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        config = (DOCS_ROOT / "conf.py").read_text(encoding="utf-8")

        self.assertNotIn('"mkdocs', project)
        self.assertIn('"sphinx>=9.1', project)
        self.assertIn('"myst-parser>=5.1', project)
        self.assertIn('"pydata-sphinx-theme>=0.20', project)
        self.assertIn('"sphinx-copybutton>=0.5.2', project)
        self.assertIn('requires-python = ">=3.12"', project)
        self.assertFalse((REPO_ROOT / "mkdocs.yml").exists())
        self.assertIn('html_theme = "pydata_sphinx_theme"', config)
        self.assertIn('"default_mode": "light"', config)
        self.assertIn("myst_heading_anchors = 4", config)

    def test_navigation_has_task_guides_integrations_and_reference(self) -> None:
        index = (DOCS_ROOT / "index.md").read_text(encoding="utf-8")
        for entry in (
            "getting-started",
            "guides/index",
            "integrations",
            "reference/index",
        ):
            self.assertIn(entry, index)

        guides = (DOCS_ROOT / "guides" / "index.md").read_text(encoding="utf-8")
        for entry in (
            "/regression-testing",
            "/guardrails",
            "/viewer",
            "/claude-code",
            "/scheduled-checks",
            "/extraction",
        ):
            self.assertIn(entry, guides)

    def test_cli_commands_have_individual_reference_pages(self) -> None:
        overview = (DOCS_ROOT / "cli.md").read_text(encoding="utf-8")
        for slug in CLI_COMMAND_PAGES:
            page = DOCS_ROOT / "cli" / f"{slug}.md"
            with self.subTest(slug=slug):
                self.assertTrue(page.exists())
                self.assertIn(f"cli/{slug}", overview)

    def test_integrations_have_individual_guides(self) -> None:
        overview = (DOCS_ROOT / "integrations.md").read_text(encoding="utf-8")
        for slug in INTEGRATION_PAGES:
            page = DOCS_ROOT / "integrations" / f"{slug}.md"
            with self.subTest(slug=slug):
                self.assertTrue(page.exists())
                self.assertIn(f"integrations/{slug}", overview)

    def test_docs_brand_is_text_only_and_assets_keep_stable_paths(self) -> None:
        brand = (
            DOCS_ROOT / "_templates" / "maida-brand.html"
        ).read_text(encoding="utf-8")
        config = (DOCS_ROOT / "conf.py").read_text(encoding="utf-8")
        integrations = (DOCS_ROOT / "integrations.md").read_text(encoding="utf-8")

        self.assertIn(">Maida<", brand)
        self.assertIn(">Docs<", brand)
        self.assertNotIn("<img", brand)
        self.assertIn('destination = Path(app.outdir) / "assets" / "examples"', config)
        self.assertIn('app.connect("build-finished", _copy_download_assets)', config)
        self.assertIn("/docs/assets/examples/", integrations)

    def test_theme_uses_maida_light_and_dark_tokens_without_grid_or_glow(self) -> None:
        stylesheet = (
            DOCS_ROOT / "_static" / "maida-docs.css"
        ).read_text(encoding="utf-8")
        layout = (
            DOCS_ROOT / "_templates" / "layout.html"
        ).read_text(encoding="utf-8")

        self.assertIn('html[data-theme="light"]', stylesheet)
        self.assertIn('html[data-theme="dark"]', stylesheet)
        self.assertIn("--maida-green", stylesheet)
        self.assertIn("--maida-danger", stylesheet)
        self.assertIn('class="maida-docs-home"', layout)
        self.assertIn(
            "body.maida-docs-home .bd-main .bd-content .bd-article-container",
            stylesheet,
        )
        self.assertIn(
            ".bd-article #catch-agent-changes-before-merge > h1",
            stylesheet,
        )
        self.assertIn("max-width: 76rem", stylesheet)
        self.assertNotIn("grid-pattern", stylesheet)
        self.assertNotIn("radial-gradient", stylesheet)
        self.assertNotIn("box-shadow: 0 0", stylesheet)

    def test_ci_and_deploy_use_the_canonical_docs_build(self) -> None:
        makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
        ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
        deploy = (REPO_ROOT / ".github" / "workflows" / "deploy.yml").read_text()

        self.assertIn("sphinx-build", makefile)
        self.assertIn("-W --keep-going", makefile)
        self.assertIn("-b dirhtml", makefile)
        self.assertIn("run: make docs", ci)
        self.assertIn("run: make docs", deploy)
        self.assertNotIn("mkdocs build", deploy)


if __name__ == "__main__":
    unittest.main()
