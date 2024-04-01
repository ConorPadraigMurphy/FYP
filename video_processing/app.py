from ultralytics import YOLO
import os
from datetime import datetime
from confluent_kafka import Producer
import uuid
from flask_cors import CORS
from flask import Flask, jsonify, request, abort
from werkzeug.utils import secure_filename
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app)
# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))
inputs_dir = os.path.join(current_dir, "inputs")


@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return abort(400, "No file part found in request.")

    file = request.files["file"]
    if file.filename == "":
        return abort(400, "No selected file")

    # Generate a unique video ID
    video_id = str(uuid.uuid4())
    filename = secure_filename(f"{video_id}.mp4")  # Assuming the file is in mp4 format
    filepath = os.path.join(inputs_dir, filename)
    file.save(filepath)

    # Message with video_id and location data
    message = json.dumps(
        {
            "video_id": video_id,
            "address": request.form["address"],
            "latitude": request.form["latitude"],
            "longitude": request.form["longitude"],
            "dateTime": request.form["dateTime"],
        }
    )

    # Produce the video ID to Kafka
    try:
        producer.produce("incoming-videos", message)
        producer.flush()
    except Exception as e:
        return jsonify({"error": str(e)})

    return jsonify({"message": "Video uploaded successfully, video_id: " + video_id})


# Kafka configuration
kafka_config = {
    "bootstrap.servers": "localhost:9092",
    "max.poll.interval.ms": 600000,
}

# Create a Kafka producer instance
producer = Producer(kafka_config)

if __name__ == "__main__":
    app.run(debug=True)
