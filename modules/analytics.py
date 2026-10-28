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
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='#131924',
        paper_bgcolor='#131924',
        font=dict(color='#e6edf3', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        title_font=dict(size=16, color='#ffffff'),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)', linecolor='rgba(255,255,255,0.1)', tickfont=dict(color='#8b949e')),
        yaxis=dict(gridcolor='rgba(255,255,255,0.06)', linecolor='rgba(255,255,255,0.1)', tickfont=dict(color='#8b949e'))
    )
    fig.update_traces(
        line=dict(color='#00ff87', width=3),
        marker=dict(size=8, color='#00ff87', line=dict(width=2, color='#ffffff'))
    )
    return fig

def plot_exercise_distribution(df):
    """Returns a Plotly pie chart of exercises done."""
    if df.empty:
        return None
        
    exercise_counts = df['exercise'].value_counts().reset_index()
    exercise_counts.columns = ['exercise', 'count']
    palette = ['#00ff87', '#00d2ff', '#7928ca', '#ff0080', '#f5a623', '#0070f3']
    fig = px.pie(
        exercise_counts,
        names='exercise',
        values='count',
        title="Exercise Distribution",
        hole=0.45,
        color_discrete_sequence=palette
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='#131924',
        paper_bgcolor='#131924',
        font=dict(color='#e6edf3', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'),
        title_font=dict(size=16, color='#ffffff'),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(font=dict(color='#c9d1d9'))
    )
    fig.update_traces(
        textfont=dict(color='#ffffff'),
        marker=dict(line=dict(color='#131924', width=2))
    )
    return fig
