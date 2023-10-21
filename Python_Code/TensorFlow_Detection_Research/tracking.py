import numpy as np
from ultralytics import YOLO
import cv2
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
outputDir = 'Outputs'
os.makedirs(outputDir, exist_ok=True)
# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Load video
cap = cv2.VideoCapture('./Cars.mp4')

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

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        output.write(annotated_frame)

        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            trackIDs = results[0].boxes.id.int().cpu().tolist()
            carIDs.update(trackIDs)

            for track_id in trackIDs:
                if track_id not in timeStamps:
                    timeStamps[track_id] = {"start_frame": cap.get(
                        cv2.CAP_PROP_POS_FRAMES), "start_time": cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0}
                timeStamps[track_id]['end_frame'] = cap.get(
                    cv2.CAP_PROP_POS_FRAMES)
                timeStamps[track_id]['end_time'] = cap.get(
                    cv2.CAP_PROP_POS_MSEC) / 1000.0

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

        # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release video capture and close the OpenCV window
cap.release()
cv2.destroyAllWindows()

# Write all car IDs to a text file
textOutputDir = os.path.join(outputDir, "CarIDs&TimestampsTRACKING.txt")
with open(textOutputDir, 'w') as car_ids_file:
    for car_id in carIDs:
        start_time = timeStamps[car_id]['start_time']
        end_time = timeStamps[car_id]['end_time']
        direction = carDirections.get(car_id, 'NA')
        car_ids_file.write(
            f"Car ID: {car_id}, Entered: {start_time} secs, Exited: {end_time} secs, Direction: {direction}\n")
