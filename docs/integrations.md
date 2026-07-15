# Integrations

## Philosophy

Maida is **framework-agnostic** at the core. The SDK is a thin layer: you call `@trace` and `record_llm_call` / `record_tool_call` / `record_state` from any Python code. No required dependency on LangChain, OpenAI Agents SDK, or others.

**Adapters** are thin translation layers: they hook into a framework's callbacks and emit Maida events. They do not lock you into that framework for the rest of your app.

Every supported adapter preserves the same core contract:

- Framework packages are optional and loaded only when their adapter is imported.
- Equivalent LLM and tool activity becomes the same `LLM_CALL` and `TOOL_CALL` structure, regardless of framework.
- Framework-specific details stay in `meta`; adapters do not add framework-specific event types.
- Payloads and metadata pass through Maida's redaction and truncation before they are stored.

| Adapter | Install from PyPI | Activate |
|---|---|---|
| LangChain / LangGraph | `pip install "maida-ai[langchain]"` | Create `LangChainCallbackHandler` and pass it in `config["callbacks"]` |
| OpenAI Agents SDK | `pip install "maida-ai[openai]"` | Import `maida.integrations.openai_agents` |
| CrewAI | `pip install "maida-ai[crewai]"` | Import `maida.integrations.crewai` |

---

## Available

### LangChain / LangGraph callback handler

**Status: available.** An optional callback handler lives at `maida.integrations.langchain`. It records LLM calls and tool calls to the active Maida run automatically.

**Requirements:** `langchain-core` must be installed. Install Maida with the LangChain extra:

```bash
pip install "maida-ai[langchain]"
```

If `langchain-core` is missing, accessing `LangChainCallbackHandler` raises an `ImportError` that identifies the LangChain extra. Importing core `maida` remains safe.

**Usage:**

```python
from maida import trace
from maida.integrations import LangChainCallbackHandler

@trace
def run_agent():
    handler = LangChainCallbackHandler()
    config = {"callbacks": [handler]}

    # Use config with any LangChain chain, LLM, or tool:
    result = my_chain.invoke(input_data, config=config)
    return result
```

The handler captures:

- **LLM calls** (`on_llm_start` / `on_chat_model_start` -> `on_llm_end`): records model name, prompt, response, and token usage via `record_llm_call`.
- **Tool calls** (`on_tool_start` -> `on_tool_end` / `on_tool_error`): records tool name, args, result, and error status via `record_tool_call`.

The [offline LangChain example](assets/examples/langchain-minimal.py) uses `FakeListLLM` and a local tool, so it requires no API key or network call:

```bash
python langchain-minimal.py
maida view
```

The normal run has this structural signature:

- event sequence: `RUN_START -> TOOL_CALL -> LLM_CALL -> RUN_END`
- tool sequence: `lookup` (one call)
- LLM calls: one `FakeListLLM` call
- terminal status: `ok`

Use its deterministic regression mode to see the pre-merge gate catch one extra tool call:

```bash
# Capture the known-good behavior.
python langchain-minimal.py
maida baseline --out langchain-baseline.json

# Simulate a code change that repeats the local lookup.
python langchain-minimal.py --regression
maida assert --baseline langchain-baseline.json --tool-call-tolerance 0
```

The regression signature is `RUN_START -> TOOL_CALL -> TOOL_CALL -> LLM_CALL -> RUN_END`, with the tool sequence `lookup -> lookup`, one `FakeListLLM` call, and terminal status `ok`. The final command reports the tool-call increase from 1 to 2 and exits with code `1`, so the same check can block a pull request even though the agent itself completed successfully.

