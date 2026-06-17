# Trace format (public contract)

This page describes the **public trace format** for Maida (`spec_version: "0.2"`). Traces use **OpenTelemetry spans** as the internal representation and are stored locally as **JSONL span records** plus a **run metadata file** (`meta.json`). The format is a public contract for local tooling and integrations.

**Versioning:** The trace format is versioned independently from the package version via `spec_version` (currently `"0.2"`). All Maida releases that use `spec_version "0.2"` share the same public trace contract. Additive changes (new optional fields, new event types, new span attributes) may be introduced without a spec version bump. Breaking changes will result in a new `spec_version`.

---

## Overview

- **Per run:** One directory `runs/<trace_id_hex>/` containing:
  - **spans.jsonl** - required append-only span log; one JSON object per line (one OTel span per line).
  - **meta.json** - required run metadata; created while the run is active and finalized when the root span ends.
- **Ordering:** Spans in `spans.jsonl` are in export order; `start_time` provides logical ordering.
- **Span hierarchy:** Root span (no `parent_span_id`) represents the run itself; child spans represent LLM calls, tool calls, state updates, warnings, and errors.

`trace_id_hex` is the 32-character lowercase hexadecimal OTel trace ID. The CLI still uses the user-facing argument name `RUN_ID` in several commands for compatibility; in current storage that value resolves to a full OTel `trace_id`, and short prefixes are accepted when they uniquely match a run.

### Files and readers

| Path or payload | Required? | Stable for external tools? | Notes |
|-----------------|-----------|----------------------------|-------|
| `runs/<trace_id>/meta.json` | Yes | Yes | Run discovery and summary metadata. The file may exist with `status: "running"` before the run finishes. |
| `runs/<trace_id>/spans.jsonl` | Yes | Yes | Append-only OTel span records. Read one JSON object per line and ignore fields you do not understand. |
| `maida export` JSON | Optional generated artifact | Yes | Portable single-file view with `spec_version`, `run`, and projected `events`. |
| Viewer API `/api/runs/{trace_id}/spans` | Runtime API | Yes | Returns `spec_version`, `trace_id`, raw `spans`, and projected `events`. |
| Temporary files such as `.meta.json.<pid>.tmp` | No | No | Internal atomic-write implementation detail; do not read or depend on them. |

External tools should prefer `maida export` or the viewer API when they need `spec_version` in the response envelope. Direct local-file readers should treat the directory layout and schemas below as the storage contract and should pair them with the documented `spec_version` for the Maida release they target.

**Redaction and truncation:** All span attributes and event payloads written to disk pass through redaction and truncation before being written. See the configuration reference for `redact`, `redact_keys`, and `max_field_bytes`.

---

## Span envelope (all spans)

Every OTel span is serialized as a single JSON object with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `trace_id` | string | 32-hex-character OTel trace ID |
| `span_id` | string | 16-hex-character OTel span ID |
| `parent_span_id` | string \| null | 16-hex-character parent span ID, or `null` for root |
| `name` | string | Span name (e.g. model name, tool name, run name) |
| `kind` | string | `INTERNAL`, `CLIENT`, `SERVER`, `PRODUCER`, `CONSUMER` |
| `start_time` | string | UTC ISO8601 with microsecond precision and trailing `Z` |
| `end_time` | string \| null | UTC ISO8601 with microsecond precision and trailing `Z` |
| `duration_ms` | integer \| null | Duration in milliseconds |
| `attributes` | object | Key-value pairs (string, bool, int, float values) |
| `events` | array | In-span events (name, timestamp, attributes) |
| `status_code` | string | `OK`, `ERROR`, or `UNSET` |
| `status_description` | string | Error description when status is `ERROR` |

### Derived event view

Consumers that need the v0.1-style event list can use `spans_to_events()` to project the span tree into a flat event list with `spec_version`, `event_type`, `ts`, `payload`, and related fields. This compatibility projection is what baselines, assertions, diffs, exports, and the local viewer use when they need event-like records.

Projection rules are part of the public contract at the event-type level: Maida preserves the event types and payload shapes below for consumer-facing workflows. The exact internal helper names and private implementation modules that perform the projection are not public API.

---

## Event types

| Type | Description |
|------|-------------|
| `RUN_START` | Run started (emitted by `@trace` / `traced_run`) |
| `RUN_END` | Run finished (ok or error) |
| `LLM_CALL` | One LLM invocation (model, prompt, response, usage) |
| `TOOL_CALL` | One tool invocation (name, args, result, status) |
| `STATE_UPDATE` | State snapshot or diff (e.g. between steps) |
| `ERROR` | Exception captured (type, message, stack) |
| `LOOP_WARNING` | Loop detection: repeated pattern in recent events |

---

## Payload schemas by event type

### RUN_START

```json
{
  "run_name": "optional string or null",
  "python_version": "3.11.7",
  "platform": "darwin | linux | win32",
  "cwd": "/path/to/cwd",
  "argv": ["script.py", "arg1"]
}
```

