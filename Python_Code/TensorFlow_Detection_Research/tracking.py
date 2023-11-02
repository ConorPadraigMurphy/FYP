import numpy as np
from ultralytics import YOLO
import cv2
import os

from flask import Flask, jsonify
app = Flask(__name__)


os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
outputDir = 'Outputs'
inputDir = 'Inputs'
vidInputDir = os.path.join(inputDir, "./Cars.mp4")
os.makedirs(outputDir, exist_ok=True)
# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Load video
cap = cv2.VideoCapture(vidInputDir)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
outputPath = os.path.join(outputDir, "TrackingvideoOutput.avi")
output = cv2.VideoWriter(outputPath, fourcc,
                         30.0, (int(cap.get(3)), int(cap.get(4))))

frameRate = int(cap.get(cv2.CAP_PROP_FPS))

ret = True

timeStamps = {}
trackIDs = []
carIDs = set()
previousPositions = {}
directionCategory = {}
carDirections = {}

while ret:
    ret, frame = cap.read()

    if ret:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames, classes=2(car)
        results = model.track(frame, persist=True, classes=2)
        boxes = results[0].boxes.xyxy.cpu()

        # Plots the boxes on the video
        annotated_frame = results[0].plot()

        output.write(annotated_frame)

        # Displays the annotated_frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            trackIDs = results[0].boxes.id.int().cpu().tolist()
            carIDs.update(trackIDs)

            # Gets the timestamps of the teacked object IDs
            for track_id in trackIDs:
                if track_id not in timeStamps:
                    timeStamps[track_id] = {"start_frame": cap.get(
                        cv2.CAP_PROP_POS_FRAMES), "start_time": cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0}
                timeStamps[track_id]['end_frame'] = cap.get(
                    cv2.CAP_PROP_POS_FRAMES)
                timeStamps[track_id]['end_time'] = cap.get(
                    cv2.CAP_PROP_POS_MSEC) / 1000.0

            # Checks if the car is going left or right across the frame
            if track_id in previousPositions:
                currentPosition = (results[0].boxes.xyxy[0][0].item(
                ), results[0].boxes.xyxy[0][1].item())
                previousPosition = previousPositions[track_id]
                objectDirection = (
                    currentPosition[0] - previousPosition[0], currentPosition[1], previousPosition[1])

                if objectDirection[0] > 0:
                    directionCategory = 'Right'
                else:
                    directionCategory = 'Left'

            carDirections[track_id] = directionCategory
            previousPositions[track_id] = (
                results[0].boxes.xyxy[0][0].item(), results[0].boxes.xyxy[0][1].item())

        # End process in progress by pressing Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release video capture and close the OpenCV window
cap.release()
cv2.destroyAllWindows()

# Write all car IDs and Timestamps of when the car appears and when the car exits the video to a text file
textOutputDir = os.path.join(outputDir, "CarIDs&TimestampsTRACKING.txt")
with open(textOutputDir, 'w') as car_ids_file:
    for car_id in carIDs:
        start_time = timeStamps[car_id]['start_time']
        end_time = timeStamps[car_id]['end_time']
        direction = carDirections.get(car_id, 'NA')
        car_ids_file.write(
            f"Car ID: {car_id}, Entered: {start_time} secs, Exited: {end_time} secs, Direction: {direction}\n")
        


# Endpoint to get car IDs, timestamps, and directions as JSON - http://127.0.0.1:5000/api/car_info
@app.route('/api/car_info', methods=['GET'])
def get_car_info():
    car_info = []
    for car_id in carIDs:
        start_time = timeStamps[car_id]['start_time']
        end_time = timeStamps[car_id]['end_time']
        direction = carDirections.get(car_id, 'NA')
        car_info.append({
            "car_id": car_id,
            "entered_time": start_time,
            "exited_time": end_time,
            "direction": direction
        })
    return jsonify(car_info)

if __name__ == '__main__':
    app.run(debug=True)
