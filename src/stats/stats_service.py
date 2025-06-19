import logging
import os
import random
import datetime
import requests
from typing import Optional, List
from .models_db import ExercisePerformed, WorkoutStats
from .models_dto import WorkoutStatsSchema, ExercisePerformedSchema
from .database import db_session

logger = logging.getLogger(__name__)

monolith_url = os.getenv("MONOLITH_URL")
coach_url = os.getenv("COACH_URL")
headers = {"X-API-Key": os.getenv("FIT_API_KEY")}


def generate_workout_stats(user_email: str) -> Optional[WorkoutStatsSchema]:

    db = db_session()
    try:
        resp = requests.post(f"{monolith_url}/workouts/last", headers=headers, json={"email": user_email})
        resp.raise_for_status()
        exercise_ids = resp.json()

        if not exercise_ids:
            logger.info(f"No last workout found for user {user_email}")
            return None

        workout_stats = WorkoutStats(
            generated_at=datetime.datetime.now(datetime.timezone.utc),
            user_email=user_email
        )
        db.add(workout_stats)
        db.flush() 

        exercise_schemas = []
        for ex_id in exercise_ids:
            ex_resp = requests.get(f"{coach_url}/exercises/{ex_id}")
            ex_resp.raise_for_status()
            ex_data = ex_resp.json()

            performed = ExercisePerformed(
                name=ex_data["name"],
                actual_reps=random.randint(8, 15),
                actual_weight=round(random.uniform(5.0, 50.0), 1),
                performed_at=datetime.datetime.utcnow(),
                workout_id=workout_stats.id
            )
            db.add(performed)
            exercise_schemas.append(performed)

        db.commit()
        logger.info(f"Workout stats generated for user {user_email}")

        return WorkoutStatsSchema(
            id=workout_stats.id,
            generated_at=workout_stats.generated_at.isoformat(),
            user_email=user_email,
            exercises=[
                ExercisePerformedSchema(
                    id=ex.id,
                    name=ex.name,
                    actual_reps=ex.actual_reps,
                    actual_weight=ex.actual_weight,
                    performed_at=ex.performed_at.isoformat()
                ) for ex in exercise_schemas
            ]
        )

    except requests.RequestException as e:
        logger.error(f"Request error while generating stats for {user_email}: {str(e)}")
        db.rollback()
        return None

    except Exception as e:
        logger.error(f"Unexpected error for {user_email}: {str(e)}")
        db.rollback()
        return None

    finally:
        db.close()

def get_stats_by_user(user_email: str) -> List[WorkoutStatsSchema]:
    db = db_session()
    try:
        stats = db.query(WorkoutStats).filter(WorkoutStats.user_email == user_email).all()
        return [
            WorkoutStatsSchema(
                id=w.id,
                generated_at=w.generated_at.isoformat(),
                user_email=w.user_email,
                exercises=[
                    ExercisePerformedSchema(
                        id=e.id,
                        name=e.name,
                        actual_reps=e.actual_reps,
                        actual_weight=e.actual_weight,
                        performed_at=e.performed_at.isoformat()
                    ) for e in w.exercises
                ]
            ) for w in stats
        ]
    finally:
        db.close()