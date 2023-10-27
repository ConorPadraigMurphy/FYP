import cv2
import numpy as np
import tensorflow as tf
import os

outputDir = 'Outputs'
os.makedirs(outputDir, exist_ok=True)
# Loads models
model = tf.saved_model.load(
    'Model\efficientdet_d0_coco17_tpu-32\saved_model')

# Image and Video
cap = cv2.VideoCapture('Cars.mp4')

fourcc = cv2.VideoWriter_fourcc(*'XVID')

outputPath = os.path.join(outputDir, "videoOutput.avi")

output = cv2.VideoWriter(outputPath, fourcc,
                         30.0, (int(cap.get(3)), int(cap.get(4))))

carCount = 0
motorCycleCount = 0
busCount = 0

# initializing IDs so that I only count a car/motorcycle once per video rather than counting the same car in every frame
carID = set()


# Initialize variables to keep track of car timestamps
car_detected = False  # Flag to track if a car is currently detected
car_appeared_time = 0.0  # Timestamp when the car first appeared
car_left_time = 0.0  # Timestamp when the car left the frame
car_ids_and_timestamps = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Processing for video
    input_tensor = cv2.resize(frame, (500, 500))
    input_tensor = np.expand_dims(input_tensor, axis=0)

    # Detects vehicles
    detections = model(input_tensor)

    # Process videos for detection
    for i, detection in enumerate(detections['detection_boxes'][0]):
        ymin, xmin, ymax, xmax = detection.numpy()
        xmin, xmax, ymin, ymax = int(xmin * frame.shape[1]), int(xmax * frame.shape[1]), \
            int(ymin * frame.shape[0]), int(ymax * frame.shape[0])

        # Gets the object ID. List of IDs here ->  https://stackoverflow.com/questions/50665110/tensorflow-models-uses-coco-90-class-ids-although-coco-has-only-80-categories
        class_id = int(detections['detection_classes'][0][i].numpy())
        score = detections['detection_scores'][0][i].numpy()

        # id 3 is a car, 6 is for buses
        # score is how confident we want it to be before it labels it as a car/motorcycle etc
        if class_id == 3 and score > 0.5:
            label = f"Car ({score: .2f})"
            carID.add(i)

            if not car_detected:
                car_appeared_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                car_detected = True
                car_id = len(carID)
                car_ids_and_timestamps.append(
                    (car_id, car_appeared_time, None))

        else:
            continue

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        cv2.putText(frame, label, (xmin, ymin - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        carCount = len(carID)

    if car_detected and class_id != 3:
        car_left_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        car_detected = False
        for i, car_info in enumerate(car_ids_and_timestamps):
            if car_info[2] is None:
                car_ids_and_timestamps[i] = (
                    car_info[0], car_info[1], car_left_time)

    output.write(frame)
    cv2.imshow('Detection tool', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
output.release()
cv2.destroyAllWindows()

# Outputs count of vehicle to a file but must allow the video to fully play
textOutputDir = os.path.join(outputDir, "VehicleCount.txt")
outputfile = textOutputDir
with open(outputfile, 'w') as file:
    file.write(f'Number of Cars Detected: {carCount}\n')
    file.write(f'TimeStamps + IDs: \n')
    for car_info in car_ids_and_timestamps:
        file.write(
            f'CarID: {car_info[0]}, First Detected: {car_info[1]}, Last Detected: {car_info[2]}\n')
