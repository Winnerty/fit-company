from pydantic import BaseModel

class CreateStatsMessage(BaseModel):
    email: str
    workout_id: int