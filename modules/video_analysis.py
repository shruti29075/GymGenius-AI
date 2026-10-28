import cv2
import numpy as np
import os
import tempfile
import time
from modules.pose_detector import PoseDetector
from modules.form_analyzer import FormAnalyzer
from modules.rep_counter import RepCounter

def analyze_workout_video(input_video_path: str, exercise: str, target_reps: int = 10, progress_callback=None) -> dict:
    """
    Analyzes an offline recorded workout video frame-by-frame, performs biomechanical 
    pose detection, counts repetitions, calculates form accuracy, overlays HUD graphics, 
    and writes an annotated playback video.
    """
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        return {"error": "Could not open video file."}
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
    
    # Scale down if very large for faster processing and smooth display
    target_width = 720
    if width > target_width:
        scale = target_width / width
        out_w = target_width
        out_h = int(height * scale)
    else:
        out_w = width
        out_h = height
        
    # Ensure dimensions are even (required by most video codecs)
    out_w = out_w if out_w % 2 == 0 else out_w - 1
    out_h = out_h if out_h % 2 == 0 else out_h - 1
    
    detector = PoseDetector()
    if detector.error:
        cap.release()
        return {"error": f"PoseDetector initialization failed: {detector.error}"}
        
    analyzer = FormAnalyzer()
    counter = RepCounter()
    counter.target_reps = target_reps
    
    temp_dir = tempfile.gettempdir()
    out_path = os.path.join(temp_dir, f"analyzed_{int(time.time())}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, fps, (out_w, out_h))
    
    frame_idx = 0
    good_form_count = 0
    total_evaluated_frames = 0
    feedback_log = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_idx += 1
        if out_w != width or out_h != height:
            frame = cv2.resize(frame, (out_w, out_h))
            
        timestamp_ms = int((frame_idx / fps) * 1000)
        frame, pose_result = detector.find_pose(frame, timestamp_ms, draw=True)
        lm_list = detector.get_position(frame, pose_result, draw=False)
        
        angle = None
        feedback = "Detecting Pose..."
        
        if lm_list:
            if exercise == "Squat":
                angle, feedback = analyzer.analyze_squat(lm_list)
                count, stage = counter.count_squat_reps(angle)
            elif exercise == "Push Up":
                angle, feedback = analyzer.analyze_push_up(lm_list)
                count, stage = counter.count_push_up_reps(angle)
            elif exercise == "Bicep Curl":
                angle, feedback = analyzer.analyze_bicep_curl(lm_list)
                count, stage = counter.count_bicep_curl_reps(angle)
            elif exercise == "Lunge":
                angle, feedback = analyzer.analyze_lunge(lm_list)
                count, stage = counter.count_lunge_reps(angle)
            elif exercise == "Jumping Jack":
                angle, feedback = analyzer.analyze_jumping_jack(lm_list)
                count, stage = counter.count_jumping_jack_reps(angle)
            elif exercise == "Plank":
                angle, feedback = analyzer.analyze_plank(lm_list)
                count, stage = counter.count_plank_reps(angle)
            else:
                count = counter.count
                stage = counter.stage
                
            total_evaluated_frames += 1
            if "excellent" in feedback.lower() or "good" in feedback.lower() or "standing" in feedback.lower():
                good_form_count += 1
                
            if feedback and (not feedback_log or feedback_log[-1] != feedback):
                feedback_log.append(feedback)
                
            # Draw HUD overlay on video frame
            cv2.rectangle(frame, (10, 10), (320, 130), (19, 25, 36), cv2.FILLED)
            cv2.rectangle(frame, (10, 10), (320, 130), (0, 255, 135), 2)
            cv2.putText(frame, f"REPS: {counter.count} / {target_reps}", (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"SETS: {counter.sets}", (25, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            form_col = (0, 255, 135) if "excellent" in feedback.lower() or "good" in feedback.lower() else (70, 70, 255)
            cv2.putText(frame, f"{feedback[:22]}", (25, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.65, form_col, 2)
            
        out.write(frame)
        
        if progress_callback and total_frames > 0 and frame_idx % 5 == 0:
            progress_callback(min(1.0, frame_idx / total_frames))
            
    cap.release()
    out.release()
    
    total_reps = counter.count + (counter.sets * target_reps)
    accuracy_score = round((good_form_count / total_evaluated_frames * 100), 1) if total_evaluated_frames > 0 else 85.0
    duration_sec = int(frame_idx / fps)
    
    cal_rates = {"Squat": 0.45, "Push Up": 0.50, "Bicep Curl": 0.30, "Lunge": 0.40, "Jumping Jack": 0.20, "Plank": 0.15}
    rate = cal_rates.get(exercise, 0.35)
    calories = round(max(5.0, total_reps * rate * 3.5), 1)
    
    return {
        "output_path": out_path,
        "total_reps": total_reps,
        "sets": max(1, counter.sets if counter.count == 0 and counter.sets > 0 else (counter.sets + 1)),
        "accuracy_score": accuracy_score,
        "duration_sec": max(10, duration_sec),
        "calories": calories,
        "feedback_samples": feedback_log[:5]
    }

