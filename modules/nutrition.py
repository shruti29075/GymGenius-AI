def calculate_nutrition_plan(weight_kg: float, height_cm: float, age: int, gender: str, goal: str = "Hypertrophy", activity: str = "Moderate") -> dict:
    """
    Calculates scientific BMR, TDEE, Calorie Targets, and Macro Splits 
    using the Mifflin-St Jeor Equation and sports nutrition guidelines.
    """
    weight_kg = float(weight_kg) if weight_kg else 70.0
    height_cm = float(height_cm) if height_cm else 170.0
    age = int(age) if age else 25
    gender = str(gender).capitalize() if gender else "Male"
    goal = str(goal).strip() if goal else "Hypertrophy"
    
    # 1. Body Mass Index (BMI)
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        bmi_status = "Underweight"
        bmi_color = "#38bdf8"
    elif 18.5 <= bmi < 25.0:
        bmi_status = "Optimal / Healthy"
        bmi_color = "#00ff87"
    elif 25.0 <= bmi < 30.0:
        bmi_status = "Overweight"
        bmi_color = "#f59e0b"
    else:
        bmi_status = "Obese"
        bmi_color = "#ef4444"
        
    # 2. Basal Metabolic Rate (BMR) - Mifflin-St Jeor formula
    if gender == "Female":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        
    # 3. Total Daily Energy Expenditure (TDEE)
    multipliers = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725
    }
    tdee = bmr * multipliers.get(activity, 1.55)
    
    # 4. Target Calorie Adjustment based on Fitness Goal
    goal_lower = goal.lower()
    if "fat loss" in goal_lower or "weight loss" in goal_lower or "cut" in goal_lower:
        target_calories = tdee - 500
        strategy = "Caloric Deficit (-500 kcal)"
    elif "muscle" in goal_lower or "hypertrophy" in goal_lower or "bulk" in goal_lower:
        target_calories = tdee + 350
        strategy = "Lean Surplus (+350 kcal)"
    elif "strength" in goal_lower:
        target_calories = tdee + 150
        strategy = "Performance Baseline (+150 kcal)"
    else:
        target_calories = tdee
        strategy = "Maintenance"
        
    target_calories = max(1200, int(target_calories))
    
    # 5. Daily Macronutrients Breakdown (Sports Nutrition Standards)
    # High protein for athletes (2.0g per kg bodyweight)
    protein_g = int(weight_kg * 2.0)
    protein_kcal = protein_g * 4
    
    # Healthy dietary fats (25% of total caloric intake)
    fat_kcal = target_calories * 0.25
    fat_g = int(fat_kcal / 9)
    
    # Remaining calories allocated to complex carbohydrates
    carb_kcal = max(0, target_calories - (protein_kcal + fat_kcal))
    carb_g = int(carb_kcal / 4)
    
    # 6. Hydration recommendation (approx 35 ml per kg bodyweight)
    water_liters = round((weight_kg * 0.035) + 0.5, 1) # extra 0.5L for training perspiration
    
    return {
        "bmi": round(bmi, 1),
        "bmi_status": bmi_status,
        "bmi_color": bmi_color,
        "bmr": int(bmr),
        "tdee": int(tdee),
        "target_calories": target_calories,
        "strategy": strategy,
        "protein_g": protein_g,
        "fat_g": fat_g,
        "carb_g": carb_g,
        "water_liters": water_liters
    }

