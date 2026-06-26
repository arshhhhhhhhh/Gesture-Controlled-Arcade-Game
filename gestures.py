import math


def _distance(lm_list, p1, p2):
    x1, y1 = lm_list[p1][1], lm_list[p1][2]
    x2, y2 = lm_list[p2][1], lm_list[p2][2]
    return math.hypot(x2 - x1, y2 - y1)


def _hand_scale(lm_list):
    ref = _distance(lm_list, 0, 9)
    return ref if ref != 0 else 1


def fingers_up(lm_list, hand_label="Right"):
    """Returns [thumb, index, middle, ring, pinky], 1 = up."""
    fingers = []

    if hand_label == "Right":
        fingers.append(1 if lm_list[4][1] > lm_list[3][1] else 0)
    else:
        fingers.append(1 if lm_list[4][1] < lm_list[3][1] else 0)

    for tip in [8, 12, 16, 20]:
        fingers.append(1 if lm_list[tip][2] < lm_list[tip - 2][2] else 0)

    return fingers


def classify(lm_list, hand_label="Right"):
    """Main entry point. Returns a gesture name string."""
    if not lm_list or len(lm_list) < 21:
        return "NONE"

    fingers = fingers_up(lm_list, hand_label)
    scale = _hand_scale(lm_list)

    pinch = _distance(lm_list, 4, 8) / scale

    if fingers == [0, 0, 0, 0, 0]:
        return "FIST"
    if fingers == [1, 1, 1, 1, 1]:
        return "OPEN_PALM"
    if fingers == [0, 1, 0, 0, 0]:
        return "POINTING"
    if fingers == [0, 1, 1, 0, 0]:
        return "PEACE"
    if fingers == [1, 0, 0, 0, 0]:
        return "THUMBS_UP"
    
    return "UNKNOWN"