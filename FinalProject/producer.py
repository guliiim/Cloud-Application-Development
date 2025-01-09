import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue acts as a Pub/Sub topic
channel.queue_declare(queue='user-registration')

def publish_message(event_message):
    channel.basic_publish(
        exchange='',
        routing_key='user-registration',
        body=event_message
    )
    print(f"Published message: {event_message}")

user_event = "User John Doe registered"
publish_message(user_event)

connection.close()
