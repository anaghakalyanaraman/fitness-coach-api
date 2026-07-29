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

def chat_with_coach(message: str, conversation_history: list, user_profile: dict) -> str:
    system_prompt = f"""You are a personal fitness and nutrition coach. 
    
User Profile:
- Age: {user_profile.get('age')}
- Weight: {user_profile.get('weight')} kg
- Height: {user_profile.get('height')} cm
- Goal: {user_profile.get('goal')}
- Activity Level: {user_profile.get('activity_level')}
- Dietary Preferences: {user_profile.get('dietary_preferences', 'No restrictions')}

Give personalized, practical advice based on the user's profile. Be concise and friendly."""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content

def generate_recipe(ingredients: list, meal_type: str, goal: str) -> dict:
    prompt = f"""
You are a professional chef and nutritionist.

Create a detailed recipe using these ingredients: {', '.join(ingredients)}
Meal type: {meal_type}
Fitness goal: {goal}

Return ONLY a valid JSON object:
{{
    "recipe_name": "string",
    "prep_time_minutes": 10,
    "cook_time_minutes": 20,
    "servings": 2,
    "ingredients": [
        {{
            "item": "string",
            "quantity": "string"
        }}
    ],
    "instructions": [
        "Step 1: string",
        "Step 2: string"
    ],
    "nutrition_per_serving": {{
        "calories": 300,
        "protein_g": 25,
        "carbs_g": 30,
        "fat_g": 10
    }},
    "tips": "string"
}}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)