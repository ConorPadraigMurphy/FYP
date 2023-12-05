from ultralytics import YOLO
import os
from datetime import datetime
from confluent_kafka import Producer
import uuid

from flask import Flask, jsonify, request, abort
from werkzeug.utils import secure_filename
app = Flask(__name__)


# Endpoint to get object IDs, timestamps, and directions as JSON - http://127.0.0.1:5000/api/bus_info
@app.route('/api/bus_info', methods=['GET'])
def get_bus_info():
    busInfoResponse = []
    for idx, busInfoEntry in enumerate(busInfo, start=0):
        busInfoResponse.append({
            'index':idx,
            'objectID':busInfoEntry['object_id'],
            'classID':busInfoEntry['class_id'],
            'enteredTime':busInfoEntry['entered_time'],
            'exitiedTime':busInfoEntry['exited_time'],
            'direction':busInfoEntry['direction'],
        })
    return jsonify(({
        "video_info": {
            "creationTime": creationTime.strftime("%Y-%m-%d %H:%M:%S"),
            "justTime": justTime
        },
        "bus_info": busInfoResponse
    }))


# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))
inputs_dir = os.path.join(current_dir, 'inputs')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return abort(400, 'No file part found in request.')

    file = request.files['file']
    if file.filename == '':
        return abort(400, 'No selected file')

    # Generate a unique video ID
    video_id = str(uuid.uuid4())
    filename = secure_filename(f"{video_id}.mp4")  # Assuming the file is in mp4 format
    filepath = os.path.join(inputs_dir, filename)
    file.save(filepath)

    # Produce the video ID to Kafka
    try:
        producer.produce('incoming-videos', video_id)
        producer.flush()
    except Exception as e:
        return jsonify({'error': str(e)})

    return jsonify({'message': 'Video uploaded successfully.'})


# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092'  
}

# Create a Kafka producer instance
producer = Producer(kafka_config)

if __name__ == '__main__':
    app.run(debug=True)
