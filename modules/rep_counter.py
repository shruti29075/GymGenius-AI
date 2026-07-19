class RepCounter:
    def __init__(self):
        self.count = 0
        self.direction = 0 # 0 for down, 1 for up
        self.stage = None # "down" or "up" (or "in" or "out")
        self.sets = 0
        self.target_reps = 10
        self.is_completed = False

    def reset(self):
        self.count = 0
        self.direction = 0
        self.stage = None
        self.is_completed = False

    def _increment(self):
        self.count += 1
        if self.count >= self.target_reps:
            self.sets += 1
            self.is_completed = True
            self.count = 0 # Reset count for next set

    def count_squat_reps(self, angle):
        if angle is None: return self.count, self.stage
        if angle < 90:
            if self.stage == "up" or self.stage is None:
                self.stage = "down"
        if angle > 160:
            if self.stage == "down":
                self.stage = "up"
                self._increment()
        return self.count, self.stage

    def count_bicep_curl_reps(self, angle):
        if angle is None: return self.count, self.stage
        if angle < 50:
            if self.stage == "down" or self.stage is None:
                self.stage = "up"
        if angle > 150:
            if self.stage == "up":
                self.stage = "down"
                self._increment()
        return self.count, self.stage

    def count_push_up_reps(self, angle):
        if angle is None: return self.count, self.stage
        if angle < 90:
            if self.stage == "up" or self.stage is None:
                self.stage = "down"
        if angle > 160:
            if self.stage == "down":
                self.stage = "up"
                self._increment()
        return self.count, self.stage
        
    def count_lunge_reps(self, angle):
        if angle is None: return self.count, self.stage
        if angle < 90:
            if self.stage == "up" or self.stage is None:
                self.stage = "down"
        if angle > 150:
            if self.stage == "down":
                self.stage = "up"
                self._increment()
        return self.count, self.stage
        
    def count_jumping_jack_reps(self, angle):
        if angle is None: return self.count, self.stage
        if angle > 130:
            if self.stage == "down" or self.stage is None:
                self.stage = "up"
        if angle < 45:
            if self.stage == "up":
                self.stage = "down"
                self._increment()
        return self.count, self.stage
        
    def count_plank_reps(self, angle):
        # Plank is a hold exercise. Rep counting doesn't cleanly apply here.
        # But for the sake of consistency in the UI, we can return 0 reps,
        # or we could implement a timer if we had timestamp access.
        # For this requirement, we will just return a static count.
        return self.count, "holding"
