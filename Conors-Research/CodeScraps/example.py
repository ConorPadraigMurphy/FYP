from ultralytics import YOLO
import cv2
import os
##Example of basic detection/tracking
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# load yolov8 model
model = YOLO('yolov8n.pt')

# load video
cap = cv2.VideoCapture('Cars.mp4')

ret = True
# read frames
while ret:
    ret, frame = cap.read()

    if ret:

        # detect objects
        # track objects
        results = model.track(frame, persist=True)
        print(results)
        # plot results
        # cv2.rectangle
        # cv2.putText
        frame_ = results[0].plot()

        # visualize
        cv2.imshow('frame', frame_)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
