"""Deterministic OpenAI Agents SDK adapter example (no network calls)."""

from agents.tracing import (
    function_span,
    generation_span,
    handoff_span,
    set_trace_processors,
    trace as agents_trace,
)

from maida import trace
from maida.integrations import openai_agents


@trace(name="OpenAI Agents minimal example")
def run_agent() -> None:
    # Keep SDK tracing local: replace its processors with Maida's processor.
    set_trace_processors([openai_agents.PROCESSOR])

    with agents_trace("Maida OpenAI Agents example"):
        with generation_span(
            input=[{"role": "user", "content": "Summarize Maida."}],
            output=[
                {
                    "role": "assistant",
                    "content": "Maida blocks behavioral regressions before merge.",
                }
            ],
            model="fake-model",
            usage={"prompt_tokens": 3, "completion_tokens": 6, "total_tokens": 9},
        ):
            pass

        with function_span(
            name="lookup_docs",
            input={"query": "Maida integrations"},
            output={"hits": 2},
        ):
            pass

        with handoff_span(from_agent="router", to_agent="docs"):
            pass


if __name__ == "__main__":
    run_agent()
    print("Run complete. View with: maida view")
