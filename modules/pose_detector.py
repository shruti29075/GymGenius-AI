import cv2
import numpy as np
import os
import requests

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, 'pose_landmarker_full.task')
MODEL_URL = 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/pose_landmarker_full.task'

def download_model_if_missing():
    if not os.path.exists(MODEL_PATH):
        try:
            print("Downloading MediaPipe Pose model...")
            response = requests.get(MODEL_URL, stream=True)
            response.raise_for_status()
            with open(MODEL_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Model downloaded successfully.")
            return True
        except Exception as e:
            print(f"Failed to download model: {e}")
            return False
    return True

# Define MediaPipe Pose Connections manually to avoid needing legacy solutions.drawing_utils
POSE_CONNECTIONS = frozenset([
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20), (11, 23),
    (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28), (27, 29),
    (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)
])

class PoseDetector:
    def __init__(self):
        self.detector = None
        self.error = None
        
        if not MP_AVAILABLE:
            self.error = "MediaPipe is not installed. Please check requirements."
            return

        if not download_model_if_missing():
            self.error = "Failed to download MediaPipe model. Please check your internet connection."
            return

        try:
            base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.VIDEO,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
        except Exception as e:
            self.error = f"Failed to initialize PoseLandmarker: {e}"

    def draw_landmarks(self, img, landmarks):
        """Custom drawing function to replace mp.solutions.drawing_utils"""
        h, w, c = img.shape
        
        # Draw connections
        for connection in POSE_CONNECTIONS:
            start_idx = connection[0]
            end_idx = connection[1]
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                lm1 = landmarks[start_idx]
                lm2 = landmarks[end_idx]
                # Only draw if both points are reasonably visible
                if lm1.visibility > 0.5 and lm2.visibility > 0.5:
                    x1, y1 = int(lm1.x * w), int(lm1.y * h)
                    x2, y2 = int(lm2.x * w), int(lm2.y * h)
                    cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    
        # Draw points
        for lm in landmarks:
            if lm.visibility > 0.5:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 4, (245, 117, 66), cv2.FILLED)

    def find_pose(self, img, timestamp_ms, draw=True):
        if self.error:
            return img, None
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        try:
            pose_result = self.detector.detect_for_video(mp_image, timestamp_ms)
            if draw and pose_result.pose_landmarks:
                for landmarks in pose_result.pose_landmarks:
                    self.draw_landmarks(img, landmarks)
            return img, pose_result
        except Exception as e:
            print(f"Detection error: {e}")
            return img, None

    def get_position(self, img, pose_result, draw=False):
        lm_list = []
        if not pose_result:
            return lm_list
            
        if pose_result.pose_landmarks:
            landmarks = pose_result.pose_landmarks[0]
            for id, lm in enumerate(landmarks):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy, lm.visibility])
                if draw and lm.visibility > 0.5:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lm_list
