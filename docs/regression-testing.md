# Regression testing

Maida turns traced runs into behavioral regression tests. Use **run** to repeat
a non-deterministic agent and aggregate the evidence, **baseline** and
**assert** for the single-run workflow, **diff** to investigate changes, and
**accept** to update a reviewed baseline intentionally.

---

## Why

Agent behavior is non-deterministic. A prompt tweak, model upgrade, or tool change can silently increase token usage, add unexpected tool calls, or introduce loops. `maida run` repeats the agent and measures how reliably its traces satisfy the same policy, while `maida assert` remains available for a completed single run.

---

## Workflow overview

```
1. Run your known-good agent   python your_agent.py
2. Capture a baseline          maida baseline
3. Gate repeated trials        maida run path/to/agent.py --baseline .maida/baselines/my_agent.json
4. Inspect a trial             maida view <TRACE_ID>
5. If expected, accept         maida accept <TRACE_ID> --baseline .maida/baselines/my_agent.json --reason "..."
```

`baseline`, `assert`, `diff`, and `accept` default to the latest run when no run ID is given; pass an OTel trace ID or short prefix to target a specific run.

To see the whole workflow on canned data first, run `maida demo --regression`.

---

## Step 1: Capture a baseline

After a successful run that represents the expected behavior:

```bash
maida baseline <RUN_ID>
```

This creates a JSON snapshot at `.maida/baselines/<run_name>.json` (or the run ID if no name was set). Use `--out` to control the path:

```bash
maida baseline a1b2c3d4 --out baselines/support_agent_v1.json
```

**What gets captured:**

| Field | Description |
|---|---|
| `schema_version` | Baseline format version (`"0.2"`) |
| `source_run_id` | The resolved OTel trace ID this baseline was created from |
| `source_run_name` | Run name (if set) |
| `summary` | Aggregate metrics: total events, LLM calls, tool calls, errors, loop warnings, duration, tokens |
| `tool_path` | Sorted list of unique tool names used |
| `tool_call_counts` | Per-tool invocation counts |
| `llm_models_used` | Models seen in LLM_CALL events |
| `event_type_sequence` | Ordered list of event types |
| `guardrail_events` | Any guardrail-triggered events |
| `final_status` | Run status (`"ok"` or `"error"`) |

Check the baseline file into version control so the team shares the same reference point.

---

## Step 2: Assert against a baseline

```bash
maida assert <RUN_ID> --baseline .maida/baselines/my_agent.json
```

Exit codes: `0` = all checks pass, `1` = one or more checks failed, `2` = run or baseline not found, `10` = internal error.

### What gets checked

Checks are controlled by the **assertion policy** — a combination of a policy YAML file and CLI flags. By default, if a baseline is provided, every numeric metric is compared with a 50% tolerance. You can tighten or customize this with a policy file or CLI flags.

### Standalone thresholds (no baseline needed)

You can assert without a baseline by setting hard caps:

```bash
maida assert <RUN_ID> --max-steps 80 --max-tool-calls 30 --no-loops
```

### Combining baseline and thresholds

When both a baseline and a `max_*` threshold are set, the effective limit is the **lesser** of the two:

```
limit = min(baseline_value * (1 + tolerance), max_value)
```

