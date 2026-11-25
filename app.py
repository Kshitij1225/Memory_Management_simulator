from flask import Flask, render_template, request, jsonify
from memory_manager import MemoryManager
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("simulation_history.db")
manager = MemoryManager(1024)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_history(action, details):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO history (action, details) VALUES (?, ?)", (action, details))

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/state")
def state():
    return jsonify(manager.snapshot())

@app.post("/api/configure")
def configure():
    data = request.get_json(force=True)
    try:
        size = int(data.get("total_memory", 1024))
        manager.configure(size, data.get("layout", manager.layout))
        save_history("Configure", f"Total memory set to {size} KB")
        return jsonify(manager.snapshot())
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/allocate")
def allocate():
    data = request.get_json(force=True)
    try:
        name = str(data.get("process_name", "")).strip()
        size = int(data.get("size", 0))
        strategy = str(data.get("strategy", "first")).lower()
        result = manager.allocate(name, size, strategy)
        save_history("Allocate", f"{name}: {size} KB using {strategy}")
        return jsonify({"message": result, **manager.snapshot()})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/deallocate")
def deallocate():
    data = request.get_json(force=True)
    try:
        name = str(data.get("process_name", "")).strip()
        message = manager.deallocate(name)
        save_history("Deallocate", message)
        return jsonify({"message": message, **manager.snapshot()})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/reset")
def reset():
    data = request.get_json(silent=True) or {}
    try:
        size = int(data.get("total_memory", manager.total_memory))
        manager.configure(size, data.get("layout", manager.layout))
        save_history("Reset", f"Simulation reset to {size} KB")
        return jsonify({"message": "Simulation reset.", **manager.snapshot()})
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.get("/api/history")
def history():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT action, details, created_at FROM history ORDER BY id DESC LIMIT 8"
        ).fetchall()
    return jsonify([{"action": r[0], "details": r[1], "created_at": r[2]} for r in rows])

init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
