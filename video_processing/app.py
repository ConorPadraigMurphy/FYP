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
from dotenv import load_dotenv

# Load environment variables from .env file
DOTENV_PATH = "./.env"
load_dotenv(dotenv_path=DOTENV_PATH)


app = Flask(__name__)
CORS(app)
# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))
inputs_dir = os.path.join(current_dir, "inputs")

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flask App</title>
    </head>
    <body>
        <h1>Welcome to My Flask App!</h1>
        <p>This is the index page.</p>
    </body>
    </html>
    """

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
        producer.produce("incoming-videos", key=str(uuid.uuid4()), value=message, callback=acked)
        producer.flush()
    except Exception as e:
        print(f"Publish to Kafka failed: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Video uploaded successfully, video_id: " + video_id})

def acked(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# Kafka configuration
kafka_config = {
    "bootstrap.servers": os.getenv("KAFKA_BROKER_URL", "localhost:9092"),
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": os.getenv("KAFKA_API_KEY"),
    "sasl.password": os.getenv("KAFKA_API_SECRET"), 
}


# Create a Kafka producer instance
producer = Producer(kafka_config)

if __name__ == "__main__":
    app.run(debug=True)
