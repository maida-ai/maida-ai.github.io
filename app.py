from flask import Flask, render_template, request, url_for

app = Flask(__name__)

@app.context_processor
def inject_globals():
    from datetime import datetime
    return {"request": request, "now": datetime.utcnow(), "url_for": url_for}

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
