from ultralytics import YOLO
import cv2
import os
import time
import datetime


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
output = cv2.VideoWriter(outputPath, fourcc, 30.0,
                         (int(cap.get(3)), int(cap.get(4))))

timeStamps = {}
trackIDs = []
carIDs = set()
directionCategory = {}
carDirections = {}
previousPosition = {}
frameCount = 0
startTime = time.time()


def getVideoDateTime(videoPath):
    try:
        filmTime = cap.get(cv2.CAP_PROP_POS_MSEC)
        if filmTime > 0:
            filmDateTime = datetime.datetime.fromtimestamp(
                filmTime / 1000)
            return filmDateTime.date(), filmDateTime.time()
        else:
            return None, None
    except:
        return None, None


vidFilmDate, vidFilmTime = getVideoDateTime(vidInputDir)


ret = True

while ret:
    ret, frame = cap.read()

    if ret:
        frameCount += 1
        # Run YOLOv8 tracking on the frame, persisting tracks between frames, classes=2(car)
        results = model.track(frame, persist=True, classes=2)
        boxes = results[0].boxes.xyxy.cpu()

        # Plots the boxes on the video
        annotated_frame = results[0].plot()

        output.write(annotated_frame)

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


                if track_id not in previousPosition:
                    previousPosition[track_id] = results[0].boxes.xyxy[trackIDs.index(track_id)][0].item()

                currentX = results[0].boxes.xyxy[trackIDs.index(track_id)][0].item()
    
                if currentX is not None and previousPosition[track_id] is not None:
                    objectDirection = float(currentX) - float(previousPosition[track_id])

                    if track_id not in carDirections:
                        carDirections[track_id] = []

                    carDirections[track_id] = objectDirection  # Append the direction to the list
                    previousPosition[track_id] = currentX

            # Update end timestamps as the car is still being tracked
            timeStamps[track_id]['end_frame'] = cap.get(cv2.CAP_PROP_POS_FRAMES)
            timeStamps[track_id]['end_time'] = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0



    for track_id, direction_list in carDirections.items():
        if not isinstance(direction_list, (list, tuple)):
            continue

        numeric_direction = [d for d in direction_list if isinstance(d, (int, float))]

        if numeric_direction:
            avgDirection = sum(numeric_direction) / len(numeric_direction)
            directionCategory = 'Right' if avgDirection > 0 else 'Left'
            carDirections[track_id] = [directionCategory]
        else:
            carDirections[track_id] = ['Unknown']


    # Works out how many frames are executed by the process per second
    endTime = time.time()
    totalTime = endTime - startTime
    FPS = frameCount/totalTime

    annotated_frameFPS = annotated_frame.copy()
    text = f'FPS: {FPS: .2f}'
    cv2.putText(annotated_frameFPS, text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
    output.write(annotated_frameFPS)
    print(f'FPS: {FPS: .2f}')

    # Displays the annotated_frameFPS which adds the FPS which the tracking process is taking
    cv2.imshow("YOLOv8 Tracking", annotated_frameFPS)

    frameCount = 0
    startTime = endTime

    # End process in progress by pressing Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release video capture and close the OpenCV window
cap.release()
cv2.destroyAllWindows()

# Write all car IDs and Timestamps of when the car appears and when the car exits the video to a text file
textOutputDir = os.path.join(outputDir, "CarIDs&TimestampsTRACKING.txt")
with open(textOutputDir, 'w') as car_ids_file:
    car_ids_file.write(
        f'Date Filmed: {vidFilmDate}  Time Filmed: {vidFilmTime}\n')
    for car_id in carIDs:
        start_time = timeStamps[car_id]['start_time']
        end_time = timeStamps[car_id]['end_time']
        direction = carDirections.get(car_id, 'NA')
        if direction > 0:
            direction = 'Right'
        else:
            direction = 'Left'
        car_ids_file.write(
            f"Car ID: {car_id}, Entered: {start_time} secs, Exited: {end_time} secs, Direction: {direction}\n")
        
        print(f"Car ID: {car_id}, Raw Direction: {direction}")


# Endpoint to get car IDs, timestamps, and directions as JSON - http://127.0.0.1:5000/api/car_info
@app.route('/api/car_info', methods=['GET'])
def get_car_info():
    car_info = []
    for car_id in carIDs:
        start_time = timeStamps[car_id]['start_time']
        end_time = timeStamps[car_id]['end_time']
        direction = carDirections.get(car_id, 'NA')
        if direction > 0:
            direction = 'Right'
        else:
            direction = 'Left'
        car_info.append({
            "car_id": car_id,
            "entered_time": start_time,
            "exited_time": end_time,
            "direction": direction
        })
    return jsonify(car_info)

if __name__ == '__main__':
    app.run(debug=True)
