
import time

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import gestures

START_GESTURE_NAME = "OPEN_PALM"
JUMP_GESTURE_NAME = "OPEN_PALM"
THUMBS_UP_GESTURE_NAME = "THUMBS_UP"
FIST_GESTURE_NAME = "FIST"


class GestureController:
    def __init__(self, model_path="hand_landmarker.task", camera_index=0, debug=False):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            raise RuntimeError("Could not open webcam (camera_index=%d)" % camera_index)

        self.debug = debug
        self.current_gesture = "NONE"
        self.previous_gesture = "NONE"
        self.start_edge_triggered = False
        self.jump_edge_triggered = False
        self.thumbs_up_edge_triggered = False
        self.fist_edge_triggered = False
        self.last_frame = None

    def poll(self):
        """Read one camera frame and update the last gesture state."""
        success, frame = self.capture.read()
        if not success:
            return

        frame = cv2.flip(frame, 1)
        self.last_frame = frame
        height, width, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        timestamp_ms = int(time.time() * 1000)
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)

        gesture_name = "NONE"
        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            landmark_list = [[index, int(point.x * width), int(point.y * height)] for index, point in enumerate(hand)]
            gesture_name = gestures.classify(landmark_list, hand_label="Right")

        self.previous_gesture = self.current_gesture
        self.current_gesture = gesture_name
        self.start_edge_triggered = (gesture_name == START_GESTURE_NAME and self.previous_gesture != START_GESTURE_NAME)
        self.jump_edge_triggered = (gesture_name == JUMP_GESTURE_NAME and self.previous_gesture != JUMP_GESTURE_NAME)
        self.thumbs_up_edge_triggered = (gesture_name == THUMBS_UP_GESTURE_NAME and self.previous_gesture != THUMBS_UP_GESTURE_NAME)
        self.fist_edge_triggered = (gesture_name == FIST_GESTURE_NAME and self.previous_gesture != FIST_GESTURE_NAME)

        if self.debug:
            print(f"[gesture] {gesture_name}")

    def is_start_gesture(self):
        return self.current_gesture == START_GESTURE_NAME

    def consume_start_signal(self):
        """Return True once for a fresh start gesture, then clear the flag."""
        edge = self.start_edge_triggered
        self.start_edge_triggered = False
        return edge

    def consume_jump_signal(self):
        """Return True once for a fresh jump gesture, then clear the flag."""
        edge = self.jump_edge_triggered
        self.jump_edge_triggered = False
        return edge

    def consume_thumbs_up_signal(self):
        """Return True once for a fresh thumbs-up gesture, then clear the flag."""
        edge = self.thumbs_up_edge_triggered
        self.thumbs_up_edge_triggered = False
        return edge

    def consume_fist_signal(self):
        """Return True once for a fresh fist gesture, then clear the flag."""
        edge = self.fist_edge_triggered
        self.fist_edge_triggered = False
        return edge

    def release(self):
        self.capture.release()
        self.landmarker.close()
