import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime
from faker import Faker
import os

class SensorProducer:
    """
    A class responsible for producing sensor data messages to a Kafka topic.

    Attributes:
        topic (str): The Kafka topic to which messages will be sent.
        bootstrap_servers (str): The Kafka server address.
        producer (KafkaProducer): The Kafka producer instance.
    """

    def __init__(self, topic, bootstrap_servers):
        """
        Initializes the SensorProducer with the specified topic and Kafka server.

        Args:
            topic (str): The Kafka topic to which messages will be sent.
            bootstrap_servers (str): The Kafka server address.
        """
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def generate_temperature(self):
        """
        Generates a random temperature reading with sensor metadata.

        Returns:
            dict: A dictionary containing sensor data.
        """
        fake = Faker()
        return {
            "sensor_type": "temperature",
            "sensor_id": fake.uuid4(),
            "timestamp": datetime.utcnow().isoformat(),
            "reading": {
                "value": round(random.uniform(-10, 40), 1),
                "unit": "C"
            },
            "location": {
                "latitude": float(round(fake.latitude(), 6)),
                "longitude": float(round(fake.longitude(), 6))
            }
        }

    def produce_messages(self, duration_seconds):
        """
        Produces sensor data messages to the Kafka topic for a specified duration.

        Args:
            duration_seconds (int): The duration in seconds for which messages will be produced.
        """
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            temperature_data = self.generate_temperature()
            self.producer.send(self.topic, temperature_data)
            print("Sent temperature:", temperature_data)
            time.sleep(1)

        self.producer.flush()
        self.producer.close()

if __name__ == "__main__":
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'sensores')
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

    producer = SensorProducer(KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS)
    producer.produce_messages(duration_seconds=180)
