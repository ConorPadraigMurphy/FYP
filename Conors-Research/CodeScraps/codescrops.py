##Codescraps i was using that I got rid of that might have come in use 

# # Draw the tracking lines
            # points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            # cv2.polylines(annotated_frame, [points], isClosed=False, color=(
            #     230, 230, 230), thickness=10)

# Get the boxes and track IDs
# boxes = results[0].boxes.xyxy.cpu()
# track_cls = results[0].boxes.cls.int().cpu().tolist()
# track_ids = results[0].boxes.ids.int().cpu().tolist()


# Plot the tracks
# for box, cls in zip(boxes, track_cls):
#x1, y1, x2, y2 = box

# if cls != 2:
# continue

#print(x1, y1, x2, y2)

# cv2.rectangle(frame, (int(x1.item()), int(y1.item())),
# (int(x2.item()), int(y2.item())), (0, 255, 0), 2)
