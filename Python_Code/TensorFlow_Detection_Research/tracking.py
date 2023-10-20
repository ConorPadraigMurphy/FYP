from ultralytics import YOLO
import cv2
import os
import time as t

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# load yolov8 model
model = YOLO('./yolov8n.pt')

carLabel = "car"

# load video
video_path = './Cars.mp4'
cap = cv2.VideoCapture(video_path)

carDetected = False
carAppearTime = 0.0
carDisappearTime = 0.0
carIdsandTimestamps = []

ret = True
# read frames
while ret:
    ret, frame = cap.read()

    if ret:

        # detect objects
        # track objects
        results = model.track(frame, persist=True)

        carResults = []

    for car in carResults:
        bbox = car['Bounding Box']
        label = car['class']
        confidence = car['conf']

        x, y, w, h = [int(i) for i in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        labelText = f'{label} ({confidence: .2f})'
        cv2.putText(frame, labelText, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if not carDetected:
            carAppearTime = t.time()
            carDetected = True
            carID = len(carIdsandTimestamps) + 1
            carIdsandTimestamps.append((carID, carAppearTime, None))

    if carDetected and not carResults:
        carDisappearTime = t.time()
        carDetected = False

        for i, carInfo in enumerate(carIdsandTimestamps):
            if carInfo[2] is None:
                carIdsandTimestamps[i] = (
                    carInfo[0], carInfo[1], carDisappearTime)

    # visualize
    cv2.imshow('frame', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

textOutputDirectory = os.path.join(
    os.path.dirname(video_path), 'CarTrackingInfo.txt')
with open(textOutputDirectory, 'w') as file:
    file.write('Car Tracking Information:\n')
    for carInfo in carIdsandTimestamps:
        file.write(
            f'Car ID {carInfo[0]} > Entered Video: {carInfo[1]}, Left Video: {carInfo[2]}\n')
