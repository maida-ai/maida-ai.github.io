from flask import Flask, render_template, request, url_for

app = Flask(__name__, static_url_path='/static')

@app.context_processor
def inject_globals():
    from datetime import datetime
    return {
        "request": request,
        "now": datetime.utcnow(),
        "url_for": url_for,
        "base_url": "https://maida.ai"
    }

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
