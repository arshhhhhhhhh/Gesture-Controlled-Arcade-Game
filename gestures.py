import math


def distance_between_landmarks(landmark_list, start_index, end_index):
    x1, y1 = landmark_list[start_index][1], landmark_list[start_index][2]
    x2, y2 = landmark_list[end_index][1], landmark_list[end_index][2]
    return math.hypot(x2 - x1, y2 - y1)


def estimate_hand_scale(landmark_list):
    reference_length = distance_between_landmarks(landmark_list, 0, 9)
    return reference_length if reference_length != 0 else 1


def fingers_up(landmark_list):
    finger_states = []

    pinky_base_joint = 17
    thumb_tip_distance = distance_between_landmarks(landmark_list, 4, pinky_base_joint)
    thumb_inner_distance = distance_between_landmarks(landmark_list, 3, pinky_base_joint)
    finger_states.append(1 if thumb_tip_distance > thumb_inner_distance else 0)

    for tip_index in [8, 12, 16, 20]:
        finger_states.append(1 if landmark_list[tip_index][2] < landmark_list[tip_index - 2][2] else 0)

    return finger_states


def classify(landmark_list, hand_label="Right"):
    """Main entry point for gesture recognition."""
    if not landmark_list or len(landmark_list) < 21:
        return "NONE"

    finger_states = fingers_up(landmark_list)
    estimate_hand_scale(landmark_list)

    if finger_states == [0, 0, 0, 0, 0]:
        return "FIST"
    if finger_states == [1, 1, 1, 1, 1]:
        return "OPEN_PALM"
    if finger_states == [0, 1, 0, 0, 0]:
        return "POINTING"
    if finger_states == [0, 1, 1, 0, 0]:
        return "PEACE"
    if finger_states == [1, 0, 0, 0, 0]:
        return "THUMBS_UP"

    return "UNKNOWN"