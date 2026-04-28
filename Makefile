.PHONY: dev css build deploy clean

TAILWIND_BIN ?= ./bin/tailwindcss

dev:
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --watch &
	uv run flask --app app run --debug

css:
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --minify

build: css
	rm -rf dist
	uv run python freeze.py
	cp _worker.js dist/_worker.js

deploy: build
	wrangler pages deploy ./dist

clean:
	rm -rf dist static/styles.css __pycache__
