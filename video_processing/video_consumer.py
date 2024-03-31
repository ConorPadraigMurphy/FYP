from confluent_kafka import Consumer, KafkaException, KafkaError
import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from pymongo import MongoClient
import json
from dotenv import load_dotenv

# Load environment variables from .env file
DOTENV_PATH = "./.env"
load_dotenv(dotenv_path=DOTENV_PATH)

# Mongo Connection string
mongo_uri = os.getenv("MONGO_API_KEY")
client = MongoClient(mongo_uri)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Mongo DB and collection
db = client["FYP"]
collection = db["FYP"]

# Kafka Consumer Configuration
consumer_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "video-processing-group",
    "auto.offset.reset": "latest",
    "max.poll.interval.ms": 1000000,
}

# Create a Kafka Consumer instance
consumer = Consumer(consumer_conf)

# Load YOLOv8 model
model = YOLO("yolov8n.pt")
OUTPUT_DIR = "Outputs"
INPUT_DIR = "Inputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_video(video_id, location_data):

    print(f"Location Data: {location_data}")
    vid_input_dir = os.path.join(INPUT_DIR, f"{video_id}.mp4")
    if not os.path.exists(vid_input_dir):
        print(f"Video file {vid_input_dir} not found.")
        return

    stat_info = os.stat(vid_input_dir)
    cap = cv2.VideoCapture(vid_input_dir)
    if not cap.isOpened():
        print(f"Failed to open video file {vid_input_dir}.")
        return

    downscale_width = 640
    downscale_height = 420
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, downscale_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, downscale_height)

    # Getting time and date of video creation from meta data
    creation_time = datetime.fromtimestamp(stat_info.st_mtime)
    just_time = creation_time.strftime("%H:%M:%S")

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    output_path = os.path.join(OUTPUT_DIR, f"TrackingvideoOutput_{video_id}.avi")
    output = cv2.VideoWriter(
        output_path, fourcc, 30.0, (downscale_width, downscale_height)
    )

    time_stamps, track_ids, object_ids = {}, [], set()
    object_directions, previous_position = {}, {}
    object_class_pairs, unique_objectids = [], set()
    start_time = time.time()
    frame_count = 0

    ret, frame = cap.read()
    while ret:

        frame_count += 1
        # Downscales video that is being processed to 640x420
        frame = cv2.resize(
            frame, (downscale_width, downscale_height), interpolation=cv2.INTER_LINEAR
        )
        # Run YOLOv8 tracking on the frame, persisting tracks between frames, bus = 5, car = 2
        results = model.track(frame, persist=True, classes=[2, 5])
        # Plots the boxes on the video
        annotated_frame = results[0].plot()
        output.write(annotated_frame)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().cpu().tolist()
            object_ids.update(track_ids)

            for i, track_id in enumerate(track_ids):
                class_id = results[0].boxes.cls[i].int().item()

                # Adds objects ids and class ID to uniqueObjectIDs as long as it is not already in it
                if track_id not in unique_objectids:
                    object_class_pairs.append(
                        {"ObjectId: ": track_id, "ClassId: ": class_id}
                    )
                    unique_objectids.add(track_id)

                # Gets the time that the object enters the videos frame and the time that it leaves the frame
                if track_id not in time_stamps:
                    time_stamps[track_id] = {
                        "start_frame": cap.get(cv2.CAP_PROP_POS_FRAMES),
                        "start_time": cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0,
                    }
                time_stamps[track_id]["end_frame"] = cap.get(cv2.CAP_PROP_POS_FRAMES)
                time_stamps[track_id]["end_time"] = (
                    cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                )

                # Adds object ID to previous positions to keep track of object
                if track_id not in previous_position:
                    previous_position[track_id] = (
                        results[0].boxes.xyxy[track_ids.index(track_id)][0].item()
                    )

                current_x = results[0].boxes.xyxy[track_ids.index(track_id)][0].item()

                # Tracks direction of object
                if current_x is not None and previous_position[track_id] is not None:
                    object_direction = float(current_x) - float(
                        previous_position[track_id]
                    )

                    if track_id not in object_directions:
                        object_directions[track_id] = []

                    object_directions[track_id] = object_direction
                    previous_position[track_id] = current_x

            # Update end timestamps as the object is still being tracked
            for track_id in unique_objectids:
                time_stamps[track_id]["end_frame"] = cap.get(cv2.CAP_PROP_POS_FRAMES)
                time_stamps[track_id]["end_time"] = (
                    cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                )

            # Works out how many frames are executed by the process per second
            end_time = time.time()
            total_time = end_time - start_time
            FPS = frame_count / total_time

            annotated_frame_fps = annotated_frame.copy()
            text = f"FPS: {FPS: .2f}"
            cv2.putText(
                annotated_frame_fps,
                text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 255),
                2,
            )
            output.write(annotated_frame_fps)

            # Displays the annotated_frameFPS which adds the FPS which the tracking process is taking
            cv2.imshow("YOLOv8 Tracking", annotated_frame_fps)

            frame_count = 0
            start_time = end_time

            # End process in progress by pressing Q
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        total_time = total_frames / 30.0
        just_time_in_seconds = sum(
            x * int(t) for x, t in zip([3600, 60, 1], just_time.split(":"))
        )

        # Subtract totalTime from justTimeInSeconds
        new_time_in_seconds = just_time_in_seconds - total_time

        # Convert the result back to HH:MM:SS format
        hours, remainder = divmod(new_time_in_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        new_just_time = "{:02}:{:02}:{:02}".format(
            int(hours), int(minutes), int(seconds)
        )

        creation_time = datetime.fromtimestamp(stat_info.st_mtime)
        day_of_week = creation_time.strftime("%A")

        ret, frame = cap.read()

    info_list = []
    # Write all object IDs and Timestamps of when the object appears and when the object exits the video to a text file
    for object_info in object_class_pairs:
        objectID = object_info["ObjectId: "]
        class_id = object_info["ClassId: "]
        if class_id == 2:  # Car
            class_name = "Car"
        elif class_id == 5:  # Bus
            class_name = "Bus"
        else:
            continue

        start_time = time_stamps[objectID]["start_time"]
        end_time = time_stamps[objectID]["end_time"]
        direction = object_directions.get(objectID, "NA")
        if direction > 0:
            direction = "Right"
        else:
            direction = "Left"

        #  Work on entered_time being seconds not hours
        time_str = new_just_time[:2]
        time_float = float(time_str)
        time_seconds = time_float * 3600
        combined_time = time_seconds + start_time

        hours = int(combined_time / 3600)
        minutes = int((combined_time - hours * 3600) / 60)
        combinedtime_float = float(f"{hours}.{minutes}")

        info_list.append(
            {
                "object_id": objectID,
                "class_id": class_name,
                "entered_time": start_time,
                "exited_time": end_time,
                "direction": direction,
                "timestamp": combinedtime_float,
                "dayOfWeek": day_of_week,
            }
        )

    # Adding location to info_list
    for info in info_list:
        info["address"] = location_data.get("address", "")
        info["latitude"] = location_data.get("latitude", "")
        info["longitude"] = location_data.get("longitude", "")

    # Insert data into MongoDB
    try:
        if info_list:  # Check if busInfo is not empty
            collection.insert_many(info_list)
            print(f"Inserted car & bus data for video {video_id}")

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
                    print(
                        "%% %s [%d] reached end at offset %d\n"
                        % (msg.topic(), msg.partition(), msg.offset())
                    )
                else:
                    raise KafkaException(msg.error())
            else:
                # Successfully received a message
                # Deserialize the message value from JSON format
                message_data = json.loads(msg.value().decode("utf-8"))

                # Extract the video ID and location data from the message
                video_id = message_data["video_id"]
                location_data = {
                    "address": message_data.get("address", ""),
                    "latitude": message_data.get("latitude", ""),
                    "longitude": message_data.get("longitude", ""),
                }

                # Pass the video_id and location_data to your video processing function
                process_video(video_id, location_data)
    finally:
        # Close the consumer to commit final offsets and free up resources
        consumer.close()


if __name__ == "__main__":
    # List of topics to subscribe to
    topics = ["incoming-videos"]
    # Start consuming messages
    consume_loop(consumer, topics)
