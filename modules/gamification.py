import pandas as pd
from datetime import datetime, date, timedelta
from database.db import get_connection

def calculate_streak(df: pd.DataFrame) -> int:
    """Calculates consecutive active days of workouts."""
    if df.empty or 'date' not in df.columns:
        return 0
    
    # Extract unique sorted dates (as date objects)
    dates = pd.to_datetime(df['date']).dt.date.drop_duplicates().sort_values(ascending=False).tolist()
    if not dates:
        return 0
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # If the user hasn't worked out today or yesterday, streak is reset to 0
    if dates[0] not in (today, yesterday):
        return 0
    
    streak = 1
    for i in range(len(dates) - 1):
        if dates[i] - dates[i+1] == timedelta(days=1):
            streak += 1
        else:
            break
            
    return streak

def calculate_athlete_level(df: pd.DataFrame) -> dict:
    """Calculates XP, Level tier, and progress towards next level."""
    if df.empty:
        total_reps = 0
        total_workouts = 0
        total_cal = 0
    else:
        total_reps = int(df['reps'].sum())
        total_workouts = len(df)
        total_cal = float(df['calories'].sum())
        
    xp = int((total_reps * 10) + (total_workouts * 100) + (total_cal * 0.4))
    
    tiers = [
        (1, "Rookie Athlete", 0, 500, "🌱"),
        (2, "Dedicated Lifter", 500, 1500, "⚡"),
        (3, "Iron Warrior", 1500, 3500, "⚔️"),
        (4, "Beast Mode", 3500, 7500, "🦍"),
        (5, "Hyper Titan", 7500, 15000, "👑"),
    ]
    
    current_tier = tiers[0]
    for tier in tiers:
        if xp >= tier[2]:
            current_tier = tier
            
    lvl, title, min_xp, max_xp, badge_icon = current_tier
    progress_range = max_xp - min_xp
    current_in_range = max(0, min(xp - min_xp, progress_range))
    progress_pct = int((current_in_range / progress_range) * 100) if progress_range > 0 else 100
    
    return {
        "level": lvl,
        "title": title,
        "badge_icon": badge_icon,
        "xp": xp,
        "min_xp": min_xp,
        "next_xp": max_xp,
        "progress_pct": progress_pct,
        "total_reps": total_reps,
        "total_workouts": total_workouts,
        "total_cal": round(total_cal, 1)
    }

def get_user_badges(df: pd.DataFrame) -> list:
    """Evaluates achievements and unlocked trophies based on workout records."""
    total_workouts = len(df) if not df.empty else 0
    total_reps = int(df['reps'].sum()) if not df.empty else 0
    total_cal = float(df['calories'].sum()) if not df.empty else 0
    unique_exercises = df['exercise'].nunique() if not df.empty else 0
    streak = calculate_streak(df)
    has_high_accuracy = (df['accuracy_score'] >= 95.0).any() if (not df.empty and 'accuracy_score' in df.columns) else False
    
    badges = [
        {
            "id": "first_workout",
            "name": "First Blood",
            "icon": "🥊",
            "description": "Completed your very first workout session",
            "unlocked": total_workouts >= 1
        },
        {
            "id": "streak_3",
            "name": "Consistency King",
            "icon": "🔥",
            "description": "Maintained an active 3-day workout streak",
            "unlocked": streak >= 3
        },
        {
            "id": "century_reps",
            "name": "Centurion",
            "icon": "💯",
            "description": "Pumped out 100+ total lifetime repetitions",
            "unlocked": total_reps >= 100
        },
        {
            "id": "volume_500",
            "name": "Volume Monster",
            "icon": "🦍",
            "description": "Reached 500+ total lifetime repetitions",
            "unlocked": total_reps >= 500
        },
        {
            "id": "perfectionist",
            "name": "Form Perfectionist",
            "icon": "🎯",
            "description": "Scored 95%+ movement biomechanical accuracy",
            "unlocked": has_high_accuracy
        },
        {
            "id": "calorie_crusher",
            "name": "Calorie Torcher",
            "icon": "⚡",
            "description": "Burned over 1,000 total active kilocalories",
            "unlocked": total_cal >= 1000.0
        },
        {
            "id": "all_rounder",
            "name": "All-Rounder",
            "icon": "🌟",
            "description": "Trained across at least 4 distinct exercise movements",
            "unlocked": unique_exercises >= 4
        },
        {
            "id": "veteran",
            "name": "Gym Veteran",
            "icon": "🏆",
            "description": "Logged 10+ completed workout sessions",
            "unlocked": total_workouts >= 10
        }
    ]
    return badges

def get_community_leaderboard() -> list:
    """Fetches top athletes across the platform ranked by total workouts & reps."""
    conn = get_connection()
    query = """
        SELECT u.id, u.username, 
               COUNT(w.id) as workout_count,
               COALESCE(SUM(w.reps), 0) as total_reps,
               COALESCE(SUM(w.calories), 0) as total_calories
        FROM users u
        LEFT JOIN workouts w ON u.id = w.user_id
        GROUP BY u.id, u.username
        ORDER BY total_reps DESC, workout_count DESC
        LIMIT 10
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    
    leaderboard = []
    for rank, row in enumerate(rows, start=1):
        leaderboard.append({
            "rank": rank,
            "username": row["username"],
            "workouts": row["workout_count"],
            "reps": row["total_reps"],
            "calories": round(row["total_calories"], 0)
        })
    return leaderboard

