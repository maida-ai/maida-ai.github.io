import os

from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

DOCS_BUILD_DIR = os.path.join(os.path.dirname(__file__), "site")

SITE_URL = "https://maida.ai"

BLOG_POSTS = [
    "why-your-agent-needs-a-regression-gate",
]


@app.context_processor
def inject_site_url():
    return {"SITE_URL": SITE_URL}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/pricing/")
def pricing():
    return render_template("pricing.html")


@app.route("/blog/")
def blog_index():
    return render_template("blog/index.html")


@app.route("/blog/<slug>/")
def blog_post(slug):
    return render_template(f"blog/{slug}.html")


@app.route("/docs/")
@app.route("/docs/<path:path>")
def docs(path=""):
    """Serve MkDocs build output from site/ during local dev."""
    if not os.path.isdir(DOCS_BUILD_DIR):
        abort(404)
    if not path or os.path.isdir(os.path.join(DOCS_BUILD_DIR, path)):
        path = os.path.join(path, "index.html")
    return send_from_directory(DOCS_BUILD_DIR, path)
