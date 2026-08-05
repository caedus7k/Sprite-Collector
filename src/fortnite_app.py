import os
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
)

from fortnite_api import FortniteApiError, fetch_progress

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret")

PLATFORMS = [
    ("pc", "Epic / PC"),
    ("psn", "PlayStation"),
    ("xbl", "Xbox"),
]


@app.route("/fortnite", methods=["GET"])
def fortnite_index():
    return render_template(
        "fortnite_index.html",
        platforms=PLATFORMS,
        epic_username=session.get("epic_username", ""),
        selected_platform=session.get("platform", "pc"),
    )


@app.route("/fortnite/login", methods=["POST"])
def fortnite_login():
    epic_username = request.form.get("epic_username", "").strip()
    platform = request.form.get("platform", "pc").strip().lower()

    if not epic_username:
        return render_template(
            "fortnite_index.html",
            platforms=PLATFORMS,
            error="Enter your Epic display name before continuing.",
            epic_username=epic_username,
            selected_platform=platform,
        )

    if platform not in {"pc", "psn", "xbl"}:
        platform = "pc"

    session["epic_username"] = epic_username
    session["platform"] = platform
    return redirect(url_for("fortnite_dashboard"))


@app.route("/fortnite/dashboard", methods=["GET"])
def fortnite_dashboard():
    if "epic_username" not in session:
        return redirect(url_for("fortnite_index"))

    return render_template(
        "fortnite_dashboard.html",
        epic_username=session["epic_username"],
        platform=session["platform"],
    )


@app.route("/fortnite/logout", methods=["GET"])
def fortnite_logout():
    session.pop("epic_username", None)
    session.pop("platform", None)
    return redirect(url_for("fortnite_index"))


@app.route("/fortnite/api/progress", methods=["GET"])
def fortnite_api_progress():
    if "epic_username" not in session:
        return jsonify({"error": "Not logged in."}), 401

    try:
        progress = fetch_progress(session["epic_username"], session["platform"])
        return jsonify(progress)
    except FortniteApiError as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
