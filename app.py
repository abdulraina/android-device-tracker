import os, sqlite3, secrets
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
DB_PATH = os.environ.get("DB_PATH", "visitors.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

with db() as con:
    con.execute("""CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        device TEXT, brand TEXT, model TEXT, os_version TEXT, browser TEXT,
        screen TEXT, language TEXT, timezone TEXT, battery_level REAL,
        charging INTEGER, battery_supported INTEGER, ip TEXT
    )""")

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/visit")
def record_visit():
    data = request.get_json(silent=True) or {}
    if data.get("consent") is not True:
        return jsonify(error="Consent is required"), 400
    # IP is retained only for basic abuse/security context. No precise GPS is requested.
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    ip = ip.split(",")[0].strip()[:64]
    with db() as con:
        con.execute("""INSERT INTO visitors
        (created_at, device, brand, model, os_version, browser, screen, language,
         timezone, battery_level, charging, battery_supported, ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (datetime.now(timezone.utc).isoformat(), data.get("device","")[:80],
         data.get("brand","")[:80], data.get("model","")[:100],
         data.get("os_version","")[:80], data.get("browser","")[:100],
         data.get("screen","")[:40], data.get("language","")[:40],
         data.get("timezone","")[:80], data.get("battery_level"),
         int(bool(data.get("charging"))), int(bool(data.get("battery_supported"))), ip))
    return jsonify(ok=True)

@app.get("/admin/login")
def login():
    return render_template("login.html", error=None)

@app.post("/admin/login")
def login_post():
    if not ADMIN_PASSWORD:
        return render_template("login.html", error="Set ADMIN_PASSWORD on the server first."), 503
    if secrets.compare_digest(request.form.get("password",""), ADMIN_PASSWORD):
        session["admin"] = True
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Incorrect password."), 401

@app.post("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/admin")
@admin_required
def dashboard():
    with db() as con:
        rows = con.execute("SELECT * FROM visitors ORDER BY id DESC LIMIT 500").fetchall()
    return render_template("dashboard.html", visitors=rows)

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    if not ADMIN_PASSWORD:
        print("WARNING: Set ADMIN_PASSWORD before deployment.")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
