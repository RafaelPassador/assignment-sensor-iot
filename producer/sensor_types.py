"""Base classes for different sensor types."""
from abc import ABC, abstractmethod
from datetime import datetime
from faker import Faker

class BaseSensor(ABC):
    """Abstract base class for sensor data generation."""
    
    def __init__(self):
        self.fake = Faker()
    
    def generate_base_data(self):
        """Generate common sensor data."""
        return {
            "sensor_id": self.fake.uuid4(),
            "timestamp": datetime.utcnow().isoformat(),
            "location": {
                "latitude": float(round(self.fake.latitude(), 6)),
                "longitude": float(round(self.fake.longitude(), 6))
            }
        }
    
    @abstractmethod
    def generate_reading(self):
        """Generate sensor-specific reading data."""
        pass

class TemperatureSensor(BaseSensor):
    """Temperature sensor implementation."""
    
    def generate_reading(self):
        """Generate temperature reading data."""
        data = self.generate_base_data()
        data.update({
            "sensor_type": "temperature",
            "reading": {
                "value": round(self.fake.random.uniform(-10, 40), 1),
                "unit": "C"
            }
        })
        return data
