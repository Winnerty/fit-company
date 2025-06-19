from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from .database import Base


class ExercisePerformed(Base):
    __tablename__ = "performed_exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    actual_reps = Column(Integer, nullable=True)
    actual_weight = Column(Float, nullable=True)
    performed_at = Column(DateTime, nullable=False)

    workout_id = Column(Integer, ForeignKey("workout_stats.id"))
    workouts = relationship("WorkoutStats", back_populates="exercises")


class WorkoutStats(Base):
    __tablename__ = "workout_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    generated_at = Column(DateTime, nullable=False)
    user_email = Column(String, nullable=False, index=True)

    exercises = relationship("ExercisePerformed", back_populates="workouts")
