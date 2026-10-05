# Contributing to the Maida website

## Versioning

The default documentation at `/docs/` is deployed from a pinned Maida engine release; the pin in `tests/contracts/current-main.json` determines that version. The selector also offers engine `main` at `/docs/main/`, clearly labelled unreleased and rebuilt weekly. A website Git tag identifies a site snapshot. For numbered site releases, use the pinned engine's `MAJOR.MINOR` compatibility line and an independent `PATCH` number, with immutable full `vMAJOR.MINOR.PATCH` tags. Publish a new site version only after the pinned engine docs have been built and checked; a matching tag alone does not establish compatibility. See the [Maida versioning policy](https://github.com/maida-ai/maida/blob/main/CONTRIBUTING.md#versioning-and-compatibility).
