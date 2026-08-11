# Maida

**Maida** is the pre-merge behavioral regression gate for AI agents. It records agent runs, compares current behavior against a known-good baseline, and fails CI when structural behavior regresses: more steps, unexpected tool calls, loops, latency spikes, or cost blowups.

**What it is:** A local-first, CI-first developer tool for recording runs, capturing baselines, and blocking bad PRs before merge.

**What it is not:** It is not a hosted telemetry product, a generic output eval platform, or a framework lock-in layer. The local viewer helps inspect evidence, but the core product is behavioral regression gating.

---

## In 60 seconds

**1. Install Maida:**

```bash
uv tool install "maida-ai>=0.5"
```

**2. Run the bundled demo agent** (simulated; no repo clone, no API keys):

```bash
maida demo
```

**3. Open the timeline viewer:**

```bash
maida view
```

A browser tab opens showing the run timeline - tool calls, LLM calls, timing, warnings, and errors. Data is stored locally under `~/.maida/runs/<trace_id>/` as OTel-compatible spans plus metadata.

To watch the gate catch a regression end-to-end on canned data — baseline a good run, run a "refactored" agent that loops and calls a new tool, see the failing report with a PR-comment preview:

```bash
maida demo --regression
```

When you're ready to wire up your own project, `maida init` scaffolds a policy-v2
`.maida/policy.yaml` (add `--github` for a ready-to-edit CI workflow). Use
[`maida run`](regression-testing.md) to capture a reviewed baseline sample and
gate candidate trials.

---

## Demos and examples

| Example | Path | How to run |
|--------|------|------------|
| **Minimal agent** (pure Python) | `examples/minimal/` | `python examples/minimal/simple_agent.py` |
| **LangChain minimal** | [offline script](assets/examples/langchain-minimal.py) | `python langchain-minimal.py` |
| **OpenAI Agents minimal** | [offline script](assets/examples/openai-agents-minimal.py) | `python openai-agents-minimal.py` |
| **CrewAI minimal** | [offline script](assets/examples/crewai-minimal.py) | `CREWAI_DISABLE_TELEMETRY=true python crewai-minimal.py` |
| **Langfuse import** | [offline tutorial](https://github.com/maida-ai/maida-tutorials/tree/main/demos/langfuse_import) | Import synthetic traces, baseline a good run, and prove a regression fails |
| **LangChain customer support** (advanced) | `examples/langchain/` | Set API keys, then follow `_customer_support/README.md` |
| **Demos** (short scripts) | `examples/demo/` | `python examples/demo/pure_python.py` or `python examples/demo/langchain.py` |

After any run, open the timeline with `maida view`.

---

## Documentation

| Page | Description |
|------|-------------|
| [Getting started](getting-started.md) | Installation (uv/pip), quickstart, data dir, redaction |
| [Guardrails](guardrails.md) | Stop runaway runs with loop, count, and duration limits |
| [Capture Claude Code](claude-code.md) | Capture, import, and gate Claude Code sessions and isolated scenarios |
| [Regression testing](regression-testing.md) | Policy-v2 baseline sampling and candidate gate workflow |
| [Scheduled checks](scheduled-checks.md) | Read-only drift verdicts over completed native trace windows |
| [Gate draft extraction](extraction.md) | Derive inactive policy and baseline drafts for human review |
| [CLI](cli.md) | `demo`, `init`, `validate-trace`, `capture`, `import`, `scenario`, `run`, `extract`, `drift`, `list`, `view`, `export`, `baseline`, `accept`, `assert`, `diff` with options and exit codes |
| [Viewer](viewer.md) | Timeline UI usage, URL params, live refresh, and development |
| [SDK](sdk.md) | `@trace`, `traced_run`, `has_active_run`, `record_llm_call`, `record_tool_call`, `record_state` |
| [Integrations](integrations.md) | LangChain, OpenAI Agents, and CrewAI adapters, including failure behavior and limitations |
| [Import Langfuse traces](langfuse.md) | Read-only API import, mapping, local gating, privacy, and CI setup |
| [Architecture](architecture.md) | OTel span schema, storage layout, viewer API, loop detection |
| **Reference** | |
| [Trace format](reference/trace-format.md) | OTel span envelope, derived event types, payload schemas, meta.json (public contract) |
| [External emitter guide](reference/trace-emitter.md) | Produce and validate native Maida traces without an SDK |
| [Configuration](reference/config.md) | Env vars, YAML precedence, redaction, truncation, loop detection, guardrails |
| [Policy v2](reference/policy.md) | Metric kinds, sufficiency, directions, composition, and v1 migration |
