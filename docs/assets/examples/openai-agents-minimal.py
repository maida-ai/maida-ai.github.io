"""Deterministic OpenAI Agents SDK adapter example (no network calls)."""

import argparse

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
def run_agent(*, regression: bool = False) -> None:
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

        if regression:
            with function_span(
                name="lookup_docs",
                input={"query": "Maida regression check"},
                output={"hits": 2},
            ):
                pass

        with handoff_span(from_agent="router", to_agent="docs"):
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regression",
        action="store_true",
        help="emit one extra lookup_docs tool call",
    )
    args = parser.parse_args()

    run_agent(regression=args.regression)
    print("Run complete. View with: maida view")


if __name__ == "__main__":
    main()
