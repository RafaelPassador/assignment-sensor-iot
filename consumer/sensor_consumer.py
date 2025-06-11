from kafka import KafkaConsumer
import json
from writer.data_writer import DataWriter
import logging
import os
import signal
import sys
from jsonschema import validate, ValidationError
from schemas.sensor_schema import TEMPERATURE_SENSOR_SCHEMA

class SensorConsumer:
    """
    A class responsible for consuming sensor data messages from a Kafka topic.

    Attributes:
        topic (str): The Kafka topic to consume messages from.
        bootstrap_servers (str): The Kafka server address.
        group_id (str): The consumer group ID.
        writer (DataWriter): The instance responsible for writing data to the database.
        shutdown_flag (bool): Flag to indicate when the consumer should stop.
        consumer (KafkaConsumer): The Kafka consumer instance.
    """

    def __init__(self, topic, bootstrap_servers, group_id, writer):
        """
        Initializes the SensorConsumer with the specified topic, Kafka server, group ID, and writer.

        Args:
            topic (str): The Kafka topic to consume messages from.
            bootstrap_servers (str): The Kafka server address.
            group_id (str): The consumer group ID.
            writer (DataWriter): The instance responsible for writing data to the database.
        """
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.writer = writer
        self.shutdown_flag = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

    def validate_message(self, message):
        """
        Validates the message against the sensor schema.

        Args:
            message (dict): The message to validate.

        Returns:
            bool: True if validation succeeds, False otherwise.
        """
        try:
            validate(instance=message, schema=TEMPERATURE_SENSOR_SCHEMA)
            return True
        except ValidationError as e:
            self.logger.error(f"Schema validation error: {e}")
            return False

    def handle_shutdown_signal(self, signum, frame):
        """
        Handles shutdown signals to gracefully stop the consumer.

        Args:
            signum (int): The signal number.
            frame (FrameType): The current stack frame.
        """
        self.logger.info("Shutdown signal received. Closing consumer...")
        self.shutdown_flag = True

    def handle_lost_message(self, message, error=None):
        """
        Handles lost or invalid Kafka messages by logging them.

        Args:
            message (dict): The lost or invalid message.
            error (str, optional): The error message if any. Defaults to None.
        """
        try:
            error_msg = f"Lost/invalid message: {message}"
            if error:
                error_msg += f" Error: {error}"
            self.logger.error(error_msg)
            with open("lost_messages.log", "a") as f:
                f.write(json.dumps({"message": message, "error": str(error)}) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to handle lost message: {e}")

    def consume_messages(self):
        """
        Consumes messages from the Kafka topic and processes them using the writer.
        """
        try:
            for message in self.consumer:
                if self.shutdown_flag:
                    break

                if not message or not message.value:
                    self.logger.warning("Received empty or invalid Kafka message, skipping.")
                    continue

                try:
                    if self.validate_message(message.value):
                        self.writer.process(message.value)
                    else:
                        self.handle_lost_message(message.value, "Schema validation failed")
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    self.handle_lost_message(message.value, str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error in consumer: {e}")
        finally:
            self.consumer.close()
            self.logger.info("Kafka consumer closed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'sensores')
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'sensor-group')

    writer = DataWriter()
    consumer = SensorConsumer(KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID, writer)

    signal.signal(signal.SIGINT, consumer.handle_shutdown_signal)
    signal.signal(signal.SIGTERM, consumer.handle_shutdown_signal)

    consumer.consume_messages()