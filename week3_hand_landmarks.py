"""
Week 3: MediaPipe Hand Landmark Detection & Visualization
"""

import cv2
import time
import math
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def classify_gesture(hand):
    thumb_up = hand[4].x < hand[3].x
    index_up = hand[8].y < hand[6].y
    middle_up = hand[12].y < hand[10].y
    ring_up = hand[16].y < hand[14].y
    pinky_up = hand[20].y < hand[18].y

    fingers = [thumb_up, index_up, middle_up, ring_up, pinky_up]
    count = sum(fingers)

    # Distance-based gestures checked first (more specific)
    pinch_dist = distance(hand[4], hand[8])
    hand_scale = distance(hand[0], hand[9])
    normalized_pinch = pinch_dist / hand_scale if hand_scale != 0 else 1

    if count == 0:
        return "FIST"
    
    if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
        return "THUMBS_UP"

    if index_up and not middle_up and not ring_up and not pinky_up:
        return "POINTING"
    
    if index_up and pinky_up and not middle_up and not ring_up and not thumb_up:
        return "ROCK_ON"

    if middle_up and not index_up and not ring_up and not pinky_up:
        return "MIDDLE_POINTING"

    if index_up and middle_up and not ring_up and not pinky_up:
        return "PEACE"

    if normalized_pinch < 0.35 and middle_up and ring_up and pinky_up:
        return "OK_SIGN"

    if count >= 4:
        return "OPEN_PALM"

    return "UNKNOWN"


base_options = python.BaseOptions(
    model_asset_path="hand_landmarker.task"
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

landmarker = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    timestamp_ms = int(time.time() * 1000)
    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            for start_idx, end_idx in HAND_CONNECTIONS:
                p1 = hand[start_idx]
                p2 = hand[end_idx]
                x1, y1 = int(p1.x * w), int(p1.y * h)
                x2, y2 = int(p2.x * w), int(p2.y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            for lm in hand:
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            gesture = classify_gesture(hand)
            print(gesture)

            cv2.putText(frame, f"Gesture: {gesture}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            index_tip = hand[8]
            ix, iy = int(index_tip.x * w), int(index_tip.y * h)
            cv2.circle(frame, (ix, iy), 12, (0, 0, 255), -1)
            cv2.putText(frame, f"({ix}, {iy})", (ix + 15, iy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Gesture Control", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cap.release()
landmarker.close()
cv2.destroyAllWindows()