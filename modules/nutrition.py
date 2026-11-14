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
        bmi_advice = "Focus on a healthy calorie surplus with nutrient-dense foods to build lean muscle mass."
    elif 18.5 <= bmi < 25.0:
        bmi_status = "Optimal / Healthy"
        bmi_color = "#00ff87"
        bmi_advice = "Your body weight is in an ideal range! Focus on progressive strength training and body recomposition."
    elif 25.0 <= bmi < 30.0:
        bmi_status = "Overweight"
        bmi_color = "#f59e0b"
        bmi_advice = "Focus on a moderate caloric deficit with high protein to protect muscle while cutting body fat."
    else:
        bmi_status = "Obese"
        bmi_color = "#ef4444"
        bmi_advice = "Prioritize sustainable calorie deficit, high-fiber foods, daily walking, and resistance training."
        
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
        strategy_desc = "Burns stored fat while preserving muscle mass (~0.4-0.6 kg fat loss per week)."
    elif "muscle" in goal_lower or "hypertrophy" in goal_lower or "bulk" in goal_lower:
        target_calories = tdee + 350
        strategy = "Lean Surplus (+350 kcal)"
        strategy_desc = "Provides extra energy needed for muscle synthesis without excess fat gain."
    elif "strength" in goal_lower:
        target_calories = tdee + 150
        strategy = "Performance Baseline (+150 kcal)"
        strategy_desc = "Fuel for maximal strength output, central nervous system recovery, and joint health."
    else:
        target_calories = tdee
        strategy = "Maintenance"
        strategy_desc = "Keeps your weight steady while improving body composition and endurance."
        
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
        "bmi_advice": bmi_advice,
        "bmr": int(bmr),
        "tdee": int(tdee),
        "target_calories": target_calories,
        "strategy": strategy,
        "strategy_desc": strategy_desc,
        "protein_g": protein_g,
        "fat_g": fat_g,
        "carb_g": carb_g,
        "water_liters": water_liters
    }


def get_member_action_plan(plan: dict, goal: str, activity: str) -> dict:
    """
    Returns customer-friendly explanations, habit recommendations, 
    and meal suggestions (Veg & Non-Veg) tailored for the gym member.
    """
    target_cals = plan['target_calories']
    protein = plan['protein_g']
    
    meals_veg = [
        {
            "meal": "🍳 Breakfast (Subah ka Nashta)",
            "calories": f"~{int(target_cals * 0.25)} kcal",
            "items": [
                "Oats / Dalia cooked in skimmed milk with almonds & chia seeds",
                "Besan chilla (2) stuffed with paneer or boiled sprouts",
                "1 cup green tea or black coffee (sugar-free)"
            ]
        },
        {
            "meal": "🥗 Lunch (Dopahar ka Khana)",
            "calories": f"~{int(target_cals * 0.35)} kcal",
            "items": [
                "2 Multigrain / Whole wheat rotis OR 1 bowl brown/white rice",
                "150g Low-fat Paneer / Tofu curry or thick Rajma / Dal",
                "1 big bowl cucumber, tomato & carrot salad with curd (dahi)"
            ]
        },
        {
            "meal": "🍌 Pre-Workout Snack (Gym se 45-60 min pehle)",
            "calories": f"~{int(target_cals * 0.15)} kcal",
            "items": [
                "1 Banana with 1 tbsp peanut butter OR 2 brown bread slices with peanut butter",
                "Black coffee (optional) for enhanced focus & training stamina"
            ]
        },
        {
            "meal": "🍲 Dinner (Raat ka Khana - Light & Protein-rich)",
            "calories": f"~{int(target_cals * 0.25)} kcal",
            "items": [
                "150g grilled paneer / soya chunks bhurji with sauteed vegetables",
                "1 roti or quinoa bowl with mixed vegetable soup",
                "Warm turmeric milk (haldi doodh) before bed for muscle recovery"
            ]
        }
    ]

    meals_nonveg = [
        {
            "meal": "🍳 Breakfast (Subah ka Nashta)",
            "calories": f"~{int(target_cals * 0.25)} kcal",
            "items": [
                "3-4 Boiled eggs (2 whole + 2 egg whites) or scrambled eggs",
                "2 slices whole grain toast with avocado or peanut butter",
                "1 bowl fresh fruits (apple, papaya, or berries)"
            ]
        },
        {
            "meal": "🥗 Lunch (Dopahar ka Khana)",
            "calories": f"~{int(target_cals * 0.35)} kcal",
            "items": [
                "150g Grilled / Steamed chicken breast or fish curry",
                "1 cup steamed basmati or brown rice + dal",
                "Green salad with lemon & olive oil dressing"
            ]
        },
        {
            "meal": "🍌 Pre-Workout Fuel (Gym se 45-60 min pehle)",
            "calories": f"~{int(target_cals * 0.15)} kcal",
            "items": [
                "1-2 Bananas or rice cakes with peanut butter",
                "1 scoop Whey Protein in water (or post-workout)"
            ]
        },
        {
            "meal": "🍲 Dinner (Raat ka Khana - High Protein Recovery)",
            "calories": f"~{int(target_cals * 0.25)} kcal",
            "items": [
                "150g Grilled chicken breast / salmon / egg bhurji",
                "Steamed broccoli, beans, carrots, and sweet potato",
                "Plenty of water; avoid high sodium right before sleep"
            ]
        }
    ]

    action_habits = [
        f"🎯 **Protein Goal ({protein}g/day)**: Apne protein ko 3-4 meals mein divide karein (~{protein // 4}g per meal) taaki muscle synthesis active rahe.",
        f"💧 **Hydration Reminder ({plan['water_liters']} Liters)**: Har 2 ghante mein 1-2 glass paani piyein. Dehydration se workout strength 15% tak gir sakti hai.",
        "⏱️ **Meal Timing**: Workout se 1 ghanta pehle carbs lein taaki energy mile, aur workout ke 45 min baad protein lein taaki muscle repair ho sake.",
        "💤 **Sleep & Recovery**: Rozana 7-8 ghante ki uninterrupted neend lein; 90% muscle repair aur growth hormone sleep ke dauran banta hai."
    ]

    return {
        "meals_veg": meals_veg,
        "meals_nonveg": meals_nonveg,
        "habits": action_habits
    }
