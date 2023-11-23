from ultralytics import YOLO
import cv2
import os
import time
from datetime import datetime


from flask import Flask, jsonify, request, abort
from werkzeug.utils import secure_filename
app = Flask(__name__)

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
outputDir = 'Outputs'
inputDir = 'Inputs'
vidInputDir = os.path.join(inputDir, "./ATUBuses.mp4")
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
busInfo, carInfo = [], []
busIDsFile, carIDsFile = [], [] 
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
        results = model.track(frame, persist=True, classes=[2, 5])
        boxes = results[0].boxes.xyxy.cpu()
        # Plots the boxes on the video
        annotated_frame = results[0].plot()
        output.write(annotated_frame)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            trackIDs = results[0].boxes.id.int().cpu().tolist()
            objectIDs.update(trackIDs)

            for i, track_id in enumerate(trackIDs):
                class_id = results[0].boxes.cls[i].int().item()
                
                # Adds objects ids and class ID to uniqueObjectIDs as long as it is not already in it
                if track_id not in uniqueObjectIDs:
                    objectClassPairs.append({'ObjectId: ':track_id, 'ClassId: ':class_id})
                    uniqueObjectIDs.add(track_id)

                # Gets the time that the object enters the videos frame and the time that it leaves the frame
                if track_id not in timeStamps:
                    timeStamps[track_id] = {"start_frame": cap.get(
                        cv2.CAP_PROP_POS_FRAMES), "start_time": cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0}
                timeStamps[track_id]['end_frame'] = cap.get(
                    cv2.CAP_PROP_POS_FRAMES)
                timeStamps[track_id]['end_time'] = cap.get(
                    cv2.CAP_PROP_POS_MSEC) / 1000.0

                # Adds object ID to previous positions to keep track of object
                if track_id not in previousPosition:
                    previousPosition[track_id] = results[0].boxes.xyxy[trackIDs.index(track_id)][0].item()

                currentX = results[0].boxes.xyxy[trackIDs.index(track_id)][0].item()

                # Tracks direction of object
                if currentX is not None and previousPosition[track_id] is not None:
                    objectDirection = float(currentX) - float(previousPosition[track_id])

                    if track_id not in objectDirections:
                        objectDirections[track_id] = []

                    objectDirections[track_id] = objectDirection
                    previousPosition[track_id] = currentX
                

            # Update end timestamps as the object is still being tracked
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

# Write all object IDs and Timestamps of when the object appears and when the object exits the video to a text file
for objectInfo in objectClassPairs:
    objectID = objectInfo['ObjectId: ']
    class_id = objectInfo['ClassId: ']
    if class_id == 2:  # Car
        class_name = 'Car'
        info_list = carInfo
    elif class_id == 5:  # Bus
        class_name = 'Bus'
        info_list = busInfo
    else:
        continue

    start_time = timeStamps[objectID]['start_time']
    end_time = timeStamps[objectID]['end_time']
    direction = objectDirections.get(objectID, 'NA')
    if direction > 0:
        direction = 'Right'
    else:
        direction = 'Left'

    info_list.append({
        "object_id": objectID,
        'class_id': class_name,
        "entered_time": start_time,
        "exited_time": end_time,
        "direction": direction
    })


    busOutputDirectory = os.path.join(outputDir, "BusObjectsInfo.txt")
    with open(busOutputDirectory, 'w') as busIDsFile :
        busIDsFile.write(f'Filmed: {creationTime}, Time: {newJustTime}\n')
        for idx, busInfoEntry in enumerate(busInfo, start=0):
            busIDsFile.write(
                f"Object ID: {busInfoEntry['object_id']}, Class ID: {busInfoEntry['class_id']}, "
                f"Entered: {busInfoEntry['entered_time']:.2f} secs, Exited: {busInfoEntry['exited_time']:.2f} secs, "
                f"Direction: {busInfoEntry['direction']}\n")
            
    carOutputDirectory = os.path.join(outputDir, "CarObjectsInfo.txt")
    with open(carOutputDirectory, 'w') as carIDsFile :
        carIDsFile.write(f'Filmed: {creationTime}, Time: {newJustTime}\n')
        for idx, carInfoEntry in enumerate(carInfo, start=0):
            carIDsFile.write( f'Index: {idx}, '
                f"Object ID: {carInfoEntry['object_id']}, Class ID: {carInfoEntry['class_id']}, "
                f"Entered: {carInfoEntry['entered_time']:.2f} secs, Exited: {carInfoEntry['exited_time']:.2f} secs, "
                f"Direction: {carInfoEntry['direction']}\n")

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

# Endpoint to get object IDs, timestamps, and directions as JSON - http://127.0.0.1:5000/api/car_info
@app.route('/api/car_info', methods=['GET'])
def get_car_info():
    carInfoResponse = []
    for idx, carInfoEntry in enumerate(carInfo, start=0):
        carInfoResponse.append({
            'index':idx,
            'objectID':carInfoEntry['object_id'],
            'classID':carInfoEntry['class_id'],
            'enteredTime':carInfoEntry['entered_time'],
            'exitiedTime':carInfoEntry['exited_time'],
            'direction':carInfoEntry['direction'],
        })
    return jsonify(({
        "video_info": {
            "creationTime": creationTime.strftime("%Y-%m-%d %H:%M:%S"),
            "justTime": justTime
        },
        "car_info": carInfoResponse
    }))



# Get the current directory
current_dir = os.path.dirname(os.path.realpath(__file__))
inputs_dir = os.path.join(current_dir, 'inputs')

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
  file.save(os.path.join(inputs_dir, filename))

  # Return a JSON response with the message "Video uploaded successfully."
  return jsonify({'message': 'Video uploaded successfully.'})


if __name__ == '__main__':
    app.run(debug=True)
