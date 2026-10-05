# Maida website infrastructure

This repository publishes [maida.ai](https://maida.ai) and the [Maida documentation site](https://maida.ai/docs/). It is public infrastructure, outside the core product and supported extensions.

**Maida checks agent changes before merge.** Start with the [Maida engine and CLI](https://github.com/maida-ai/maida), the [canonical runnable coding-agent experience](https://github.com/maida-ai/maida-tutorials), and the [GitHub Action](https://github.com/maida-ai/maida-assert).

## Maintain the site

This repository owns the presentation layer: Flask templates frozen to static HTML and the Sphinx documentation layout. Reference content comes from the engine's `docs/` at the release pinned in `tests/contracts/current-main.json`; synced pages are generated artifacts. Change reference documentation in the engine repository.

See [contributor guidance](CONTRIBUTING.md), [build commands and content ownership](AGENTS.md), and the [engine contract](https://github.com/maida-ai/maida/tree/main/contracts) before changing the site or its release pin.
