"""
Week 1: Webcam Feed with FPS Counter and Annotations
"""

import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

prev_time = time.time()
fps_list = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    fps_list.append(fps)
    if len(fps_list) > 30:
        fps_list.pop(0)
    avg_fps = sum(fps_list) / len(fps_list)

    cv2.rectangle(frame, (50, 25), (220, 70), (0, 255, 0), 2)
    cv2.putText(frame, f"Arsh | FPS: {int(avg_fps)}", (55, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, "Press 'q' to quit", (55, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Week 1 - Webcam Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()