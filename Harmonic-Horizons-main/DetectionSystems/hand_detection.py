import cv2, os, sys
import mediapipe as mp
import numpy as np
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from Settings.settings import SettingsManager

def run_hand_detection(detection_results, lock):
    # Initialize video capture
    setting = SettingsManager()
    cap = cv2.VideoCapture(0)

    # Create hand position detector
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
        
    # Configure pose detection
    pose = mp_pose.Pose(min_detection_confidence=setting.motion_detection_sensitivity, min_tracking_confidence=setting.motion_detection_sensitivity)

    while cap.isOpened():
        # Read frame from camera
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert the frame to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and find body landmarks
        results = pose.process(image_rgb)
        
        if results.pose_landmarks:
            # Get shoulder and hip landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Get required landmarks
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
            left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            
            # Update shared state based on hand positions
            with lock:
                detection_results['left_hand_up'] = left_hand.y < left_shoulder.y
                detection_results['right_hand_up'] = right_hand.y < right_shoulder.y
                detection_results['left_hand_down'] = abs(left_hand.y - left_hip.y) <= 0.1
                detection_results['right_hand_down'] = abs(right_hand.y - right_hip.y) <= 0.1
                detection_results['cross_arm'] = abs(right_hand.x - left_shoulder.x) < 0.1 and abs(left_hand.x -right_shoulder.x) < 0.1

        # Display results
        text_lines = [
            f"Left Hand Up: {detection_results['left_hand_up']}",
            f"Right Hand Up: {detection_results['right_hand_up']}",
            f"Left Hand Down: {detection_results['left_hand_down']}",
            f"Right Hand Down: {detection_results['right_hand_down']}"
        ]
        
        # Draw text on frame
        for i, line in enumerate(text_lines):
            cv2.putText(frame, line, (10, 30 + i * 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                        (0, 255, 0), 2)
        
        # Show the frame
        cv2.imshow('Hand Position Control', frame)
        
        # Break loop on 'q' key press
        if cv2.waitKey(10) & 0xFF == ord('q') or detection_results["ended"]:
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    detection_results = {
        "right_hand_up": False,
        "left_hand_up": False,
        "right_hand_down": False,
        "left_hand_down": False,
        "clapped": False,
        "cross_arm": False,
        "ended": False

    }
    run_hand_detection(detection_results)
