"""Deterministic LangChain/LangGraph adapter example (no network calls)."""

import argparse

from langchain_core.language_models.fake import FakeListLLM
from langchain_core.tools import tool

from maida import trace
from maida.integrations import LangChainCallbackHandler


@tool
def lookup(query: str) -> str:
    """Return a fixed local result."""
    return f"result for: {query}"


@trace(name="LangChain minimal example")
def run_agent(*, regression: bool = False) -> str:
    handler = LangChainCallbackHandler()
    config = {"callbacks": [handler]}

    result = lookup.invoke({"query": "Maida"}, config=config)
    if regression:
        lookup.invoke({"query": "Maida regression check"}, config=config)

    FakeListLLM(responses=["Maida blocks regressions before merge."]).invoke(
        "Summarize the result.", config=config
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--regression",
        action="store_true",
        help="emit one extra lookup tool call",
    )
    args = parser.parse_args()

    print(run_agent(regression=args.regression))
    print("Run complete. View with: maida view")


if __name__ == "__main__":
    main()
