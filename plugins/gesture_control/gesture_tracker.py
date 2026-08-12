#!/usr/bin/env python3
"""MediaPipe & OpenCV Hand Gesture Tracking Module for Mouse Control."""

import math
import sys

def main():
    try:
        import cv2
        import mediapipe as mp
        import pyautogui
    except ImportError:
        print("Required packages missing. Install with: pip install opencv-python mediapipe pyautogui")
        sys.exit(1)

    pyautogui.FAILSAFE = False
    screen_w, screen_h = pyautogui.size()

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        sys.exit(1)

    print("Gesture Tracker Active. Press 'q' in the camera preview window to exit.")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_image)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                # Map index finger coordinates to screen coordinates
                cursor_x = int(index_tip.x * screen_w)
                cursor_y = int(index_tip.y * screen_h)
                pyautogui.moveTo(cursor_x, cursor_y)

                # Calculate distance between thumb and index finger for pinch click
                dx = (index_tip.x - thumb_tip.x) * w
                dy = (index_tip.y - thumb_tip.y) * h
                dist = math.hypot(dx, dy)

                if dist < 30:
                    pyautogui.click()
                    cv2.putText(image, "PINCH CLICK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Brahma AI - Gesture Control", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
