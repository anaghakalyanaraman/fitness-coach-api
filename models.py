from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, Text
from typing import Optional


class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key = True)
    name : Mapped[str] = mapped_column(String(100))
    email : Mapped[str] = mapped_column(String(100), unique = True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(255))


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id : Mapped[int] = mapped_column(primary_key = True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    age : Mapped[int] = mapped_column(Integer, default=0)
    weight : Mapped[float] = mapped_column(Float, default=0)
    height : Mapped[float] = mapped_column(Float, default=0)
    goal : Mapped[str] = mapped_column(String(100))
    dietary_preferences: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    activity_level : Mapped[str] = mapped_column(String(50))
    created_at : Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    id : Mapped[int] = mapped_column(primary_key = True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    exercise: Mapped[str] = mapped_column(String(100))
    sets : Mapped[int] = mapped_column(Integer, default=0)
    reps : Mapped[int] = mapped_column(Integer, default=0)
    weight_kg : Mapped[float] = mapped_column(Float, nullable=True)
    notes : Mapped[Optional[str]] = mapped_column(Text, nullable = True)
    logged_at : Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)
    

class WeightLog(Base):
    __tablename__ = "weight_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    weight_kg: Mapped[float] = mapped_column(Float)
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SavedWorkoutPlan(Base):
    __tablename__ = "saved_workout_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_data: Mapped[str] = mapped_column(Text)  # JSON stored as string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)