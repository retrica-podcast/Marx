#!/usr/bin/env python3
"""
Retrica Marx Quiz - Backend server
Start met: python server.py
Leerlingen surfen naar: http://<jouw-ip>:5000
Moderator:             http://<jouw-ip>:5000  → klik "Moderator"
"""

import socket
import threading
from flask import Flask, request, jsonify, send_from_directory
import os, json, time

app = Flask(__name__, static_folder=".")
app.config["JSON_SORT_KEYS"] = False

# In-memory scoreboard: { "naam_lowercase": { name, score, progress, status, ts } }
scores = {}
lock = threading.Lock()


# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/api/score", methods=["POST"])
def push_score():
    data = request.get_json(force=True)
    name   = str(data.get("name", "")).strip()
    if not name:
        return jsonify({"ok": False, "error": "name required"}), 400
    key = name.lower()
    with lock:
        scores[key] = {
            "name":     name,
            "score":    int(data.get("score", 0)),
            "progress": int(data.get("progress", 0)),
            "status":   str(data.get("status", "playing")),
            "ts":       time.time(),
        }
    return jsonify({"ok": True})


@app.route("/api/scores", methods=["GET"])
def get_scores():
    with lock:
        snapshot = list(scores.values())
    snapshot.sort(key=lambda p: (-p["score"], p["name"]))
    return jsonify(snapshot)


@app.route("/api/clear", methods=["POST"])
def clear_scores():
    with lock:
        scores.clear()
    return jsonify({"ok": True})


# ── Serve the quiz HTML ───────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "quiz.html")


# ── Start ─────────────────────────────────────────────────────────────────────

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    ip = get_local_ip()
    print("\n" + "═" * 52)
    print("  🎙  RETRICA MARX QUIZ — server gestart")
    print("═" * 52)
    print(f"\n  Leerlingen surfen naar:  http://{ip}:5000")
    print(f"  Moderator (ww: RetRica): http://{ip}:5000")
    print(f"  Lokaal testen:           http://127.0.0.1:5000")
    print("\n  Druk Ctrl+C om te stoppen.\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
