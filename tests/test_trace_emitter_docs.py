import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class TraceEmitterDocsTests(unittest.TestCase):
    def test_emitter_guide_documents_the_external_contract(self) -> None:
        guide = (REPO_ROOT / "docs" / "reference" / "trace-emitter.md").read_text(
            encoding="utf-8"
        )

        for expected in (
            "maida validate-trace emitted-run/",
            '"spec_version": "0.2.0"',
            "meta.json",
            "spans.jsonl",
            "Required fields",
            "Optional enrichments",
            "Main thread",
            "Subthreads",
            "parent_span_id",
            "Breaking changes",
            "Exit codes",
            "maida/blob/main/schemas/trace/0.2.0/meta.schema.json",
            "maida/blob/main/schemas/trace/0.2.0/span.schema.json",
        ):
            self.assertIn(expected, guide)

    def test_navigation_index_and_cli_expose_trace_validation(self) -> None:
        nav = (REPO_ROOT / "docs" / "reference" / "index.md").read_text(
            encoding="utf-8"
        )
        index = (REPO_ROOT / "docs" / "index.md").read_text(encoding="utf-8")
        cli = (REPO_ROOT / "docs" / "cli" / "validate-trace.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("External emitter guide </reference/trace-emitter>", nav)
        self.assertIn("External emitter guide", index)
        self.assertIn("# `maida validate-trace`", cli)
        self.assertIn("maida validate-trace PATH [--json]", cli)
        self.assertIn("invalid trace content", cli)
        self.assertNotIn('"spec_version": "0.2",', cli)

    def test_trace_reference_uses_the_in_band_versioned_contract(self) -> None:
        reference = (REPO_ROOT / "docs" / "reference" / "trace-format.md").read_text(
            encoding="utf-8"
        )

        for expected in (
            'spec_version: "0.2.0"',
            "versioned JSON Schemas",
            "Patch releases",
            "Minor releases",
            "Major releases",
            "immutable",
            "maida validate-trace",
            "trace-emitter.md",
        ):
            self.assertIn(expected, reference)

        self.assertNotIn(
            "does not currently include a top-level `spec_version`", reference
        )
        self.assertNotIn("Local `meta.json` does not include `spec_version`", reference)

    def test_storage_summaries_include_the_contract_version(self) -> None:
        architecture = (REPO_ROOT / "docs" / "architecture.md").read_text(
            encoding="utf-8"
        )
        getting_started = (REPO_ROOT / "docs" / "getting-started.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("**meta.json** - Run metadata: `spec_version`", architecture)
        self.assertIn("`meta.json` - run metadata (`spec_version`", getting_started)


if __name__ == "__main__":
    unittest.main()
