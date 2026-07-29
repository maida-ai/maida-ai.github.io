# CLI

The `maida` CLI runs the bundled demo, executes repeatable statistical gates, scaffolds a project, lists trace-backed runs, starts the local viewer, exports runs to JSON, updates baselines intentionally, and gates runs against baselines. Storage is under `~/.maida/` by default (overridable with `MAIDA_DATA_DIR`). Current runs are identified by OTel trace IDs; the CLI keeps the user-facing argument name `RUN_ID` for compatibility and accepts short trace ID prefixes. For all configuration options and precedence, see the [configuration reference](reference/config.md).

Commands that take a run ID (`assert`, `baseline`, `accept`, `export`, `diff`) default to the **latest run** when the ID is omitted. The selected run is announced on stderr so stdout stays machine-readable.

---

## `maida demo`

Runs a bundled simulated customer-support agent and records a trace. No network, no API keys; all LLM/tool data is canned and nothing leaves your machine.

**Usage:**

```bash
maida demo [--regression]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--regression` | Full story: baseline a known-good run, run a "refactored" agent that loops, calls a new tool, and burns more tokens, then show the failing gate report and a PR-comment preview. Writes the baseline to `.maida/baselines/demo-support-agent.json`. |

**Exit codes:** `0` success (including when the demo gate intentionally fails); `10` internal error.

---

## `maida run`

Runs an agent script repeatedly in isolated workspaces and aggregates the
configured behavioral checks into a statistical gate verdict. Use it when a
single successful execution is not enough evidence for a non-deterministic
agent.

**Usage:**

```bash
maida run AGENT_SCRIPT [options]
```

**Arguments / options:**

| Argument/Option | Default | Description |
|---|---|---|
| `AGENT_SCRIPT` | *(required)* | Python agent script to execute once per trial |
| `--trials` | `3` | Number of independent trials |
| `--confidence-level` | `0.95` | Confidence level for the two-sided Wilson interval |
| `--pass-rate-threshold` | `0.90` | Minimum acceptable pass rate for each check |
| `--baseline` | - | Baseline JSON file used by each trial's assertions |
| `--policy` | `.maida/policy.yaml` (auto-detected) | Policy YAML file with gate settings and assertion thresholds |
| `--max-steps` | - | Override the policy's maximum event count for this invocation |
| `--format` | `text` | Report format: `text`, `json`, or `markdown` |
| `--json-out` | - | Also write the complete JSON report to this path, independent of the display format |

`--trials`, `--confidence-level`, `--pass-rate-threshold`, and assertion
options such as `--max-steps` override values from the policy file.

**Examples:**

```bash
# Use the policy defaults and print a text report
maida run path/to/agent.py --baseline .maida/baselines/my_agent.json

# Increase the evidence and keep both Markdown and machine-readable output
maida run path/to/agent.py \
  --trials 30 \
  --confidence-level 0.95 \
  --pass-rate-threshold 0.90 \
  --baseline .maida/baselines/my_agent.json \
  --format markdown \
  --json-out maida-report.json
```

Every trial starts a fresh subprocess in a fresh temporary workspace copied
from the caller's tracked files and non-ignored working-tree files. Git
metadata and ignored files are excluded. Trial traces are isolated during
execution, then completed traces are preserved in the caller's Maida store for
`maida view` and `maida diff`.

The verdict is `PASS`, `FAIL`, or `INCONCLUSIVE`. `FAIL` exits `1`; `PASS` and
`INCONCLUSIVE` exit `0` so an uncertain estimate remains visible without being
reported as a confirmed regression. Missing inputs exit `2`, and internal
errors exit `10`.

JSON output uses `report_version: "1"`. It includes the overall `verdict`, a
tri-state `passed` compatibility field, run metadata, every trial and its
baseline diff, and `aggregate_results` with the observed pass rate, confidence
interval, threshold, decision rule, and trial outcomes for each check.

