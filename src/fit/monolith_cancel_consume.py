import pika
import json
from models_db import UserModel, db_session

def update_premium(data):
    db = db_session()
    try:
        email = data['email']
        db.query(UserModel).filter(UserModel.email == email).update({
            UserModel.premium_status: False,
        })
        db.commit()
        print(f"Updated premium status")
    except Exception as e:
        print(f"DB error: {e}")
        db.rollback()
    finally:
        db.close()

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        update_premium(data)
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
channel.queue_declare(queue='', durable=True)

channel.basic_consume(
    queue='premiumUsersQueue-canceled',
    on_message_callback=callback,
    auto_ack=True
)

print('Waiting...')
channel.start_consuming()