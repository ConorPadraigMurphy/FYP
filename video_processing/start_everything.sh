#!/bin/bash

ls

echo "Starting Flask application..."
export FLASK_APP=app.py
export FLASK_ENV=development
flask run &

echo "Running video_consumer.py script..."
python3 video_consumer.py &


echo "All processes started."