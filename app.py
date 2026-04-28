from flask import Flask, render_template

app = Flask(__name__)

SITE_URL = "https://maida.ai"

ALTERNATIVES = [
    "arize-ai",
    "braintrust",
    "confident-ai",
    "galileo",
    "honeyhive",
    "langsmith",
    "respan",
]

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


@app.route("/alternatives/")
def alternatives_index():
    return render_template("alternatives/index.html")


@app.route("/alternatives/<slug>/")
def alternative(slug):
    return render_template(f"alternatives/{slug}.html")
