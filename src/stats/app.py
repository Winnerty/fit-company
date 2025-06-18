from flask import Flask, jsonify
from pymongo import MongoClient
from schemas import WorkoutStatSchema

app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017/")
db = client["fit_company"]
stats_collection = db["workout_stats"]

stat_schema = WorkoutStatSchema()

@app.route("/stats", methods=["GET"])
def get_stats():
    stats = list(stats_collection.find({}, {"_id": 0}))
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)