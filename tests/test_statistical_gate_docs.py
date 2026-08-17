import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class StatisticalGateDocsTests(unittest.TestCase):
    def test_regression_guide_documents_current_contract(self) -> None:
        guide = (REPO_ROOT / "docs" / "regression-testing.md").read_text()

        for expected in (
            "maida run my_agent.py",
            "--no-fail-fast",
            "PASS",
            "FAIL",
            "INCONCLUSIVE",
            "Baseline schema `0.3.1`",
            "Report schema `2.0.1`",
            "one-sided Wilson",
            "v2 policy",
        ):
            self.assertIn(expected, guide)
        self.assertNotIn('"report_version": "1"', guide)

    def test_cli_reference_documents_current_commands_and_versions(self) -> None:
        cli = "\n".join(
            path.read_text()
            for path in sorted((REPO_ROOT / "docs" / "cli").glob("*.md"))
        )

        for expected in (
            "# `maida capture claude-code`",
            "# `maida scenario run`",
            "# `maida run`",
            "# `maida extract`",
            "# `maida drift`",
            "`--trials`",
            "`--fail-fast` / `--no-fail-fast`",
            "`--json-out`",
            "report schema `2.0.1`",
        ):
            self.assertIn(expected, cli)

    def test_policy_reference_is_v2_and_keeps_v1_in_migration_only(self) -> None:
        policy = (REPO_ROOT / "docs" / "reference" / "policy.md").read_text()

        self.assertIn("# Policy v2 and gate decisions", policy)
        self.assertIn("version: 2.1", policy)
        self.assertIn("plan_depth", policy)
        self.assertIn("| Plan | `0.1.0`", policy)
        self.assertIn("Unknown fields are errors", policy)
        self.assertIn("one-sided coverage", policy)
        self.assertIn("## v1 migration", policy)
        primary = policy.split("## v1 migration", 1)[0]
        self.assertNotIn("\nassert:\n", primary)

    def test_public_surfaces_match_python_owned_current_main_snapshot(self) -> None:
        contract = json.loads(
            (REPO_ROOT / "tests" / "contracts" / "current-main.json").read_text()
        )
        index = (REPO_ROOT / "docs" / "index.md").read_text()
        getting_started = (REPO_ROOT / "docs" / "getting-started.md").read_text()
        homepage_paths = [
            REPO_ROOT / "templates" / "index.html",
            *(REPO_ROOT / "templates" / "sections" / "home").glob("*.html"),
        ]
        homepage = "\n".join(path.read_text() for path in homepage_paths)
        regression = (REPO_ROOT / "docs" / "regression-testing.md").read_text()
        policy = (REPO_ROOT / "docs" / "reference" / "policy.md").read_text()
        trace = (REPO_ROOT / "docs" / "reference" / "trace-format.md").read_text()
        cli = "\n".join(
            path.read_text()
            for path in sorted((REPO_ROOT / "docs" / "cli").glob("*.md"))
        )
        scheduled = (REPO_ROOT / "docs" / "scheduled-checks.md").read_text()

        for text in (index, getting_started, homepage):
            self.assertIn(contract["install_requirement"], text)
        self.assertIn(contract["action_ref"], homepage)
        self.assertIn("checks: write", homepage)
        self.assertIn(
            f'maida {contract["cli"]["primary_gate"]} my_agent.py', homepage
        )
        self.assertIn(f'Baseline schema `{contract["schemas"]["baseline"]}`', regression)
        self.assertIn(f'Report schema `{contract["schemas"]["report"]}`', regression)
        self.assertIn(f'version: {contract["schemas"]["policy"]}', policy)
        self.assertIn(f'| Plan | `{contract["schemas"]["plan"]}`', policy)
        self.assertIn(f'report schema `{contract["schemas"]["report"]}`', cli)
        self.assertIn(
            f'report schema `{contract["schemas"]["report"]}`',
            scheduled.replace("\n", " "),
        )
        self.assertIn(f'spec_version: "{contract["schemas"]["trace"]}"', trace)
        self.assertNotIn("maida assert --baseline", homepage)

    def test_navigation_exposes_current_workflows(self) -> None:
        nav = "\n".join(
            (
                (REPO_ROOT / "docs" / "index.md").read_text(),
                (REPO_ROOT / "docs" / "guides" / "index.md").read_text(),
                (REPO_ROOT / "docs" / "reference" / "index.md").read_text(),
            )
        )
        for expected in (
            "Capture Claude Code </claude-code>",
            "Scheduled checks </scheduled-checks>",
            "Gate draft extraction </extraction>",
            "Policy v2 </reference/policy>",
        ):
            self.assertIn(expected, nav)

    def test_ci_and_deploy_both_enforce_documentation_contracts(self) -> None:
        ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
        deploy = (REPO_ROOT / ".github" / "workflows" / "deploy.yml").read_text()

        command = "uv run python -m unittest discover -s tests"
        self.assertIn(command, ci)
        self.assertIn("make docs", ci)
        self.assertIn(command, deploy)


if __name__ == "__main__":
    unittest.main()
