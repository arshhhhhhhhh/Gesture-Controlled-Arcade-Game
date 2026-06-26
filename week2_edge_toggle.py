"""
Week 2 — Image Processing + Edge View Toggle
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
edge_mode = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    fps_list.append(fps)
    if len(fps_list) > 30:
        fps_list.pop(0)
    avg_fps = sum(fps_list) / len(fps_list)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('e'):
        edge_mode = True
    elif key == ord('n'):
        edge_mode = False

    if edge_mode:
        display = cv2.Canny(frame, 50, 150)
        display = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
    else:
        display = frame

    cv2.rectangle(display, (50, 25), (220, 70), (0, 255, 0), 2)
    cv2.putText(display, f"Arsh | FPS: {int(avg_fps)}", (55, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(display, "Press 'e' edges, 'n' normal, 'q' quit", (55, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow("Week 2 - Image Processing", display)

cap.release()
cv2.destroyAllWindows()