from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_workout_plan(age: int, weight: float, height: float, goal: str, activity_level: str) -> dict:
    prompt = f"""
You are a professional fitness coach. Generate a personalized 7-day workout plan.

User Profile:
- Age: {age}
- Weight: {weight} kg
- Height: {height} cm
- Goal: {goal}
- Activity Level: {activity_level}

Return ONLY a valid JSON object in this exact format, no other text:
{{
    "plan_name": "string",
    "goal": "string",
    "duration_weeks": 1,
    "days": [
        {{
            "day": "Monday",
            "focus": "string",
            "exercises": [
                {{
                    "name": "string",
                    "sets": 3,
                    "reps": "string",
                    "rest_seconds": 60
                }}
            ]
        }}
    ],
    "notes": "string"
}}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def generate_meal_plan(ingredients: list, goal: str, dietary_preferences: str = None) -> dict:
    prompt = f"""
You are a professional nutritionist. Generate a meal plan using the available ingredients.

Available Ingredients: {', '.join(ingredients)}
Fitness Goal: {goal}
Dietary Preferences: {dietary_preferences or 'No restrictions'}

Return ONLY a valid JSON object in this exact format, no other text:
{{
    "meals": [
        {{
            "meal_type": "Breakfast",
            "name": "string",
            "ingredients": ["string"],
            "instructions": "string",
            "calories": 300,
            "protein_g": 20,
            "carbs_g": 30,
            "fat_g": 10
        }}
    ],
    "total_calories": 1500,
    "notes": "string"
}}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)