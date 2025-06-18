import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq', port=5672, credentials=pika.PlainCredentials('rabbit', 'docker'))
)
channel = connection.channel()
channel.queue_declare(queue='workoutCreatedQueue', durable=True)

connection.close()