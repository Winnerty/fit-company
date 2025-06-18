import pika
import json
from pymongo import MongoClient
from schemas import WorkoutStatSchema
from queue_messages import WorkoutCreatedMessage

client = MongoClient("mongodb://mongo:27017/")
db = client["fit_company"]
stats_collection = db["workout_stats"]

stat_schema = WorkoutStatSchema()

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        msg = WorkoutCreatedMessage(**data)
        errors = stat_schema.validate(data)
        if errors:
            print(f"Validation errors: {errors}")
            return
        stats_collection.insert_one(msg.data())
        else:
            print(f"Message processed successfully: {msg}")
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