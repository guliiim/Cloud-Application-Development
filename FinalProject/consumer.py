import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='user-registration')

def process_message(ch, method, properties, body):
    print(f"Received message: {body.decode()}")
    print("Notification sent successfully!")

channel.basic_consume(
    queue='user-registration',
    on_message_callback=process_message,
    auto_ack=True
)

print('Waiting for messages...')
channel.start_consuming()
