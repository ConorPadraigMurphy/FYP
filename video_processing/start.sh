#!/bin/sh

# Start the Flask app
gunicorn app:app &

# Wait for a few seconds to ensure Flask app starts first
sleep 5

# Start the video_consumer.py script
python3 video_consumer.py