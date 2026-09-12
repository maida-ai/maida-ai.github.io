.PHONY: dev css docs docs-sync docs-check build clean

TAILWIND_BIN ?= ./bin/tailwindcss

dev: docs
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --watch &
	uv run python -m flask --app app run --debug

css:
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --minify

# Documentation content lives in maida/docs and is pulled in at the pinned
# engine release. Set MAIDA_DOCS_PATH=../maida to preview unreleased pages.
docs-sync:
	uv run python bin/sync_docs.py

docs-check:
	uv run python bin/sync_docs.py --check

docs: docs-sync
	uv run sphinx-build -M clean docs site
	uv run sphinx-build -W --keep-going -E -b dirhtml -d .sphinx-doctrees docs site

build: css docs
	rm -rf dist
	uv run python freeze.py
	cp -rT site/ dist/docs/
	cp CNAME dist/CNAME

clean:
	rm -rf dist site .sphinx-doctrees static/styles.css __pycache__