See [Regression testing](regression-testing.md#repeat-the-agent-with-a-statistical-gate)
for verdict semantics and the small-sample compatibility rules.

---

## `maida init`

Scaffolds Maida configuration in the current directory. Never overwrites existing files unless `--force` is given; safe to re-run.

**Usage:**

```bash
maida init [--github] [--force]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--github` | Also write `.github/workflows/maida.yml` using the [maida-assert action](https://github.com/maida-ai/maida-assert) |
| `--force` | Overwrite existing files |

**Files written:**

- `.maida/policy.yaml` — commented starter policy with 50% baseline tolerances; strict checks such as `no_loops`, `no_guardrails`, `no_new_tools`, and `expect_status: ok` are shown as opt-ins
- `.github/workflows/maida.yml` (with `--github`) — PR check running your traced agent and posting the regression report as a sticky comment

**Exit codes:** `0` success; `10` internal error.

---

## `maida list`

Lists recent runs (by `started_at` descending).

**Usage:**

```bash
maida list [--limit N] [--json]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--limit`, `-n` | 20 | Maximum number of runs to list |
| `--json` | - | Output machine-readable JSON |

**Examples:**

```bash
maida list
maida list --limit 5
maida list --json
```

**Exit codes:** `0` success; `10` internal error.

**Text columns:** run_id (short trace ID), run_name, started_at, duration_ms, llm_calls, tool_calls, status.

---

## `maida view`

Starts the local viewer server and optionally opens the browser. Default bind: `127.0.0.1:8712`.

**Usage:**

```bash
maida view [RUN_ID] [--host HOST] [--port PORT] [--no-browser] [--json]
```

**Arguments / options:**

| Argument/Option | Default | Description |
|-----------------|---------|-------------|
| `RUN_ID` | (latest) | Run to view; can be a short trace ID prefix (e.g. first 8 hex chars) |
| `--host`, `-H` | 127.0.0.1 | Bind host |
| `--port`, `-p` | 8712 | Bind port |
| `--no-browser` | - | Do not open the browser; only start the server |
| `--json` | - | Print run_id, url, status as JSON, then start server |

**Examples:**

```bash
maida view
maida view a1b2c3d4
maida view --port 9000 --no-browser
maida view --json
```

**Exit codes:** `0` success; `2` run not found (or no runs); `10` internal error.

With `--json`, output shape:

```json
{
  "spec_version": "0.2",
  "run_id": "...",
  "url": "http://127.0.0.1:8712/?run_id=...",
  "status": "serving"
}
```

The `run_id` value is the resolved OTel trace ID.

---

## `maida export`

Exports one run to a single JSON file (run metadata + projected events array).

**Usage:**

```bash
maida export [RUN_ID] --out FILE
```

**Arguments / options:**

| Argument/Option | Description |
|---|---|
| `RUN_ID` | Run to export; can be a short trace ID prefix. Defaults to the latest run when omitted |
| `--out`, `-o` | Output file path (JSON) |

**Examples:**

```bash
maida export --out trace-export.json     # latest run
maida export a1b2c3d4 -o ./exports/trace-export.json
```

**Exit codes:** `0` success; `2` run not found; `10` internal error.

Output file contains: `spec_version`, `run` (run metadata), and `events` (array of event objects projected from spans).

---

## `maida baseline`

Captures a baseline snapshot from a completed run. The snapshot records structural metrics (event counts, tool path, token usage, duration, etc.) that `maida assert` can later compare against. See [Regression testing](regression-testing.md) for the full workflow.

**Usage:**

```bash
maida baseline [RUN_ID] [--out PATH]
```

**Arguments / options:**

| Argument/Option | Default | Description |
|---|---|---|
| `RUN_ID` | *(latest run)* | OTel trace ID or prefix to snapshot |
| `--out`, `-o` | `.maida/baselines/<run_name>.json` | Output path for the baseline JSON file |

**Examples:**

```bash
maida baseline                       # snapshot the latest run
maida baseline a1b2c3d4 --out baselines/support_agent_v1.json
```

**Exit codes:** `0` success; `2` run not found; `10` internal error.

The output file is a JSON object containing `schema_version`, `source_run_id` (the resolved OTel trace ID), summary metrics, `tool_path`, `tool_call_counts`, `llm_models_used`, `event_type_sequence`, and `final_status`. Check it into version control to share the baseline with your team.

---

## `maida accept`

Updates an existing baseline from a completed run when a behavior change is intentional. Use it after inspecting `maida diff` and `maida view`; do not accept a regression just to make CI pass.

**Usage:**

```bash
maida accept [RUN_ID] --baseline PATH --reason TEXT
```

**Arguments / options:**

| Argument/Option | Default | Description |
|---|---|---|
| `RUN_ID` | *(latest run)* | OTel trace ID or prefix to accept |
| `--baseline`, `-b` | *(required)* | Existing baseline JSON file to update |
| `--reason`, `--message`, `-m` | *(required)* | Human-readable reason for accepting the change |

**Examples:**

```bash
maida diff --baseline .maida/baselines/my_agent.json
maida view
maida accept --baseline .maida/baselines/my_agent.json --reason "expected retrieval tool split"
git diff .maida/baselines/my_agent.json
```

**Exit codes:** `0` baseline updated or already matched; `2` run or baseline not found, invalid baseline, invalid run, or missing reason; `10` internal error.

When the accepted run changes baseline behavior, the baseline JSON is rewritten with the same structural fields produced by `maida baseline` plus an `acceptance` object containing the reason, timestamp, Maida version, source run ID, previous baseline source run ID, and previous baseline SHA-256. If the selected run already matches the baseline structurally, Maida prints `no update written` and leaves the file untouched.

---

## `maida assert`

Asserts that a completed run meets behavioral policy checks. Returns exit code `0` when all checks pass and `1` when any check fails, making it suitable for CI gates.

**Usage:**

```bash
maida assert [RUN_ID] [options]
```

**Arguments / options:**

| Argument/Option | Default | Description |
|---|---|---|
| `RUN_ID` | *(latest run)* | OTel trace ID or prefix to check |
| `--baseline`, `-b` | - | Baseline JSON file to compare against |
| `--policy` | `.maida/policy.yaml` (auto-detected) | Policy YAML file with assertion thresholds |
| `--max-steps` | - | Max total events allowed |
| `--step-tolerance` | `0.5` | Fractional tolerance for step count |
| `--max-tool-calls` | - | Max tool calls allowed |
| `--tool-call-tolerance` | `0.5` | Fractional tolerance for tool calls |
| `--no-new-tools` | `false` | Fail if run uses tools not in baseline |
| `--no-loops` | `false` | Fail if any LOOP_WARNING present |
| `--no-guardrails` | `false` | Fail if any guardrail was triggered |
| `--max-cost-tokens` | - | Max total tokens allowed |
| `--cost-tolerance` | `0.5` | Fractional tolerance for token cost |
| `--max-duration-ms` | - | Max run duration in ms |
| `--duration-tolerance` | `0.5` | Fractional tolerance for duration |
| `--expect-status` | - | Expected run status (`ok` or `error`) |
| `--format`, `-f` | `text` | Output format: `text`, `json`, or `markdown` |

**Precedence:** CLI flags override the policy file, which overrides defaults. See the [Policy YAML reference](reference/policy.md) for the full override rules and threshold semantics.

**Examples:**

```bash
# Assert the latest run against a baseline with default tolerances
maida assert --baseline .maida/baselines/my_agent.json

# Assert a specific run with standalone thresholds (no baseline)
maida assert a1b2c3d4 --max-steps 80 --max-tool-calls 30 --no-loops

# Assert using a policy file
maida assert --baseline baseline.json --policy ci-policy.yaml

# Markdown output for GitHub PR comments / step summaries
maida assert --baseline baseline.json --format markdown
```

**Exit codes:** `0` all checks passed; `1` one or more checks failed; `2` run or baseline not found; `10` internal error.

When a baseline is provided, the markdown report leads with a pass/fail verdict, lists failed checks first with expected vs actual values, collapses passing checks, and embeds a **What changed vs baseline** section (metric deltas, new/removed tools, model changes) plus next steps that point to `maida diff`, `maida view`, and `maida accept --reason` when the change is intentional. The text report appends the structural diff on failure.

---

## `maida diff`

Compares two runs, or a run against a baseline, showing structural differences in summary metrics, tool path, and event type distribution. Useful for understanding what changed when `maida assert` reports a failure. See [Regression testing](regression-testing.md) for the workflow.

**Usage:**

```bash
maida diff [RUN_A] [RUN_B] [--baseline FILE] [--format FORMAT]
```

Exactly one of `RUN_B` or `--baseline` must be provided.

**Arguments / options:**

| Argument/Option | Description |
|---|---|
| `RUN_A` | First OTel trace ID or prefix. Defaults to the latest run when omitted |
| `RUN_B` | Second OTel trace ID or prefix (mutually exclusive with `--baseline`) |
| `--baseline`, `-b` | Baseline JSON file to compare against (mutually exclusive with `RUN_B`) |
| `--format`, `-f` | Output format: `text` (default) |

**Examples:**

```bash
# Compare two runs
maida diff a1b2c3d4 e5f6a7b8

# Compare the latest run against a baseline
maida diff --baseline .maida/baselines/my_agent.json
```

**Exit codes:** `0` success; `2` run or baseline not found; `10` internal error.

**Text output sections:**

- **Summary** — metric-by-metric comparison with percentage change (e.g. `tool_calls: 10 -> 14 (+40%)`)
- **Tool path changes** — new (`+`) and removed (`-`) tools
- **Event type distribution** — per-event-type counts with percentage change
