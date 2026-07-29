import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class StatisticalGateDocsTests(unittest.TestCase):
    def test_regression_guide_documents_repeated_isolated_trials(self) -> None:
        guide = (REPO_ROOT / "docs" / "regression-testing.md").read_text()

        self.assertIn("maida run path/to/agent.py", guide)
        self.assertIn("fresh temporary copy", guide)
        self.assertIn("tracked files and non-ignored working-tree files", guide)
        self.assertIn("PASS", guide)
        self.assertIn("FAIL", guide)
        self.assertIn("INCONCLUSIVE", guide)
        self.assertIn("N=1", guide)
        self.assertIn("N=3", guide)
        self.assertIn('"report_version": "1"', guide)
        self.assertIn('"aggregate_results": []', guide)
        self.assertIn('"passed": null', guide)

    def test_cli_reference_documents_statistical_run_options(self) -> None:
        cli = (REPO_ROOT / "docs" / "cli.md").read_text()

        self.assertIn("## `maida run`", cli)
        self.assertIn("`--trials`", cli)
        self.assertIn("`--confidence-level`", cli)
        self.assertIn("`--pass-rate-threshold`", cli)
        self.assertIn("`--json-out`", cli)

    def test_policy_reference_documents_statistical_defaults(self) -> None:
        policy = (REPO_ROOT / "docs" / "reference" / "policy.md").read_text()

        self.assertIn("`trials`", policy)
        self.assertIn("`confidence_level`", policy)
        self.assertIn("`pass_rate_threshold`", policy)
        self.assertIn("trials: 3", policy)
        self.assertIn("confidence_level: 0.95", policy)
        self.assertIn("pass_rate_threshold: 0.90", policy)


if __name__ == "__main__":
    unittest.main()
