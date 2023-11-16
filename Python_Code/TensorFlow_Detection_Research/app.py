from ultralytics import YOLO
import cv2
import os
import time
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
outputDir = 'Outputs'
inputDir = 'Inputs'
vidInputDir = os.path.join(inputDir, "./bus.mp4")
os.makedirs(outputDir, exist_ok=True)

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Load video
statInfo = os.stat(vidInputDir)
cap = cv2.VideoCapture(vidInputDir)

downscaleWidth = 640
downscaleHeight = 420

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

cap.set(cv2.CAP_PROP_FRAME_WIDTH, downscaleWidth)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, downscaleHeight)

# Getting time and date of video creation
creationTime = datetime.fromtimestamp(statInfo.st_mtime)
justTime = creationTime.strftime('%H:%M:%S')

fourcc = cv2.VideoWriter_fourcc(*'XVID')
outputPath = os.path.join(outputDir, "TrackingvideoOutput.avi")
output = cv2.VideoWriter(outputPath, fourcc, 30.0,(downscaleWidth, downscaleHeight))

# Defining variables
timeStamps, trackIDs, objectIDs = {}, [], set()
objectDirections, previousPosition = {}, {}
objectClassPairs, uniqueObjectIDs = [], set()
startTime = time.time()
frameCount = 0

ret = True

while ret:
    ret, frame = cap.read()

    if ret:

        frameCount += 1
        # Downscales video that is being processed to 640x420
        frame = cv2.resize(frame, (downscaleWidth, downscaleHeight), interpolation=cv2.INTER_LINEAR)
        # Run YOLOv8 tracking on the frame, persisting tracks between frames, bus = 5, car = 2
        results = model.track(frame, persist=True, classes=[2,5])
        boxes = results[0].boxes.xyxy.cpu()
        # Plots the boxes on the video
        annotated_frame = results[0].plot()
        output.write(annotated_frame)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            trackIDs = results[0].boxes.id.int().cpu().tolist()
            objectIDs.update(trackIDs)

            for i, track_id in enumerate(trackIDs):
                class_id = results[0].boxes.cls[i].int().item()
                
                if track_id not in uniqueObjectIDs:
                    objectClassPairs.append({'ObjectId: ':track_id, 'ClassId: ':class_id})
                    uniqueObjectIDs.add(track_id)

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

                    if track_id not in objectDirections:
                        objectDirections[track_id] = []

                    objectDirections[track_id] = objectDirection
                    previousPosition[track_id] = currentX
                

            # Update end timestamps as the car is still being tracked
            timeStamps[track_id]['end_frame'] = cap.get(cv2.CAP_PROP_POS_FRAMES)
            timeStamps[track_id]['end_time'] = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0



    for track_id, direction_list in objectDirections.items():
        if not isinstance(direction_list, (list, tuple)):
            continue

        numeric_direction = [d for d in direction_list if isinstance(d, (int, float))]

        if numeric_direction:
            avgDirection = sum(numeric_direction) / len(numeric_direction)
            directionCategory = 'Right' if avgDirection > 0 else 'Left'
            objectDirections[track_id] = [directionCategory]
        else:
            objectDirections[track_id] = ['Unknown']


    # Works out how many frames are executed by the process per second
    endTime = time.time()
    totalTime = endTime - startTime
    FPS = frameCount/totalTime

    annotated_frameFPS = annotated_frame.copy()
    text = f'FPS: {FPS: .2f}'
    cv2.putText(annotated_frameFPS, text, (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
    output.write(annotated_frameFPS)
    print(f'FPS: {FPS: .2f}')

    # Displays the annotated_frameFPS which adds the FPS which the tracking process is taking
    cv2.imshow("YOLOv8 Tracking", annotated_frameFPS)

    frameCount = 0
    startTime = endTime

    # End process in progress by pressing Q
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

totalTime = total_frames/30.0
justTimeInSeconds = sum(x * int(t) for x, t in zip([3600, 60, 1], justTime.split(':')))

# Subtract totalTime from justTimeInSeconds
newTimeInSeconds = justTimeInSeconds - totalTime

# Convert the result back to HH:MM:SS format
hours, remainder = divmod(newTimeInSeconds, 3600)
minutes, seconds = divmod(remainder, 60)
newJustTime = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

# Release video capture and close the OpenCV window
cap.release()
cv2.destroyAllWindows()

# Write all car IDs and Timestamps of when the car appears and when the car exits the video to a text file
textOutputDir = os.path.join(outputDir, "ObjectIDs&TimestampsTRACKING.txt")
with open(textOutputDir, 'w') as object_ids_file:
    object_ids_file.write(f'Filmed: {creationTime}, Time: {newJustTime}\n')
    for objectID in objectIDs:
        start_time = timeStamps[objectID]['start_time']
        end_time = timeStamps[objectID]['end_time']
        class_id = None
        
        for objectInfo in objectClassPairs:
            if objectInfo['ObjectId: '] == objectID:
                class_id = objectInfo['ClassId: ']
                if class_id == 2:
                    class_id = 'Car'
                if class_id == 5:
                    class_id = 'Bus'

                break
        
        direction = objectDirections.get(objectID, 'NA')
        if direction > 0:
            direction = 'Right'
        else:
            direction = 'Left'
        object_ids_file.write(
            f"Object ID: {objectID}, Class ID: {class_id}, Entered: {start_time :.2f} secs, Exited: {end_time :.2f} secs, Direction: {direction}\n")
        


# Endpoint to get car IDs, timestamps, and directions as JSON - http://127.0.0.1:5000/api/object_info
@app.route('/api/object_info', methods=['GET'])
def get_object_info():
    object_info = []
    for object_id in objectIDs:
        for objectInfo in objectClassPairs:
            if objectInfo['ObjectId: '] == object_id:
                class_id = objectInfo['ClassId: ']
                if class_id == 2:
                    class_id = 'Car'
                elif class_id == 5:
                    class_id = 'Bus'
                break
        start_time = timeStamps[object_id]['start_time']
        end_time = timeStamps[object_id]['end_time']
        direction = objectDirections.get(object_id, 'NA')
        if direction > 0:
            direction = 'Right'
        else:
            direction = 'Left'
        object_info.append({
            "object_id": object_id,
            'class_id': class_id,
            "entered_time": start_time,
            "exited_time": end_time,
            "direction": direction
        })
    return jsonify(object_info)

if __name__ == '__main__':
    app.run(debug=True)
