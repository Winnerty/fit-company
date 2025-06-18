import pika
import json
from datetime import datetime
from models_db import LastWorkoutModel, db_session
from queue_messages import WorkoutCreatedMessage

def save_last_workout(data):
    db = db_session()
    try:
        last_workout = LastWorkoutModel(
            user_id=data["user_id"],
            date=datetime.fromisoformat(data["date"]),
            workout_type=data["workout_type"],
            exercises=data["exercises"]
        )
        db.add(last_workout)
        db.commit()
        print(f"Saved last workout for {data['user_id']}")
    except Exception as e:
        print(f"DB error: {e}")
        db.rollback()
    finally:
        db.close()

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        msg = WorkoutCreatedMessage(**data)
        save_last_workout(data)
    except Exception as e:
        print(f"Error processing message: {e}")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq',
        port=5672,
        credentials=pika.PlainCredentials('rabbit', 'docker')
    )
)
channel = connection.channel()
channel.queue_declare(queue='workoutCreatedQueue', durable=True)

channel.basic_consume(
    queue='workoutCreatedQueue',
    on_message_callback=callback,
    auto_ack=True
)

print('Waiting...')
channel.start_consuming()