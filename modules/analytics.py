import pandas as pd
import plotly.express as px
from database.db import get_connection

def fetch_user_workouts(user_id):
    """Fetches all workouts for a specific user as a pandas DataFrame."""
    conn = get_connection()
    query = "SELECT * FROM workouts WHERE user_id = ?"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

def save_workout(user_id, exercise, reps, sets, duration, accuracy, calories):
    """Saves a completed workout session to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO workouts (user_id, exercise, reps, sets, duration_seconds, accuracy_score, calories)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, exercise, reps, sets, duration, accuracy, calories))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving workout: {e}")
        return False
    finally:
        conn.close()

def plot_calories_over_time(df):
    """Returns a Plotly figure showing calories burned over time."""
    if df.empty:
        return None
        
    daily_calories = df.groupby(df['date'].dt.date)['calories'].sum().reset_index()
    fig = px.line(daily_calories, x='date', y='calories', title="Calories Burned Over Time", markers=True)
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFA500'))
    fig.update_traces(line_color='#FFA500')
    return fig

def plot_exercise_distribution(df):
    """Returns a Plotly pie chart of exercises done."""
    if df.empty:
        return None
        
    exercise_counts = df['exercise'].value_counts().reset_index()
    exercise_counts.columns = ['exercise', 'count']
    fig = px.pie(exercise_counts, names='exercise', values='count', title="Exercise Distribution", hole=0.4)
    fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig
