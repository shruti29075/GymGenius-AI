import google.generativeai as genai
import os

def generate_workout_plan(api_key, age, gender, weight, height, goal, level="Beginner"):
    """
    Generates a personalized workout plan using Gemini AI.
    Returns a markdown formatted string.
    """
    if not api_key:
        return "Error: Gemini API key is missing. Please configure it in settings."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Act as a professional fitness coach. Create a personalized weekly workout plan based on the following user profile:
        - Age: {age}
        - Gender: {gender}
        - Weight: {weight} kg
        - Height: {height} cm
        - Fitness Goal: {goal}
        - Experience Level: {level}
        
        The workout plan should include:
        1. Weekly schedule (Days of the week)
        2. Suggested Exercises for each day with Reps and Sets
        3. Recovery and nutrition advice
        
        Format the response in clean Markdown with appropriate headings and bullet points.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating workout plan: {str(e)}"
