import os
import sys
import json
import uuid
import sqlite3
import tempfile
import threading
from pathlib import Path

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_PATH = os.path.join(ROOT, "history.db")

def _get_conn():
    """Open a SQLite connection with thread-safe settings."""
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def _init_db():
    """Create the history table if it doesn't exist yet."""
    con = _get_conn()
    con.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id         TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL DEFAULT 'anonymous',
            file       TEXT,
            query      TEXT,
            score      REAL,
            passed     INTEGER,
            result     TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()

_init_db()

_jobs: dict[str, dict] = {}

PIPELINE_STEPS = [
    "Loading dataset",
    "Building analysis plan",
    "Running EDA",
    "Generating visualizations",
    "Extracting insights",
    "Reviewing quality",
    "Reflecting & refining",
    "Writing final report",
]


def _run_pipeline(job_id: str, tmp_path: str, query: str, filename: str):
    """Run the full LangGraph pipeline in a background thread."""
    try:
        from backend.graphs.analyst_graph import complete as analyst_pipeline

        for i, step in enumerate(PIPELINE_STEPS):
            _jobs[job_id]["step"] = i
            _jobs[job_id]["step_label"] = step

        _jobs[job_id]["step"] = 0
        _jobs[job_id]["step_label"] = PIPELINE_STEPS[0]

        initial_state = {
            "file_path": tmp_path,
            "user_query": query,
            "dataset_info": {},
            "analysis_plan": {},
            "eda_results": {},
            "visualizations": [],
            "insights": [],
            "report": "",
            "review_score": None,
            "feedback": None,
            "review": None,
            "review_passed": None,
        }

        result = analyst_pipeline.invoke(initial_state)

 
        for viz in result.get("visualizations", []):
            img_path = viz.get("image_url", "")
            if img_path:
                if img_path.startswith("http://") or img_path.startswith("https://"):
                    viz["image_url"] = img_path
                    viz["image_abs"] = img_path
                else:
                    abs_path = os.path.join(ROOT, img_path) if not os.path.isabs(img_path) else img_path
                    if os.path.exists(abs_path):
                        viz["image_url"] = f"/api/images/{os.path.basename(abs_path)}"
                        viz["image_abs"] = abs_path
                    else:
                        viz["image_url"] = f"/api/images/{os.path.basename(img_path)}"
                        viz["image_abs"] = abs_path

        report = result.get("report", "")
        if report:
            import re
            report = re.sub(r'\]\((?!https?://)(?:reports/|outputs/|datasets/)?([^)]+\.png)\)', r'](/api/images/\1)', report)
            result["report"] = report


        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["step"] = len(PIPELINE_STEPS)
        _jobs[job_id]["result"] = result

        user_id = _jobs[job_id].get("user_id", "anonymous")
        con = _get_conn()
        con.execute(
            "INSERT OR REPLACE INTO history (id, user_id, file, query, score, passed, result) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                job_id,
                user_id,
                filename,
                query,
                result.get("review_score") or 0,
                int(bool(result.get("review_passed", False))),
                json.dumps(result),
            )
        )
        con.commit()
        con.close()

    except Exception as e:
        _jobs[job_id]["status"] = "error"
        _jobs[job_id]["error"] = str(e)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Start analysis job. Returns job_id immediately."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    query = request.form.get("query", "").strip()

    if not query:
        return jsonify({"error": "No query provided"}), 400

    filename = file.filename or "upload.csv"
    suffix = ".xlsx" if filename.endswith(".xlsx") else ".csv"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    job_id = str(uuid.uuid4())
    user_id = request.form.get("user_id", "anonymous")
    _jobs[job_id] = {
        "status": "running",
        "step": 0,
        "step_label": PIPELINE_STEPS[0],
        "user_id": user_id,
        "result": None,
        "error": None,
    }

    t = threading.Thread(target=_run_pipeline, args=(job_id, tmp_path, query, filename), daemon=True)
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/api/jobs/<job_id>", methods=["GET"])
def job_status(job_id):
    """Poll job status / result."""
    job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    payload = {
        "status": job["status"],
        "step": job["step"],
        "step_label": job.get("step_label", ""),
        "total_steps": len(PIPELINE_STEPS),
    }
    if job["status"] == "done":
        payload["result"] = job["result"]
    elif job["status"] == "error":
        payload["error"] = job["error"]

    return jsonify(payload)


@app.route("/api/history", methods=["GET"])
def history():
    """Return history for this user (no heavy result payload)."""
    user_id = request.args.get("user_id", "anonymous")
    con = _get_conn()
    rows = con.execute(
        "SELECT id, file, query, score, passed FROM history "
        "WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    con.close()
    return jsonify([
        {
            "id": r["id"],
            "file": r["file"],
            "query": r["query"],
            "score": r["score"],
            "passed": bool(r["passed"]),
        }
        for r in rows
    ])


@app.route("/api/history/<job_id>", methods=["GET"])
def history_detail(job_id):
    """Return full result for a specific history entry."""
    con = _get_conn()
    row = con.execute("SELECT result FROM history WHERE id = ?", (job_id,)).fetchone()
    con.close()
    if row:
        return jsonify({"result": json.loads(row["result"])})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/images/<filename>", methods=["GET"])
def serve_image(filename):
    search_dirs = [
        os.path.join(ROOT, "reports"),
        tempfile.gettempdir(),
        os.path.join(ROOT, "datasets"),
        os.path.join(ROOT, "outputs"),
    ]
    for job in _jobs.values():
        result = job.get("result") or {}
        for viz in result.get("visualizations", []):
            abs_path = viz.get("image_abs", "")
            if abs_path and os.path.basename(abs_path) == filename and os.path.exists(abs_path):
                return send_file(abs_path, mimetype="image/png")

    for d in search_dirs:
        path = os.path.join(d, filename)
        if os.path.exists(path):
            return send_file(path, mimetype="image/png")

    return jsonify({"error": "Image not found"}), 404


if __name__ == "__main__":
    print("DataMind AI Flask API starting on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
