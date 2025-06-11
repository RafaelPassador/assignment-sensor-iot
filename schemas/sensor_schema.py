"""Schema definitions for sensor data validation."""

# Base schema for all sensor types
BASE_SENSOR_SCHEMA = {
    "type": "object",
    "properties": {
        "sensor_type": {"type": "string"},
        "sensor_id": {"type": "string", "format": "uuid"},
        "timestamp": {"type": "string", "format": "date-time"},
        "location": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "minimum": -90, "maximum": 90},
                "longitude": {"type": "number", "minimum": -180, "maximum": 180}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        }
    },
    "required": ["sensor_type", "sensor_id", "timestamp", "location"],
    "additionalProperties": False
}

# Schema specific to temperature sensors
TEMPERATURE_SENSOR_SCHEMA = {
    **BASE_SENSOR_SCHEMA,
    "properties": {
        **BASE_SENSOR_SCHEMA["properties"],
        "sensor_type": {"type": "string", "enum": ["temperature"]},
        "reading": {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "unit": {"type": "string", "enum": ["C"]}
            },
            "required": ["value", "unit"],
            "additionalProperties": False
        },
        "location": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "minimum": -90, "maximum": 90},
                "longitude": {"type": "number", "minimum": -180, "maximum": 180}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        }
    },
    "required": ["sensor_type", "sensor_id", "timestamp", "reading", "location"],
    "additionalProperties": False
}
