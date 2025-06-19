from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ExercisePerformedSchema(BaseModel):
    name: str
    actual_reps: Optional[int] = None
    actual_weight: Optional[float] = None
    performed_at: datetime


class WorkoutStatsSchema(BaseModel):
    user_email: str
    generated_at: datetime
    exercises: List[ExercisePerformedSchema]