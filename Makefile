.PHONY: dev css build clean

TAILWIND_BIN ?= ./bin/tailwindcss

dev:
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --watch &
	uv run flask --app app run --debug

css:
	$(TAILWIND_BIN) -c tailwind.config.js -i tailwind/input.css -o static/styles.css --minify

build: css
	rm -rf dist
	uv run python freeze.py
	cp CNAME dist/CNAME

clean:
	rm -rf dist static/styles.css __pycache__
