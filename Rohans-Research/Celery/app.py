from flask import Flask, jsonify
from celery import Celery
import cv2

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

celery = make_celery(app)

@celery.task(name='process_video')
def process_video(video_path):
    # Read the video file
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480), isColor=False)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Write the grayscale frame to the output file
        out.write(gray)

    cap.release()
    out.release()

@app.route('/upload', methods=['POST'])
def upload_video():
    file_path = "/"  
    process_video.delay(file_path)
    return jsonify({'message': 'Video uploaded and processing started.'})

if __name__ == '__main__':
    app.run(debug=True)
