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

from .fortnite_api import FortniteApiError, fetch_progress
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret")

PLATFORMS = [
    ("pc", "Epic / PC"),
    ("psn", "PlayStation"),
    ("xbl", "Xbox"),
]


# Database path (file created in the repo root)
DB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "fortnite_data.db")
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """
    )
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS user_sprites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        sprite_id TEXT NOT NULL,
        collected INTEGER NOT NULL DEFAULT 0,
        mastered INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL,
        UNIQUE(user_id, sprite_id)
    )
    """
    )
    conn.commit()
    conn.close()


init_db()


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
        user_name=session.get("user_name"),
    )


@app.route("/fortnite/logout", methods=["GET"])
def fortnite_logout():
    session.pop("epic_username", None)
    session.pop("platform", None)
    return redirect(url_for("fortnite_index"))


@app.route("/fortnite/account", methods=["GET"])
def fortnite_account():
    return render_template("fortnite_account.html", user=session.get("user_name"))


@app.route("/fortnite/api/user/register", methods=["POST"])
def user_register():
    data = request.form or request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), datetime.utcnow().isoformat()),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Username already exists."}), 409
    conn.close()
    session["user_id"] = user_id
    session["user_name"] = username
    return jsonify({"ok": True, "username": username})


@app.route("/fortnite/api/user/login", methods=["POST"])
def user_login():
    data = request.form or request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "Invalid username or password."}), 401
    session["user_id"] = row["id"]
    session["user_name"] = username
    return jsonify({"ok": True, "username": username})


@app.route("/fortnite/api/user/logout", methods=["GET"])
def user_logout_api():
    session.pop("user_id", None)
    session.pop("user_name", None)
    return jsonify({"ok": True})


@app.route("/fortnite/api/progress", methods=["GET"])
def fortnite_api_progress():
    if "epic_username" not in session:
        return jsonify({"error": "Not logged in."}), 401

    try:
        progress = fetch_progress(session["epic_username"], session["platform"])
        return jsonify(progress)
    except FortniteApiError as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/fortnite/api/sprites", methods=["GET"])
def api_sprites():
    sprites_path = os.path.join(os.path.dirname(__file__), "sprites.json")
    if not os.path.exists(sprites_path):
        return jsonify({"error": "Sprites not configured."}), 500
    with open(sprites_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return jsonify(data)


@app.route("/fortnite/api/user/list", methods=["GET", "POST"])
def user_list():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated."}), 401
    user_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT sprite_id, collected, mastered FROM user_sprites WHERE user_id = ?",
            (user_id,),
        )
        rows = cur.fetchall()
        result = {
            r["sprite_id"]: {
                "collected": bool(r["collected"]),
                "mastered": bool(r["mastered"]),
            }
            for r in rows
        }
        conn.close()
        return jsonify(result)

    # POST: replace/merge list
    payload = request.get_json() or {}
    # expected payload: {sprite_id: {collected: bool, mastered: bool}, ...}
    for sprite_id, state in payload.items():
        collected = 1 if state.get("collected") else 0
        mastered = 1 if state.get("mastered") else 0
        now = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO user_sprites (user_id, sprite_id, collected, mastered, updated_at) VALUES (?, ?, ?, ?, ?)"
            " ON CONFLICT(user_id, sprite_id) DO UPDATE SET collected=excluded.collected, mastered=excluded.mastered, updated_at=excluded.updated_at",
            (user_id, sprite_id, collected, mastered, now),
        )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
