# Maida

**Maida** is the pre-merge behavioral regression gate for AI agents. It records agent runs, compares current behavior against a known-good baseline, and fails CI when structural behavior regresses: more steps, unexpected tool calls, loops, latency spikes, or cost blowups.

**What it is:** A local-first, CI-first developer tool for recording runs, capturing baselines, and blocking bad PRs before merge.

**What it is not:** It is not a hosted telemetry product, a generic output eval platform, or a framework lock-in layer. The local viewer helps inspect evidence, but the core product is behavioral regression gating.

---

## In 60 seconds

**1. Install:**

```bash
pip install maida-ai
```

**2. Run the bundled demo agent** (simulated; no repo clone, no API keys):

```bash
maida demo
```

**3. Open the timeline viewer or capture a baseline:**

```bash
maida view
maida baseline --out baselines/my_agent.json
```

A browser tab opens showing the run timeline - tool calls, LLM calls, timing, warnings, and errors. Data is stored locally under `~/.maida/runs/<trace_id>/` as OTel-compatible spans plus metadata.

To watch the gate catch a regression end-to-end on canned data — baseline a good run, run a "refactored" agent that loops and calls a new tool, see the failing report with a PR-comment preview:

```bash
maida demo --regression
```

When you're ready to wire up your own project, `maida init` scaffolds a starter `.maida/policy.yaml` (add `--github` for a ready-to-edit CI workflow).

---

## Demos and examples

| Example | Path | How to run |
|--------|------|------------|
| **Minimal agent** (pure Python) | `examples/minimal/` | `python examples/minimal/simple_agent.py` |
| **LangChain minimal** | `examples/langchain/minimal.py` | `uv run --extra langchain python examples/langchain/minimal.py` |
| **OpenAI Agents minimal** | `examples/openai_agents/minimal.py` | `uv run --extra openai python examples/openai_agents/minimal.py` |
| **LangChain customer support** (advanced) | `examples/langchain/` | Set API keys, then follow `_customer_support/README.md` |
| **Demos** (short scripts) | `examples/demo/` | `python examples/demo/pure_python.py` or `python examples/demo/langchain.py` |

After any run, open the timeline with `maida view`.

---

## Documentation

| Page | Description |
|------|-------------|
| [Getting started](getting-started.md) | Installation (uv/pip), quickstart, data dir, redaction |
| [Guardrails](guardrails.md) | Stop runaway runs with loop, count, and duration limits |
| [Regression testing](regression-testing.md) | Baseline, assert, and diff workflow for catching agent regressions |
| [CLI](cli.md) | `demo`, `init`, `list`, `view`, `export`, `baseline`, `assert`, `diff` with options and exit codes |
| [Viewer](viewer.md) | Timeline UI usage, URL params, live refresh, and development |
| [SDK](sdk.md) | `@trace`, `traced_run`, `has_active_run`, `record_llm_call`, `record_tool_call`, `record_state` |
| [Integrations](integrations.md) | LangChain handler, OpenAI Agents adapter, and planned adapters |
| [Architecture](architecture.md) | OTel span schema, storage layout, viewer API, loop detection |
| **Reference** | |
| [Trace format](reference/trace-format.md) | OTel span envelope, derived event types, payload schemas, meta.json (public contract) |
| [Configuration](reference/config.md) | Env vars, YAML precedence, redaction, truncation, loop detection, guardrails |
| [Policy YAML](reference/policy.md) | Assertion policy file format, fields, threshold semantics, CLI mapping |