See the [Policy YAML reference](reference/policy.md#how-thresholds-work) for the full decision table.

---

## Repeat the agent with a statistical gate

For a non-deterministic agent, run the script several times instead of treating
one execution as representative:

```bash
maida run path/to/agent.py \
  --baseline .maida/baselines/my_agent.json \
  --trials 3 \
  --confidence-level 0.95 \
  --pass-rate-threshold 0.90
```

Each trial runs in a fresh subprocess and a fresh temporary copy of the
repository. The copy contains tracked files and non-ignored working-tree files,
including uncommitted work you are testing, but excludes `.git` metadata and
ignored build artifacts. Each trial also gets isolated Maida storage. Once a
trial completes, its trace is preserved in your configured Maida store so you
can inspect it with `maida view` or compare it with `maida diff`.

The gate evaluates every configured check in every trial and reports one of
three verdicts per check:

- **PASS** — the evidence supports a pass rate at or above the configured
  threshold.
- **FAIL** — the evidence supports a pass rate below the threshold.
- **INCONCLUSIVE** — the confidence interval crosses the threshold, so the
  collected trials do not distinguish pass from fail.

The overall verdict is `FAIL` if any check fails, otherwise `INCONCLUSIVE` if
any check is inconclusive, otherwise `PASS`. Maida uses a two-sided Wilson
confidence interval: a check passes when the interval's lower bound meets the
threshold, fails when its upper bound is below the threshold, and is
inconclusive when the interval crosses the threshold. Two compatibility rules
apply to small samples:

- At `N=1`, the lone trial is a binary pass or fail (`single_trial_binary`).
- At the default `N=3`, unanimous outcomes are a pass or fail
  (`small_n_unanimous`); mixed outcomes use the Wilson rule.

The unanimous `N=3` rule is a temporary compatibility policy, not a claim that
three runs provide the same statistical evidence as a larger sample. Increase
`--trials` when the cost of a wrong decision justifies more evidence. Runtime
and agent/API usage grow with the number of trials, so choose the sample count
with CI latency and model/tool cost in mind.

`FAIL` exits `1`. Both `PASS` and `INCONCLUSIVE` exit `0`; consumers should read
the verdict rather than treating every zero exit as a statistical pass.

### Machine-readable report

Use JSON on stdout, or write a sidecar while rendering text or Markdown:

```bash
maida run path/to/agent.py \
  --baseline .maida/baselines/my_agent.json \
  --format markdown \
  --json-out maida-report.json
```

The versioned JSON contract has `report_version: "1"` and these top-level
fields:

```json
{
  "report_version": "1",
  "trials_requested": 3,
  "verdict": "INCONCLUSIVE",
  "passed": null,
  "metadata": {
    "trials_requested": 3,
    "trials_completed": 3,
    "confidence_level": 0.95,
    "pass_rate_threshold": 0.9
  },
  "trials": [],
  "aggregate_results": []
}
```

Each `trials` entry identifies the trial, trace, run name, process exit code,
single-trial result, check results, and baseline diff. Each
`aggregate_results` entry contains `check_name`, `verdict`, `trials`,
`successes`, `pass_rate`, `confidence_interval`, `confidence_level`,
`pass_rate_threshold`, `decision_rule`, and `trial_outcomes`. The compatibility
field `passed` is `true` for `PASS`, `false` for `FAIL`, and `null` for
`INCONCLUSIVE`; use `verdict` in new integrations.

---

## Step 3: Use a policy file

Instead of passing many CLI flags, commit a `.maida/policy.yaml` file:

```yaml
assert:
  # Statistical gate defaults.
  trials: 3
  confidence_level: 0.95
  pass_rate_threshold: 0.90

  # Allowed growth vs baseline (0.5 = +50%).
  step_tolerance: 0.5
  tool_call_tolerance: 0.5
  cost_tolerance: 0.5
  duration_tolerance: 0.5

  # Strict checks (uncomment to opt in):
  # no_loops: true
  # no_guardrails: true
  # no_new_tools: true
  # expect_status: ok
```

This starter policy only applies numeric tolerance checks when a baseline is
provided. Strict checks require uncommenting the relevant rule or passing the
matching CLI flag.

`maida run` and `maida assert` auto-detect `.maida/policy.yaml` in the current directory. To use a different path:

```bash
maida assert <RUN_ID> --baseline baseline.json --policy ci-policy.yaml
```

For a repeated gate, the statistical settings can also be overridden directly:

```bash
maida run path/to/agent.py \
  --policy ci-policy.yaml \
  --trials 30 \
  --confidence-level 0.99 \
  --pass-rate-threshold 0.95
```

**Precedence:** CLI flags > policy file > defaults. See the [full policy reference](reference/policy.md) for all fields, threshold semantics, and override rules.

---

## Output formats

Use `--format` (`-f`) to choose the output format.

### Text (default)

```bash
maida assert <RUN_ID> --baseline baseline.json
```

```
  ✓ step_count: 42 steps (baseline: 38, tolerance: 50%)
  ✓ tool_calls: 12 tool calls (baseline: 10, tolerance: 50%)
  ✗ no_loops: 2 loop warning(s) detected
  ✓ expect_status: status is 'ok'

RESULT: FAILED (1 of 4 checks failed)
```

### JSON

```bash
maida assert <RUN_ID> --baseline baseline.json --format json
```

```json
{
  "run_id": "a1b2c3d4e5f67890a1b2c3d4e5f67890",
  "baseline_run_id": "e5f6a7b8c9d001122334455667788990",
  "passed": false,
  "results": [
    {
      "check_name": "step_count",
      "passed": true,
      "message": "42 steps (baseline: 38, tolerance: 50%)",
      "expected": "57",
      "actual": "42"
    },
    {
      "check_name": "no_loops",
      "passed": false,
      "message": "2 loop warning(s) detected",
      "expected": null,
      "actual": "2"
    }
  ]
}
```

### Markdown

Designed for GitHub PR comments and step summaries:

```bash
maida assert --baseline baseline.json --format markdown
```

```markdown
## ❌ Maida gate: agent behavior regressed

**1 of 4 checks failed** · run `a1b2c3d4` vs baseline `e5f6a7b8`

| Check | Expected | Actual | Details |
|---|---|---|---|
| ❌ `no_loops` | — | 2 | 2 loop warning(s) detected |

<details>
<summary>✅ 3 passing checks</summary>
...
</details>

### What changed vs baseline

| Metric | Baseline | Current | Change |
|---|---|---|---|
| tool_calls | 10 | 14 | +40% |
| loop_warnings | 0 | 2 | NEW |

**Tool changes:**
- ➕ `web_search` — new tool, not in baseline

### Next steps

- Inspect the full diff: `maida diff a1b2c3d4 --baseline baseline.json`
- Open the trace locally: `maida view a1b2c3d4`
- If this behavior change is intentional, accept it explicitly: `maida accept a1b2c3d4 --baseline baseline.json --reason "..."`
- Review and commit the baseline diff; otherwise fix the agent behavior and rerun the gate.
```

The report leads with the verdict, lists failed checks first with expected vs actual values, collapses passing checks, and — when a baseline is provided — embeds the structural diff, concise next steps, and a copy-pasteable local-repro snippet.

---

## Step 4: Drill into failures with diff

When `maida assert` fails, use `maida diff` to see exactly what changed.

### Diff against a baseline

```bash
maida diff --baseline .maida/baselines/my_agent.json
```

### Diff two runs directly

```bash
maida diff <RUN_A> <RUN_B>
```

### Sample output

```
Run comparison: a1b2c3d4 vs e5f6a7b8

Summary:
  total_events: 38 -> 42 (+11%)
  tool_calls: 10 -> 14 (+40%)
  loop_warnings: 0 -> 2 (NEW)

Tool path changes:
  + web_search (new)

Event type distribution:
  LLM_CALL: 8 -> 8
  TOOL_CALL: 10 -> 14 (+40%)
  LOOP_WARNING: 0 -> 2 (NEW)
```

The diff shows summary-level metric changes, new or removed tools, and shifts in the event type distribution.

---

## Step 5: Accept intentional changes

If the diff and trace show an intentional behavior change, update the checked-in baseline explicitly:

```bash
maida accept --baseline .maida/baselines/my_agent.json --reason "expected retrieval tool split"
git diff .maida/baselines/my_agent.json
```

`maida accept` rewrites the baseline from the selected run and records acceptance metadata in the JSON: reason, timestamp, Maida version, source run ID, previous baseline source run ID, and previous baseline SHA-256. If the selected run already matches the baseline structurally, it exits `0` and leaves the file untouched.

Always inspect the trace and Git diff before committing the updated baseline. Accepting a baseline change means the new behavior is what future PRs will be gated against; if the change is not intentional, fix the agent and rerun `maida assert` instead.

---

## GitHub Actions example

The easiest path is the packaged action, [maida-ai/maida-assert](https://github.com/maida-ai/maida-assert) — scaffold it with `maida init --github`. It runs repeated trials, evaluates the configured gate, and publishes the regression report in the pull request.

To wire it up by hand instead, run the statistical gate against the checked-in baseline:

```yaml
- name: Gate agent behavior
  run: |
    maida run path/to/agent.py \
      --baseline .maida/baselines/my_agent.json \
      --format markdown >> "$GITHUB_STEP_SUMMARY"
```

If the gate fails, the step exits with code 1 and the Markdown report appears in the GitHub Actions step summary. An inconclusive result is visible in the report but exits with code 0.

---

## Related docs

- [Policy YAML reference](reference/policy.md) — all assertion fields, threshold semantics, CLI-to-YAML mapping
- [CLI reference](cli.md) — `baseline`, `assert`, `diff` command details
- [Guardrails](guardrails.md) — runtime limits (separate from post-hoc assertions)
