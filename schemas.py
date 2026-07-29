from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class Token(BaseModel):
    access_token : str
    token_type : str

class UserCreate(BaseModel):
    name : str
    email : str
    password : str
    @field_validator('name')
    @classmethod
    def name_validator(cls, value):
        if len(value.strip())<2:
            raise ValueError("Name must be atleast 2 charecters")
        return value
    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        if '.' not in value or '@' not in value:
            raise ValueError("Enter a proper email")
        return value
    @field_validator('password')
    @classmethod
    def password_validator(cls, value):
        if len(value.strip())<6:
            raise ValueError("Password must be atleast 6 charecters")
        return value

class UserResponse(BaseModel):
    id : int
    name : str
    email : str
    created_at : datetime

class GoalEnum(str, Enum):
    lose_weight = "lose weight"
    build_muscle = "build muscle"
    endurance = "endurance"
    maintain = "maintain"

class ActivityEnum(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"

class UserProfileCreate(BaseModel):
    age: int
    weight: float
    height: float
    goal: GoalEnum
    dietary_preferences: Optional[str] = None
    activity_level: ActivityEnum

class UserProfileResponse(BaseModel):
    id : int
    user_id : int
    age: int
    weight: float
    height: float
    goal: GoalEnum
    dietary_preferences: Optional[str] = None
    activity_level: ActivityEnum
    created_at : datetime

class WorkoutLogCreate(BaseModel):
    exercise : str
    sets : int
    reps : int
    weight_kg : Optional[float] = None
    notes : Optional[str]

class WorkoutLogResponse(BaseModel):
    id : int
    user_id : int
    exercise : str
    sets : int
    reps : int
    weight_kg: Optional[float] = None
    notes : Optional[str] = None
    logged_at : datetime

