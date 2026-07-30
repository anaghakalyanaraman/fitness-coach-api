from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import User, UserProfile, WorkoutLog
from schemas import UserCreate, UserResponse, Token 
from schemas import UserProfileCreate, UserProfileResponse, WorkoutLogCreate, WorkoutLogResponse, MealPlanRequest
from auth import hash_password, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from ai_service import generate_workout_plan
from ai_service import generate_workout_plan, generate_meal_plan
from typing import List
from ai_service import generate_workout_plan, generate_meal_plan, chat_with_coach, generate_recipe
from schemas import ChatMessage, ChatResponse, RecipeRequest
from models import User, UserProfile, WorkoutLog, WeightLog, SavedWorkoutPlan
from schemas import WeightLogCreate, WeightLogResponse, ProgressResponse
import json
from fastapi import Request
from fastapi.responses import JSONResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
         "https://fitness-coach-ui-5ms1.vercel.app"
         "https://fitness-coach-ui-qk6l.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

#auth Endpoints

#1. POST /auth/register - response_model=UserResponse

@app.post("/auth/register", response_model= UserResponse)
async def register_user(user : UserCreate, db = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    hpass = hash_password(user.password)
    db_user = User(name = user.name, email = user.email, hashed_password = hpass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
#2. POST /auth/login - response_model=Token

@app.post("/auth/login", response_model= Token)
async def login_auth(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Email not found")
    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong password")
    token = create_access_token({"sub": db_user.email}, timedelta(minutes=30))
    return Token(access_token=token, token_type="bearer")

# Profile Routes

#1. Create User Profile
@app.post("/profile", response_model= UserProfileResponse)
async def create_profile(profile : UserProfileCreate, current_user = Depends(get_current_user), db = Depends(get_db)):
    db_profiles = UserProfile(user_id = current_user.id, age = profile.age, weight = profile.weight, height = profile.height, goal = profile.goal , dietary_preferences = profile.dietary_preferences, activity_level = profile.activity_level)
    db.add(db_profiles)
    db.commit()
    db.refresh(db_profiles)
    return db_profiles

#2. Get current user's profile
@app.get("/profile")
async def current_user(current_user = Depends(get_current_user), db = Depends(get_db)):
    db_profiles = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    #profiles_data = [{"id":p.id, "user_id": p.user_id, "age" : p.age, "weight":p.weight, "height":p.height,"goal":p.goal, "dietary_preferences":p.dietary_preferences, "activity_level":p.activity_level, "created_at":p.created_at} for p in db_profiles]
    return db_profiles

#3. Update User profile
@app.put("/profile", response_model= UserProfileResponse)
async def update_user(profile : UserProfileCreate, current_user = Depends(get_current_user), db = Depends(get_db)):
    db_profiles = db.query(UserProfile).filter(user_id = current_user.id).first()
    if not db_profiles:
        raise HTTPException(status_code=404, detail = "Profile not found")
    db_profiles.age = profile.age
    db_profiles.weight = profile.weight
    db_profiles.height = profile.height
    db_profiles.goal = profile.goal
    db_profiles.dietary_preferences = profile.dietary_preferences
    db_profiles.activity_level = profile.activity_level
    db.commit()
    db.refresh(db_profiles)
    return db_profiles

#Workout Routes
#1. Create Workout logs
@app.post("/logs",response_model= WorkoutLogResponse)
async def create_workoutlog(wlog : WorkoutLogCreate, current_user = Depends(get_current_user), db = Depends(get_db)):
    db_wlog = WorkoutLog(user_id = current_user.id, exercise = wlog.exercise, sets = wlog.sets, reps = wlog.reps, weight_kg = wlog.weight_kg, notes = wlog.notes)
    db.add(db_wlog)
    db.commit()
    db.refresh(db_wlog)
    return db_wlog

#2. Get all workoutlogs
@app.get("/logs")
async def get_logs(current_user = Depends(get_current_user), db = Depends(get_db)):
    db_logs = db.query(WorkoutLog).filter(WorkoutLog.user_id == current_user.id).all()
    return db_logs

#3. Delete specific log
@app.delete("/logs/{log_id}", response_model=WorkoutLogResponse)
async def delete_log(log_id: int, current_user = Depends(get_current_user), db = Depends(get_db)):
    db_log = db.query(WorkoutLog).filter(WorkoutLog.id == log_id, WorkoutLog.user_id == current_user.id).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(db_log)
    db.commit()
    return db_log 


# POST /workout-plan - generate AI workout plan
@app.post("/workout-plan")
async def create_workout_plan(current_user = Depends(get_current_user), db = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please create your profile first.")
    
    plan = generate_workout_plan(
        age=profile.age,
        weight=profile.weight,
        height=profile.height,
        goal=profile.goal,
        activity_level=profile.activity_level
    )
    return plan


@app.post("/nutrition/meal-plan")
async def create_meal_plan(request: MealPlanRequest, current_user = Depends(get_current_user), db = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    meal_plan = generate_meal_plan(
        ingredients=request.ingredients,
        goal=profile.goal,
        dietary_preferences=profile.dietary_preferences
    )
    return meal_plan

# POST /chat - conversational AI coach
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage, current_user = Depends(get_current_user), db = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    user_profile = {
        "age": profile.age,
        "weight": profile.weight,
        "height": profile.height,
        "goal": profile.goal,
        "activity_level": profile.activity_level,
        "dietary_preferences": profile.dietary_preferences
    }
    
    response = chat_with_coach(
        message=request.message,
        conversation_history=request.conversation_history,
        user_profile=user_profile
    )
    return ChatResponse(response=response)

# POST /nutrition/recipe - generate detailed recipe
@app.post("/nutrition/recipe")
async def create_recipe(request: RecipeRequest, current_user = Depends(get_current_user), db = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    recipe = generate_recipe(
        ingredients=request.ingredients,
        meal_type=request.meal_type,
        goal=profile.goal
    )
    return recipe

# POST /weight-log - log current weight
@app.post("/weight-log", response_model=WeightLogResponse)
async def log_weight(log: WeightLogCreate, current_user = Depends(get_current_user), db = Depends(get_db)):
    db_log = WeightLog(user_id=current_user.id, weight_kg=log.weight_kg)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# GET /weight-log - get all weight logs
@app.get("/weight-log")
async def get_weight_logs(current_user = Depends(get_current_user), db = Depends(get_db)):
    logs = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.logged_at).all()
    return logs

# POST /workout-plan/save - save generated workout plan
@app.post("/workout-plan/save")
async def save_workout_plan(current_user = Depends(get_current_user), db = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    plan = generate_workout_plan(
        age=profile.age,
        weight=profile.weight,
        height=profile.height,
        goal=profile.goal,
        activity_level=profile.activity_level
    )
    db_plan = SavedWorkoutPlan(user_id=current_user.id, plan_data=json.dumps(plan))
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return plan

# GET /progress - get user progress summary
@app.get("/progress")
async def get_progress(current_user = Depends(get_current_user), db = Depends(get_db)):
    total_workouts = db.query(WorkoutLog).filter(WorkoutLog.user_id == current_user.id).count()
    weight_logs = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.logged_at).all()
    recent_logs = db.query(WorkoutLog).filter(WorkoutLog.user_id == current_user.id).order_by(WorkoutLog.logged_at.desc()).limit(5).all()
    
    starting_weight = weight_logs[0].weight_kg if weight_logs else None
    current_weight = weight_logs[-1].weight_kg if weight_logs else None
    weight_change = round(current_weight - starting_weight, 2) if starting_weight and current_weight else None
    
    return {
        "total_workouts": total_workouts,
        "current_weight": current_weight,
        "starting_weight": starting_weight,
        "weight_change": weight_change,
        "recent_exercises": [log.exercise for log in recent_logs]
    }
