from confluent_kafka import Consumer, KafkaException, KafkaError
import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from pymongo import MongoClient
import json

# Mongo Connection string
client = MongoClient({process.env.MONGO_API_KEY})
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Mongo DB and collection
db = client["FYP"]
collection = db["FYP"]

# Kafka Consumer Configuration
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'video-processing-group',
    'auto.offset.reset': 'latest'
}

# Create a Kafka Consumer instance
consumer = Consumer(consumer_conf)

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

outputDir = 'Outputs'
inputDir = 'Inputs'
os.makedirs(outputDir, exist_ok=True)

def process_video(video_id, location_data):
    print(f"Location Data: {location_data}")
    busInfo, carInfo = [], []
    vidInputDir = os.path.join(inputDir, f"{video_id}.mp4")
    if not os.path.exists(vidInputDir):
        print(f"Video file {vidInputDir} not found.")
        return

    statInfo = os.stat(vidInputDir)
    cap = cv2.VideoCapture(vidInputDir)
    if not cap.isOpened():
        print(f"Failed to open video file {vidInputDir}.")
        return

    downscaleWidth = 640
    downscaleHeight = 420
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, downscaleWidth)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, downscaleHeight)

    # Getting time and date of video creation
    creationTime = datetime.fromtimestamp(statInfo.st_mtime)
    justTime = creationTime.strftime('%H:%M:%S')

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    outputPath = os.path.join(outputDir, f"TrackingvideoOutput_{video_id}.avi")
    output = cv2.VideoWriter(outputPath, fourcc, 30.0, (downscaleWidth, downscaleHeight))

    timeStamps, trackIDs, objectIDs = {}, [], set()
    objectDirections, previousPosition = {}, {}
    objectClassPairs, uniqueObjectIDs = [], set()
    busInfo, carInfo = [], []
    startTime = time.time()
    frameCount = 0

    ret, frame = cap.read()
    while ret:
        ret, frame = cap.read()
        if ret:
            frameCount += 1
            # Downscales video that is being processed to 640x420
            frame = cv2.resize(frame, (downscaleWidth, downscaleHeight), interpolation=cv2.INTER_LINEAR)
            # Run YOLOv8 tracking on the frame, persisting tracks between frames, bus = 5, car = 2
            results = model.track(frame, persist=True, classes=[2, 5])
            # Plots the boxes on the video
            boxes = results[0].boxes.xyxy.cpu()
            annotated_frame = results[0].plot()
            output.write(annotated_frame)

            if results[0].boxes is not None and results[0].boxes.id is not None:
                trackIDs = results[0].boxes.id.int().cpu().tolist()
                objectIDs.update(trackIDs)

                for i, track_id in enumerate(trackIDs):
                    class_id = results[0].boxes.cls[i].int().item()

                    # Adds objects ids and class ID to uniqueObjectIDs as long as it is not already in it
                    if track_id not in uniqueObjectIDs:
                        objectClassPairs.append({'ObjectId: ': track_id, 'ClassId: ': class_id})
                        uniqueObjectIDs.add(track_id)

                    # Gets the time that the object enters the videos frame and the time that it leaves the frame
                    if track_id not in timeStamps:
                        timeStamps[track_id] = {"start_frame": cap.get(cv2.CAP_PROP_POS_FRAMES), "start_time": cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0}
                    timeStamps[track_id]['end_frame'] = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    timeStamps[track_id]['end_time'] = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

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
                for track_id in uniqueObjectIDs:
                    timeStamps[track_id]['end_frame'] = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    timeStamps[track_id]['end_time'] = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

            # Works out how many frames are executed by the process per second
            endTime = time.time()
            totalTime = endTime - startTime
            FPS = frameCount / totalTime

            annotated_frameFPS = annotated_frame.copy()
            text = f'FPS: {FPS: .2f}'
            cv2.putText(annotated_frameFPS, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            output.write(annotated_frameFPS)

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

        # Process object direction information
        for track_id, direction_list in objectDirections.items():
            if not isinstance(direction_list, (list, tuple)):
                continue

            numeric_direction = [d for d in direction_list if isinstance(d, (int, float))]

            if numeric_direction:
                avgDirection = sum(numeric_direction) / len(numeric_direction)
                directionCategory = 'Right' if avgDirection > 0 else 'Left'
                start_time = timeStamps[objectID]['start_time']

                # Add object direction information to busInfo and carInfo
                if objectIDs[track_id] == 2:
                    busInfo.append({
                        'TrackId': track_id,
                        'ClassId': 2,
                        'AvgDirection': avgDirection,
                        'DirectionCategory': directionCategory,
                        'timestamp': chartTimeStamp
                    })
                else:
                    carInfo.append({
                        'TrackId': track_id,
                        'ClassId': 5,
                        'AvgDirection': avgDirection,
                        'DirectionCategory': directionCategory,
                        'timestamp': chartTimeStamp
                    })
                    
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

        #Work on entered_time being seconds not hours
        timeStr = newJustTime[:2]
        timeFloat = float(timeStr)
        timeSeconds = timeFloat * 3600
        combinedTime = timeSeconds + start_time

        hours = int(combinedTime/3600)
        minutes = int((combinedTime - hours * 3600)/60)
        combinedTimeFloat = float(f"{hours}.{minutes}")

        info_list.append({
            'object_id': objectID,
            'class_id': class_name,
            'entered_time': start_time,
            'exited_time': end_time,
            'direction': direction,
            'timestamp':combinedTimeFloat
        })


        # Commented out seeing as there no need for constant updates to text files now that db is connected
        # busOutputDirectory = os.path.join(outputDir, "BusObjectsInfo.txt")
        # with open(busOutputDirectory, 'w') as busIDsFile :
        #     busIDsFile.write(f'Filmed: {creationTime}, Time: {newJustTime}\n')
        #     for idx, busInfoEntry in enumerate(busInfo, start=0):
        #         busIDsFile.write(f'Index: {idx}, '
        #             f"Object ID: {busInfoEntry['object_id']}, Class ID: {busInfoEntry['class_id']}, "
        #             f"Entered: {busInfoEntry['entered_time']:.2f} secs, Exited: {busInfoEntry['exited_time']:.2f} secs, "
        #             f"Direction: {busInfoEntry['direction']}\n")

                
        # carOutputDirectory = os.path.join(outputDir, "CarObjectsInfo.txt")
        # with open(carOutputDirectory, 'w') as carIDsFile :
        #     carIDsFile.write(f'Filmed: {creationTime}, Time: {newJustTime}\n')
        #     for idx, carInfoEntry in enumerate(carInfo, start=0):
        #         carIDsFile.write(f'Index: {idx}, '
        #             f'Object ID: {carInfoEntry["object_id"]}, Class ID: {carInfoEntry["class_id"]}, '
        #             f'Entered: {carInfoEntry["entered_time"]:.2f} secs, Exited: {carInfoEntry["exited_time"]:.2f} secs,'
        #             f'Direction: {carInfoEntry["direction"]}\n')
    
    # Adding location to infos
    for info in busInfo + carInfo:
        info['address'] = location_data.get('address', '')
        info['latitude'] = location_data.get('latitude', '')
        info['longitude'] = location_data.get('longitude', '')

    # Insert data into MongoDB
    try:
        if busInfo:  # Check if busInfo is not empty
            collection.insert_many(busInfo)
            print(f"Inserted bus data for video {video_id}")

        if carInfo:  # Check if carInfo is not empty
            collection.insert_many(carInfo)
            print(f"Inserted car data for video {video_id}")

    except Exception as e:
        print(f"An error occurred while inserting data into MongoDB: {e}")


    # Clean-up after processing
    output.release()
    cap.release()
    cv2.destroyAllWindows()

def consume_loop(consumer, topics):
    try:
        # Subscribe the Kafka consumer to a list of topics
        consumer.subscribe(topics)

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue  # Continue the loop if no message is received

            if msg.error():
                # Correctly handle partition EOF using KafkaError
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('%% %s [%d] reached end at offset %d\n' %
                          (msg.topic(), msg.partition(), msg.offset()))
                else:
                    raise KafkaException(msg.error())
            else:
                # Successfully received a message
                # Deserialize the message value from JSON format
                message_data = json.loads(msg.value().decode('utf-8'))
                
                # Extract the video ID and location data from the message
                video_id = message_data['video_id']
                location_data = {
                    'address': message_data.get('address', ''),
                    'latitude': message_data.get('latitude', ''),
                    'longitude': message_data.get('longitude', '')
                }
                
                # Pass the video_id and location_data to your video processing function
                process_video(video_id, location_data)
    finally:
        # Close the consumer to commit final offsets and free up resources
        consumer.close()

if __name__ == '__main__':
    # List of topics to subscribe to
    topics = ['incoming-videos']
    # Start consuming messages
    consume_loop(consumer, topics)