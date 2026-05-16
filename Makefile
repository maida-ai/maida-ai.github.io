.PHONY: dev css docs build clean

TAILWIND_BIN ?= ./bin/tailwindcss

dev: docs
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --watch &
	uv run python -m flask --app app run --debug

css:
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --minify

docs:
	uv run python -m mkdocs build

build: css docs
	rm -rf dist
	uv run python freeze.py
	cp -rT site/ dist/docs/
	cp CNAME dist/CNAME

clean:
	rm -rf dist site static/styles.css __pycache__
