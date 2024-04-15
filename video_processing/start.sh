#!/bin/sh

# Start the Flask app using Gunicorn in the background
gunicorn app:app --daemon

# Wait for a few seconds to ensure Flask app starts first
sleep 5

# Start the video_consumer.py script
python3 video_consumer.py

# Keep the script running
wait
