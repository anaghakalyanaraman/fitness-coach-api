from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import User, UserProfile, WorkoutLog
from schemas import UserCreate, UserResponse, Token 
from schemas import UserProfileCreate, UserProfileResponse, WorkoutLogCreate, WorkoutLogResponse
from auth import hash_password, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    db_wlog = WorkoutLog(user_id = current_user.id, excercise = wlog.excercise, sets = wlog.sets, reps = wlog.reps, weight_kg = wlog.weight_kg, notes = wlog.notes)
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

    