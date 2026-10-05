# Maida website infrastructure

This repository publishes [maida.ai](https://maida.ai) and the [Maida documentation site](https://maida.ai/docs/). It is public infrastructure, outside the core product and supported extensions.

**Maida checks agent changes before merge.** Start with the [Maida engine and CLI](https://github.com/maida-ai/maida), the [canonical runnable coding-agent experience](https://github.com/maida-ai/maida-tutorials), and the [GitHub Action](https://github.com/maida-ai/maida-assert).

## Maintain the site

This repository owns the presentation layer: Flask templates frozen to static HTML and the Sphinx documentation layout. Reference content comes from the engine's `docs/`; synced pages are generated artifacts. Change reference documentation in the engine repository.

The documentation selector offers the [pinned release](https://maida.ai/docs/) and [engine main (unreleased)](https://maida.ai/docs/main/). The release follows `engine_ref` in `tests/contracts/current-main.json`; development docs follow engine `main`. `make docs` builds both from isolated sources into `site/`, with separate assets and search indexes, and publishes their shared selector manifest at `/docs/versions.json`.

The Pages workflow rebuilds both versions on website `main` pushes, manual dispatch, and every Monday at 07:23 UTC. Updating the release pin changes the release docs on the next build; the weekly build refreshes development docs without a website commit. Both strict builds must pass before deployment. GitHub may delay scheduled runs and disables schedules in public repositories after 60 days without repository activity; use manual dispatch to rebuild between scheduled runs and re-enable an inactive schedule when needed.

For a local development preview, run `MAIDA_DOCS_PATH=../maida make docs`, then `make dev` with the same environment variable and visit `/docs/main/`. This affects only development docs. Never deploy a local-preview build.

See [contributor guidance](CONTRIBUTING.md), [build commands and content ownership](AGENTS.md), and the [engine contract](https://github.com/maida-ai/maida/tree/main/contracts) before changing the site or its release pin.
