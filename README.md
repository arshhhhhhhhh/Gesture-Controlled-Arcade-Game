# Gesture-Controlled Arcade Game

A SoC project exploring real-time computer vision as a game input method — starting from raw webcam capture and ending with a fully playable, gesture-controlled Flappy Bird clone built in Pygame.

---

## Project Timeline

| Week | Focus | File |
|---|---|---|
| 1 | Webcam capture basics, FPS measurement, on-frame annotation | `week1_webcam_basics.py` |
| 2 | Image processing — live Canny edge-detection toggle | `week2_edge_toggle.py` |
| 3 | MediaPipe hand landmark detection + first rule-based gesture classifier | `week3_hand_landmarks.py` |
| 4 | Refactored gesture logic into a standalone, reusable module with a dedicated test harness | `gestures.py`, `test_gestures.py` |
| 5–6 | **Final project** — integrated gesture recognition into a complete Pygame arcade game | `main.py`, `entities.py`, `assets.py`, `gesture_input.py` |

---

## Week 1 — Webcam Basics

Opens a webcam feed with OpenCV, overlays a live FPS counter (smoothed over a rolling 30-frame window), and draws a simple on-screen HUD box. Establishes the base capture loop (`cv2.VideoCapture` → read → display → quit-on-`q`) that every later week builds on.

## Week 2 — Edge Detection Toggle

Adds a runtime-togglable **Canny edge-detection view** (`e` to enable, `n` to return to normal), controlled by keypress while the capture loop keeps running. Also introduces `cv2.flip(frame, 1)` to mirror the feed so it behaves like a selfie camera — a detail that matters later, since MediaPipe's handedness assumptions depend on the image being presented this way.

## Week 3 — Hand Landmark Detection

Switches from raw image processing to **MediaPipe's Hand Landmarker** (`mediapipe.tasks` API, `RunningMode.VIDEO`), which returns 21 3D landmarks per detected hand. This week:
- Draws the full hand skeleton (`HAND_CONNECTIONS`) and landmark dots over the live feed
- Implements a first-pass rule-based gesture classifier (`classify_gesture`) using finger up/down state (comparing tip vs. joint y-coordinates) plus a normalized pinch distance for `OK_SIGN`
- Recognizes: `FIST`, `THUMBS_UP`, `POINTING`, `ROCK_ON`, `MIDDLE_POINTING`, `PEACE`, `OK_SIGN`, `OPEN_PALM`

`RunningMode.VIDEO` (rather than single-image mode) was a deliberate choice at this stage — it lets the model use temporal context between frames, giving noticeably more stable predictions during continuous webcam use than re-running detection from scratch every frame.

## Week 4 — Gesture Module + Test Harness

The classifier logic from Week 3 was pulled out into a standalone `gestures.py` module (`classify(lm_list, hand_label)`), decoupled from any OpenCV display code, so it could be imported and reused. `test_gestures.py` became a dedicated harness for verifying the module against a live camera feed independent of any downstream application.


---

## Final Project (Weeks 5–6): Gesture-Controlled Flappy Bird

A complete Flappy Bird clone in Pygame with two selectable input modes — traditional keyboard play, and a fully gesture-driven mode powered by the Week 1–4 pipeline.

### Features

- **Two control modes**, chosen from the main menu:
  - **Keyboard** — `SPACE` to jump / start / restart
  - **Visual** — hand gestures for every action (see table below)
- **State machine** driving the game flow: `Menu → Get Ready → Playing → Game Over`
- **Persistent high score**, saved to `highscore.json` between sessions
- **Live gesture debug readout** on-screen during Visual mode (shows the currently detected gesture name), plus on-screen gesture hints on the Game Over screen
- **Graceful degradation** — if no webcam or hand-landmarker model is available, Visual mode simply fails to activate (with a console message) rather than crashing; Keyboard mode is unaffected either way

### Gesture Mapping

| Gesture | Action | Where it's used |
|---|---|---|
| Open Palm | Start the round | Get Ready screen |
| Open Palm | Jump | During gameplay |
| Thumbs Up | Restart | Game Over screen |
| Fist | Return to menu | Game Over screen |

All gestures are **edge-detected** — each action fires exactly once per fresh detection, not repeatedly while the gesture is held, so a raised palm during gameplay doesn't spam jumps.

### Architecture

```
main.py            State machine, event handling, menu/game-over UI, main loop
entities.py         Bird, Pipe, ParallaxLayer, Button — the actual game objects
assets.py            Constants, asset loading (with placeholder fallback), high-score I/O
gesture_input.py     Wraps gestures.py + MediaPipe into a per-frame poll() the game loop calls
gestures.py           Week 4's gesture classification module, used unmodified
```

`gesture_input.py` is intentionally a thin wrapper: it owns the webcam and `HandLandmarker`, and on each `poll()` reads one frame, runs it through the same `classify()` function from Week 4, and tracks which gesture just transitioned into its "active" state (the edge-detection described above). `main.py` never touches OpenCV or MediaPipe directly — it just asks `gesture_controller.consume_*_signal()` whether an action happened this frame.

### Notable implementation details

- **Delta-time based physics**: webcam capture (`cap.read()`) blocks at the camera's native frame rate, which throttles the game loop below the target 60 FPS in Visual mode. Movement (gravity, pipe speed, background scroll) is scaled by actual elapsed time rather than by tick count, so gameplay speed stays consistent regardless of which mode is active or how fast the loop happens to be running.
- **Randomized pipe spacing**: rather than a fixed gap, each new pipe is spawned once the previous one has cleared a base distance (`PIPE_SPAWN_DISTANCE`) plus a small randomized offset, giving slightly varied rhythm between obstacles instead of a perfectly uniform cadence.
- **Lazy camera initialization**: the webcam and hand-landmarker are only created when Visual mode is actually selected from the menu — Keyboard-only play never touches the camera.

### Running the Project

```bash
pip install pygame opencv-python mediapipe
python main.py
```

Requires `hand_landmarker.task` (MediaPipe's hand landmark model file) in the project root for Visual mode to initialize.

### Possible Extensions

- Multiple visual themes
- Additional gestures mapped to power-ups or alternate game modes
- On-screen camera preview / hand-skeleton overlay during Visual mode for easier calibration
