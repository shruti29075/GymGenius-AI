import bcrypt
from database.db import get_connection

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a password against a hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, password, age=None, gender=None, weight=None, height=None, fitness_goal=None):
    """Registers a new user in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."
    
    hashed_pwd = hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, age, gender, weight, height, fitness_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, hashed_pwd, age, gender, weight, height, fitness_goal))
        conn.commit()
        conn.close()
        return True, "User registered successfully."
    except Exception as e:
        conn.close()
        return False, str(e)

def login_user(username, password):
    """Authenticates a user and returns user data if successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user['password_hash']):
        return True, dict(user)
    return False, "Invalid username or password."

def update_user_profile(user_id, age, gender, weight, height, fitness_goal):
    """Updates user profile information."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE users
            SET age = ?, gender = ?, weight = ?, height = ?, fitness_goal = ?
            WHERE id = ?
        ''', (age, gender, weight, height, fitness_goal, user_id))
        conn.commit()
        conn.close()
        return True, "Profile updated successfully."
    except Exception as e:
        conn.close()
        return False, str(e)