- **run_name** is set from: `MAIDA_RUN_NAME` (env), explicit `@trace("...")` / `@trace(name="...")` or `traced_run(name="...")`, or default `path:function - YYYY-MM-DD HH:MM`. See [configuration reference](config.md#run-name-env-only).
- **argv** may contain secrets; values for options matching redact keys are redacted before write.

### RUN_END

```json
{
  "status": "ok | error"
}
```

### LLM_CALL

```json
{
  "model": "string",
  "prompt": "string | object | null",
  "response": "string | object | null",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  },
  "provider": "openai | anthropic | local | unknown",
  "temperature": 0.0,
  "stop_reason": "string | null",
  "status": "ok | error",
  "error": "object | null"
}
```

- `usage` fields may be `null` if unknown.
- `prompt` and `response` may be redacted or truncated by config.
- When `status` is `"error"`, `error` is an object with `error_type`, `message`, and optional `stack` (same shape as ERROR event payload).

### TOOL_CALL

```json
{
  "tool_name": "string",
  "args": "object | string | null",
  "result": "object | string | null",
  "status": "ok | error",
  "error": "object | null"
}
```

- When `status` is `"error"`, `error` is an object with `error_type`, `message`, and optional `stack` (same shape as ERROR event payload).

### STATE_UPDATE

```json
{
  "state": "object | string | null",
  "diff": "object | string | null"
}
```

- `diff` is optional; may be omitted if not computed.

### ERROR

Error payloads use a consistent shape (same for standalone ERROR events and nested `error` in LLM_CALL/TOOL_CALL):

```json
{
  "error_type": "ExceptionClassName",
  "message": "string",
  "stack": "string | null"
}
```

- Use **`error_type`** (not `type`) for the exception class name.
- Guardrail aborts also use `ERROR`; consumers should use `error_type` values such as `GuardrailExceeded` or `LoopAbort` to distinguish intentional guardrail stops.

### LOOP_WARNING

```json
{
  "pattern": "string",
  "repetitions": 3,
  "window_size": 6,
  "evidence_event_ids": ["event_uuid_1", "event_uuid_2"]
}
```

- Emitted at most once per run per distinct pattern (deduplicated).
- If `stop_on_loop` guardrails are enabled, `LOOP_WARNING` is still written first and is then followed by `ERROR` and `RUN_END(status="error")`.

---

## meta.json schema

Each run has a `meta.json` file in its directory. It is created as running metadata when child spans are exported and overwritten with final metadata when the root span ends. `meta.json` itself does not currently include a top-level `spec_version`; `spec_version` is exposed by consumer-facing envelopes such as `maida export`, viewer API responses, and projected event records.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `trace_id` | string | 32-hex-character OTel trace ID |
| `run_name` | string \| null | Optional run label |
| `started_at` | string | UTC ISO8601 with microsecond precision and `Z` |
| `ended_at` | string \| null | Set when run finishes |
| `duration_ms` | integer \| null | Total run duration in ms |
| `status` | string | `"running"` \| `"ok"` \| `"error"` |
| `counts` | object | See below |

Writers may add optional fields in future `spec_version "0.2"` releases. Readers should preserve unknown fields when modifying metadata and ignore unknown fields when reading.

**counts** object:

```json
{
  "llm_calls": 0,
  "tool_calls": 0,
  "errors": 0,
  "loop_warnings": 0
}
```

### Lifecycle semantics

- **During a run:** child spans are appended to `spans.jsonl`; `meta.json` may appear with `status: "running"` so the local viewer can discover active runs.
- **On run end:** `meta.json` is overwritten with final `status`, `ended_at`, `duration_ms`, and `counts`.

---

## Versioning note

The trace format is a **public contract** versioned independently from the Maida package version. All releases using `spec_version "0.2"` share this format. Additive changes (new optional fields, new event types, new span attributes) are allowed without a spec version bump. Breaking changes (removing fields, changing types or semantics) will be accompanied by a new `spec_version`. The markdown reference on this page is canonical for external tooling.

### Stable versus internal

External tooling may rely on:

- The `runs/<trace_id>/meta.json` and `runs/<trace_id>/spans.jsonl` storage layout.
- The required fields, types, and lifecycle semantics documented on this page.
- The projected event types and payload shapes documented here.
- `maida export` and viewer API response envelopes that include `spec_version`.
- Short trace ID prefix resolution through the CLI.

External tooling should not rely on:

- Temporary atomic-write files, write timing, or filesystem implementation details beyond the documented lifecycle.
- Private Python module names, helper function names, or internal class names.
- Undocumented span attributes or event attributes staying unchanged.
- Legacy v0.1 files (`run.json`, `events.jsonl`) for new runs.

### CLI commands that read and write runs

- [`maida demo`](../cli.md#maida-demo) and instrumented SDK runs write local traces.
- [`maida list`](../cli.md#maida-list) reads `meta.json` to discover recent runs.
- [`maida view`](../cli.md#maida-view) reads run metadata and span data through the local viewer API.
- [`maida export`](../cli.md#maida-export) reads `meta.json` plus `spans.jsonl` and writes a portable JSON envelope with `spec_version`, run metadata, and projected events.
- [`maida baseline`](../cli.md#maida-baseline), [`maida assert`](../cli.md#maida-assert), and [`maida diff`](../cli.md#maida-diff) read trace IDs, span data, and projected events for regression checks.

### Changes from v0.1

- Storage files renamed: `run.json` -> `meta.json`, `events.jsonl` -> `spans.jsonl`
- Run directory keyed by OTel `trace_id` (32 hex chars) instead of UUIDv4 `run_id`
- Internal representation uses OTel span model with `trace_id`, `span_id`, `parent_span_id` hierarchy
- LLM calls use GenAI semantic convention attribute names (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.*`)
- Consumer-facing event view preserved via `spans_to_events()` projection
- `spec_version` bumped to `"0.2"`
