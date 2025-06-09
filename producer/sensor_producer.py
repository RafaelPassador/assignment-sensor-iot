import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime
from faker import Faker

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

fake = Faker()

def generate_temperature():
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

start_time = time.time()
while time.time() - start_time < 180:  # Run for 3 minutes
    temperature_data = generate_temperature()

    producer.send("sensores", temperature_data)
    print("Sent temperature:", temperature_data)

    time.sleep(1)
producer.flush()
producer.close()
