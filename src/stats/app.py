from flask import Flask, jsonify, request
from .database import init_db
from .stats_service import get_stats_by_user
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

@app.route("/stats", methods=["POST"])
def get_stats():
    email = request.json.get("email")
    if not email:
        return jsonify({"error": "Missing email"}), 400

    stats = get_stats_by_user(email)
    if stats is None:
        return jsonify({"error": "Failed to fetch stats"}), 500

    return jsonify([s.model_dump() for s in stats]), 200

def run_app():
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_app()