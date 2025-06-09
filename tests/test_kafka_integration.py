import json
import os
import time
import uuid
import pytest
import logging
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaTimeoutError
from kafka.admin import KafkaAdminClient, NewTopic

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
TOPIC = "test-topic"
TEST_DATA = {"message": "integration-test"}

def wait_for_kafka(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            prod = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
            prod.close()
            return
        except NoBrokersAvailable:
            time.sleep(1)
    pytest.skip(f"Kafka not available at {KAFKA_BOOTSTRAP_SERVERS} after {timeout}s")

def create_kafka_topic():
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    topic = NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)
    try:
        admin.create_topics(new_topics=[topic], validate_only=False)
    except Exception:
        # Topic already exists
        pass
    finally:
        admin.close()

def validate_topic_creation():
    admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    topics = admin.list_topics()
    assert TOPIC in topics, f"Topic {TOPIC} was not created correctly"
    admin.close()

@pytest.mark.integration
def test_kafka_produce_consume():
    wait_for_kafka()
    create_kafka_topic()
    validate_topic_creation()

    logging.info("Producing message to the topic...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(TOPIC, TEST_DATA)
    producer.flush()
    logging.info("Message successfully produced.")

    # Consumer with unique group id
    logging.info("Configuring consumer...")
    group_id = f"test-group-{uuid.uuid4()}"
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        consumer_timeout_ms=10000,  # Timeout adjusted dynamically
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    # Ensure partition assignment
    logging.info("Checking partition assignment...")
    timeout = time.time() + 15  # Timeout adjusted
    while not consumer.assignment():
        if time.time() > timeout:
            pytest.fail("Partitions not assigned after 15s.")
        consumer.poll(timeout_ms=500)

    # Seek to beginning
    consumer.seek_to_beginning()
    logging.info("Partitions assigned and consumer positioned at the beginning.")

    # Consume
    logging.info("Consuming messages...")
    received = False
    end_time = time.time() + 10  # Timeout adjusted
    while time.time() < end_time:
        records = consumer.poll(timeout_ms=500)
        for msgs in records.values():
            for msg in msgs:
                logging.info(f"Message received: {msg.value}")
                if msg.value == TEST_DATA:
                    received = True
                    break
            if received:
                break
        if received:
            break

    consumer.close()
    assert received, "Message was not consumed correctly"
