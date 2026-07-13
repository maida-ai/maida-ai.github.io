"""Deterministic LangChain/LangGraph adapter example (no network calls)."""

from langchain_core.language_models.fake import FakeListLLM
from langchain_core.tools import tool

from maida import trace
from maida.integrations import LangChainCallbackHandler


@tool
def lookup(query: str) -> str:
    """Return a fixed local result."""
    return f"result for: {query}"


@trace(name="LangChain minimal example")
def run_agent() -> str:
    handler = LangChainCallbackHandler()
    config = {"callbacks": [handler]}

    result = lookup.invoke({"query": "Maida"}, config=config)
    FakeListLLM(responses=["Maida blocks regressions before merge."]).invoke(
        "Summarize the result.", config=config
    )
    return result


if __name__ == "__main__":
    print(run_agent())
    print("Run complete. View with: maida view")
