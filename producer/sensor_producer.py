import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime
from faker import Faker
import os
from jsonschema import validate, ValidationError
from schemas.sensor_schema import TEMPERATURE_SENSOR_SCHEMA
import logging
from monitoring.producer_metrics import (
    messages_produced,
    producer_failures,
    messages_produced_per_minute,
    start_producer_metrics_server
)

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
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.message_count = 0
        self.last_minute = time.time()
        self.messages_in_current_minute = 0
        start_producer_metrics_server(8000)

    def validate_sensor_data(self, data):
        """
        Validates sensor data against the schema.

        Args:
            data (dict): The sensor data to validate.

        Returns:
            bool: True if validation succeeds, False otherwise.
        """
        try:
            validate(instance=data, schema=TEMPERATURE_SENSOR_SCHEMA)
            return True
        except ValidationError as e:
            self.logger.error(f"Schema validation error: {e}")
            return False

    def generate_temperature(self):
        """
        Generates a random temperature reading with sensor metadata.

        Returns:
            dict: A dictionary containing sensor data.
        """
        fake = Faker()
        data = {
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
        return data

    def produce_messages(self, duration_seconds):
        """
        Produces sensor data messages to the Kafka topic for a specified duration.

        Args:
            duration_seconds (int): The duration in seconds for which messages will be produced.
        """
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            temperature_data = self.generate_temperature()
            
            try:
                if self.validate_sensor_data(temperature_data):
                    self.producer.send(self.topic, temperature_data)
                    messages_produced.inc()
                    self.message_count += 1
                    self.messages_in_current_minute += 1
                    self.logger.info(f"Sent temperature: {temperature_data}")
                else:
                    producer_failures.inc()
                    self.logger.error(f"Invalid sensor data: {temperature_data}")
            except Exception as e:
                producer_failures.inc()
                self.logger.error(f"Error sending message: {e}")
            
            # Atualiza métricas por minuto
            current_time = time.time()
            if current_time - self.last_minute >= 60:
                messages_produced_per_minute.set(self.messages_in_current_minute)
                self.messages_in_current_minute = 0
                self.last_minute = current_time

            time.sleep(1)

        self.producer.flush()
        self.producer.close()

if __name__ == "__main__":
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'sensores')
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

    producer = SensorProducer(KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS)
    #produz dados fake por 180s para simular o envio de mensagens
    producer.produce_messages(duration_seconds=180)
