from pydantic import BaseModel
from typing import List, Optional

class WorkoutCreatedMessage(BaseModel):
    user_id: str
    date: str
    workout_type: str
    exercises: List[int]
    