from kafka import KafkaConsumer
import json
from writer.data_writer import DataWriter
import logging
import os
import signal
import sys

logging.basicConfig(level=logging.INFO)

#environment variables
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'sensores')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'sensor-group')

shutdown_flag = False

def handle_shutdown_signal(signum, frame):
    global shutdown_flag
    logging.info("Shutdown signal received. Closing consumer...")
    shutdown_flag = True

#signal handlers
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    group_id=KAFKA_GROUP_ID,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

writer = DataWriter()

def handle_lost_message(message):
    """Handle lost Kafka messages by logging or storing them in a dead-letter queue."""
    try:
        logging.error(f"Lost message: {message}")

        with open("lost_messages.log", "a") as f:
            f.write(json.dumps(message) + "\n")
    except Exception as e:
        logging.error(f"Failed to handle lost message: {e}")

try:
    for message in consumer:
        if shutdown_flag:
            break

        if not message or not message.value:
            logging.warning("Received empty or invalid Kafka message, skipping.")
            continue

        try:
            writer.process(message.value)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            handle_lost_message(message.value)
except Exception as e:
    logging.error(f"Unexpected error in consumer: {e}")
finally:
    consumer.close()
    logging.info("Kafka consumer closed.")