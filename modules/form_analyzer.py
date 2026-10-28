import math
import numpy as np

def calculate_angle(a, b, c):
    """Calculates the angle between three points (a, b, c) where b is the vertex."""
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

class FormAnalyzer:
    def __init__(self):
        pass

    def get_joint_coords(self, lm_list, joint_indices):
        """Helper to extract (x,y) for a list of joint indices."""
        coords = []
        for idx in joint_indices:
            # lm_list format: [id, x, y, visibility]
            if idx < len(lm_list):
                coords.append([lm_list[idx][1], lm_list[idx][2]])
            else:
                coords.append([0, 0])
        return coords
        
    def _get_dominant_side_coords(self, lm_list, l_indices, r_indices):
        l_vis = sum([lm_list[idx][3] for idx in l_indices if idx < len(lm_list)])
        r_vis = sum([lm_list[idx][3] for idx in r_indices if idx < len(lm_list)])
        
        if l_vis > r_vis:
            return self.get_joint_coords(lm_list, l_indices)
        else:
            return self.get_joint_coords(lm_list, r_indices)

    def analyze_squat(self, lm_list):
        if not lm_list: return None, ""
        hip, knee, ankle = self._get_dominant_side_coords(lm_list, [23, 25, 27], [24, 26, 28])
        angle = calculate_angle(hip, knee, ankle)
        
        feedback = ""
        if angle > 160: feedback = "Standing straight"
        elif 90 <= angle <= 160: feedback = "Go Lower"
        elif angle < 90: feedback = "Excellent Form"
        return angle, feedback

    def analyze_bicep_curl(self, lm_list):
        if not lm_list: return None, ""
        shoulder, elbow, wrist = self._get_dominant_side_coords(lm_list, [11, 13, 15], [12, 14, 16])
        angle = calculate_angle(shoulder, elbow, wrist)
        
        feedback = ""
        if angle > 150: feedback = "Lowered completely"
        elif 50 <= angle <= 150: feedback = "Keep elbows tucked in"
        elif angle < 50: feedback = "Good squeeze"
        return angle, feedback

    def analyze_push_up(self, lm_list):
        if not lm_list: return None, ""
        shoulder, elbow, wrist = self._get_dominant_side_coords(lm_list, [11, 13, 15], [12, 14, 16])
        angle = calculate_angle(shoulder, elbow, wrist)
        
        feedback = ""
        if angle > 160: feedback = "Up position"
        elif 90 <= angle <= 160: feedback = "Go Lower"
        elif angle < 90: feedback = "Excellent Form"
        return angle, feedback
        
    def analyze_lunge(self, lm_list):
        if not lm_list: return None, ""
        
        # In a lunge, we want to look at the front leg (the one bent more)
        # We can calculate both knee angles and take the sharper one
        l_hip, l_knee, l_ankle = self.get_joint_coords(lm_list, [23, 25, 27])
        r_hip, r_knee, r_ankle = self.get_joint_coords(lm_list, [24, 26, 28])
        
        l_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_angle = calculate_angle(r_hip, r_knee, r_ankle)
        
        angle = min(l_angle, r_angle) # The front leg will have the smaller angle during lunge
        
        feedback = ""
        if angle > 150: feedback = "Standing straight"
        elif 90 <= angle <= 150: feedback = "Go Lower"
        elif angle < 90: feedback = "Excellent Form"
        return angle, feedback
        
    def analyze_jumping_jack(self, lm_list):
        if not lm_list: return None, ""
        # Look at shoulder abduction: angle between hip, shoulder, elbow
        l_hip, l_shoulder, l_elbow = self.get_joint_coords(lm_list, [23, 11, 13])
        angle = calculate_angle(l_hip, l_shoulder, l_elbow)
        
        feedback = ""
        if angle < 45: feedback = "Arms Down"
        elif 45 <= angle <= 130: feedback = "Raise Arms Higher"
        elif angle > 130: feedback = "Excellent Form"
        return angle, feedback
        
    def analyze_plank(self, lm_list):
        if not lm_list: return None, ""
        # Check alignment of shoulder, hip, ankle
        shoulder, hip, ankle = self._get_dominant_side_coords(lm_list, [11, 23, 27], [12, 24, 28])
        angle = calculate_angle(shoulder, hip, ankle)
        
        feedback = ""
        if angle < 160: feedback = "Straighten Back, Lower Hips"
        elif 160 <= angle <= 180: feedback = "Excellent Form"
        return angle, feedback