For a multi-node graph, loop failure, and guardrail walkthrough, continue with the [full LangGraph tutorial](https://github.com/maida-ai/maida-tutorials/blob/main/LangChain/Mock%20LangGraph%20Agent.ipynb).

**Guardrails (e.g. `stop_on_loop`) with LangChain / LangGraph:**
All guardrails work with the callback handler. When a guardrail fires, the handler raises `_MaidaAbortSignal` (a `BaseException`) which bypasses both LangChain's callback error handling and LangGraph's graph executor — stopping the run immediately and preventing further token-wasting LLM calls. See [Guardrails](guardrails.md) for details. To reuse a handler across runs, call `handler.reset()` between runs.

**Notes:**

- The handler requires an active Maida run - wrap your entrypoint with `@trace` or set `MAIDA_IMPLICIT_RUN=1`.
- Only callbacks delivered to this handler are recorded. Calls made without the handler in their callback config are invisible to Maida.
- Tool errors are recorded as `TOOL_CALL` events with `status="error"` and include the error message.
- LLM errors are recorded as `LLM_CALL` events with `status="error"` (not as separate `ERROR` events).

---

### OpenAI Agents SDK tracing adapter

**Status: available.** An optional adapter lives at `maida.integrations.openai_agents`. Importing it registers an OpenAI Agents tracing processor that forwards SDK generation, function, and handoff spans into the active Maida run.

**Requirements:** `openai-agents` must be installed. Install Maida with the OpenAI extra:

```bash
pip install "maida-ai[openai]"
```

If `openai-agents` is not installed, importing the integration raises a clear `ImportError` with install instructions. The integration is optional; the core package does not depend on it.

**Usage:**

```python
from maida import trace
from maida.integrations import openai_agents  # registers hooks


@trace
def run_agent():
    # ... OpenAI Agents SDK code ...
    pass
```

The adapter captures:

- **LLM calls** (`GenerationSpanData`): records model, prompt, response, and usage via `record_llm_call`.
- **Tool calls** (`FunctionSpanData`): records tool name, args, result, and error status via `record_tool_call`.
- **Handoffs** (`HandoffSpanData`): records a `TOOL_CALL` named `handoff`, with framework-specific details stored in `meta`.

The [offline OpenAI Agents example](assets/examples/openai-agents-minimal.py) constructs SDK tracing spans with fake data and replaces the SDK processor list with Maida's processor. It requires no API key or model call:

```bash
pip install "maida-ai[openai]"
python openai-agents-minimal.py
maida view
```

The normal run has this structural signature:

- event sequence: `RUN_START -> LLM_CALL -> TOOL_CALL(lookup_docs) -> TOOL_CALL(handoff) -> RUN_END`
- tool sequence: `lookup_docs -> handoff` (two calls)
- LLM calls: one `fake-model` call
- terminal status: `ok`

Capture that known-good behavior and confirm it passes the gate:

```bash
python openai-agents-minimal.py
maida baseline --out openai-agents-baseline.json
maida assert --baseline openai-agents-baseline.json
```

Then use the deterministic regression mode to repeat the local documentation lookup and run a strict tool-call check:

```bash
python openai-agents-minimal.py --regression
maida assert --baseline openai-agents-baseline.json --tool-call-tolerance 0
```

The regression signature is `RUN_START -> LLM_CALL -> TOOL_CALL(lookup_docs) -> TOOL_CALL(lookup_docs) -> TOOL_CALL(handoff) -> RUN_END`, with the tool sequence `lookup_docs -> lookup_docs -> handoff`, one `fake-model` call, and terminal status `ok`. The final command reports the tool-call increase from 2 to 3 and exits with code `1`, so the gate catches the structural regression even though the agent itself completed successfully.

For an end-to-end agent workflow and guardrail walkthrough, continue with the [full OpenAI Agents tutorial](https://github.com/maida-ai/maida-tutorials/blob/main/OpenAI/Mock%20OpenAI%20Agent.ipynb).

**Guardrails with OpenAI Agents SDK:**
All guardrails work with the tracing processor. When a guardrail fires, the processor raises `_MaidaAbortSignal` (a `BaseException`) which bypasses the SDK's `except Exception` error handling — stopping the run immediately:

```python
from maida import trace, LoopAbort

@trace(stop_on_loop=True)
def run_agent():
    result = Runner.run_sync(agent, input)
    return result
```

As a defensive fallback, the exception is also stored on `PROCESSOR.abort_exception` with a `PROCESSOR.raise_if_aborted()` convenience method.

**Notes:**

- The adapter records events only while an explicit Maida run is active; wrap your entrypoint with `@trace` or `traced_run(...)`.
- Importing the adapter registers a process-wide tracing processor. If your application later replaces the SDK processor list, include `openai_agents.PROCESSOR` in the replacement list.
- Framework-specific span details stay in `meta.openai_agents.*`, not the event payload.
- The example uses low-level SDK tracing spans with deterministic fake data, so it needs no API key and makes no model calls.

---

### CrewAI execution-hook adapter

**Status: available.** An optional adapter lives at `maida.integrations.crewai`. Importing it registers CrewAI execution hooks that automatically record LLM and tool calls into the active Maida run.

**Requirements:** `crewai[tools]` must be installed. Install Maida with the CrewAI extra:

```bash
pip install "maida-ai[crewai]"
```

If `crewai` is not installed, importing the integration raises a clear `ImportError` with install instructions.

**Usage:**

```python
import maida
from maida.integrations import crewai as maida_crewai  # registers hooks

@maida.trace
def run_crew():
    # ... your CrewAI crew.kickoff() or flow.kickoff() ...
    pass
```

The adapter captures:

- **LLM calls** (`before_llm_call` / `after_llm_call`): records model, prompt messages, and response via `record_llm_call`.
- **Tool calls** (`before_tool_call` / `after_tool_call`): records tool name, args, result, and timing via `record_tool_call`.

Framework-specific context (agent role, task description, executor ID) is stored in `meta.crewai.*`.

The [offline CrewAI example](assets/examples/crewai-minimal.py) sends fake data through CrewAI's public hook contexts, so it exercises the adapter without starting a crew, LLM, or API call. The environment flag disables CrewAI's separate anonymous package telemetry for this deterministic run:

```bash
CREWAI_DISABLE_TELEMETRY=true python crewai-minimal.py
maida view
```

**Notes:**

- The adapter requires an active Maida run — wrap your entrypoint with `@trace` or `traced_run(...)`.
- Hook ordering caveat: if another before-hook returns `False` and blocks execution, that specific call may not be captured.
- CrewAI's current hooks do not expose token usage, so CrewAI `LLM_CALL` events record `usage` as unknown.
- If a run ends before an after-hook arrives, the pending call is recorded with `status="error"` and `completion="missing_after_hook"` in its CrewAI metadata.
- The fake-hook-only example unregisters CrewAI's event-bus exit callback to avoid a current one-shot interpreter-shutdown hang. That cleanup is specific to the example and should not be copied into a long-lived Crew or Flow application.

---

## Failure cases and data safety

### Missing optional dependencies

Core Maida does not import any framework. The optional dependency is checked only when its adapter is accessed:

```bash
python -c "from maida.integrations import LangChainCallbackHandler"
python -c "from maida.integrations import openai_agents"
python -c "from maida.integrations import crewai"
```

If the corresponding extra is absent, that command fails immediately with an `ImportError` naming the missing integration and an install command. Install only the extra you use:

```bash
pip install "maida-ai[langchain]"  # or [openai] / [crewai]
```

### No active Maida run

Adapters intentionally do not create runs by themselves. If framework activity occurs outside `@trace` or `traced_run(...)`, it is ignored. This keeps library imports side-effect-free and prevents unrelated framework traffic from appearing in a Maida run.

### Framework errors

- LangChain error callbacks produce `LLM_CALL` or `TOOL_CALL` events with `status="error"`.
- OpenAI Agents spans with an SDK error produce the corresponding error-status event.
- CrewAI incomplete before/after hook pairs are flushed as error-status events when the Maida run exits.

The original framework exception remains the application's error; the adapter does not replace it with a framework-specific Maida event type.

### Redaction and truncation

Adapters call Maida's existing `record_llm_call` and `record_tool_call` functions. Prompts, responses, tool arguments, results, errors, and `meta` therefore pass through the same recursive redaction and byte limits as direct SDK calls before anything is written to `spans.jsonl`.

For example, an adapter payload containing `{"api_key": "secret"}` stores the value as `__REDACTED__` with the default configuration. Oversized values end with `__TRUNCATED__`. See [Configuration](reference/config.md#redaction) for the exact keys, precedence, and limits.

---

## Planned

Planned framework adapters (not yet implemented):

1. **Agno** - optional adapter for Agno-based agents.
2. Others as needed (e.g. AutoGen, custom loops).

For guidance on adding new integrations (optional deps, mapping callbacks to `record_*`, tests), see the [Maida contributing guide](https://github.com/maida-ai/maida/blob/main/CONTRIBUTING.md#adding-integrations--adapters).
