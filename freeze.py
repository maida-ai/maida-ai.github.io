from flask_frozen import Freezer
from app import app, ALTERNATIVES, BLOG_POSTS

app.config["FREEZER_DESTINATION"] = "dist"
app.config["FREEZER_RELATIVE_URLS"] = False


freezer = Freezer(app)


@freezer.register_generator
def alternative():
    for slug in ALTERNATIVES:
        yield {"slug": slug}


@freezer.register_generator
def blog_post():
    for slug in BLOG_POSTS:
        yield {"slug": slug}


if __name__ == "__main__":
    freezer.freeze()
