import os
from flask import Flask, request, jsonify, abort
from werkzeug.utils import secure_filename

# Create a Flask app
app = Flask(__name__)

# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))

# Define a route to handle uploading a video file
@app.route('/upload', methods=['POST'])
def upload_video():

  # Check if the request contains a file part
  if 'file' not in request.files:
    return abort(400, 'No file part found in request.')

  # Get the file from the request
  file = request.files['file']

  filename = secure_filename(file.filename)

  # Save the file to the current directory
  file.save(os.path.join(current_dir, filename))

  # Return a JSON response with the message "Video uploaded successfully."
  return jsonify({'message': 'Video uploaded successfully.'})
