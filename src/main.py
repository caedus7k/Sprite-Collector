import os
import sys

from dotenv import load_dotenv
from flask import Flask, render_template, request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from market_api import fetch_ebay_sales, fetch_tcgplayer_sales

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query", "").strip()
    marketplace = request.form.get("marketplace", "all")

    if not query:
        return render_template(
            "index.html",
            error="Please enter a search term.",
            query=query,
            marketplace=marketplace,
        )

    results = {}
    errors = []

    if marketplace in ("ebay", "all"):
        try:
            results["ebay"] = fetch_ebay_sales(query, limit=12)
        except Exception as exc:
            errors.append(f"eBay error: {exc}")

    if marketplace in ("tcgplayer", "all"):
        try:
            results["tcgplayer"] = fetch_tcgplayer_sales(query, limit=12)
        except Exception as exc:
            errors.append(f"TCGplayer error: {exc}")

    if not results:
        return render_template(
            "index.html",
            error="Could not fetch data. " + " ".join(errors),
            query=query,
            marketplace=marketplace,
        )

    return render_template("results.html", query=query, results=results, errors=errors)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
