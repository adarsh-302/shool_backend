"""
MQTT Consumer - Reads from broker and stores in SQLite
"""
import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BROKER_HOST = "mqtt.dehat.co"
BROKER_PORT = 1883
MQTT_USERNAME = "charan"
MQTT_PASSWORD = "mqtt@2026"
MQTT_TOPIC = "devices/device001/data"  # Subscribe to this topic
DB_FILE = "sensor_data.db"


def create_mqtt_client():
    """Create a paho client compatible with both 1.x and 2.x releases."""
    client_kwargs = {}
    if hasattr(mqtt, "CallbackAPIVersion"):
        client_kwargs["callback_api_version"] = mqtt.CallbackAPIVersion.VERSION1

    try:
        return mqtt.Client(**client_kwargs)
    except TypeError:
        return mqtt.Client()

# Initialize SQLite database
def init_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                device_id TEXT NOT NULL,
                device_type TEXT,
                sensor_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                date_field TEXT,
                time_field TEXT
            )
        ''')
    logger.info(f"Database initialized: {DB_FILE}")

# Insert data into database
def insert_reading(device_id, device_type, sensor_name, value, unit="", date_field="", time_field=""):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO readings (device_id, device_type, sensor_name, value, unit, date_field, time_field) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (device_id, device_type, sensor_name, value, unit, date_field, time_field)
        )
    logger.info(f"Inserted: Device={device_id}, {sensor_name}={value}{unit}")

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to: {MQTT_TOPIC}")
    else:
        logger.error(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8", errors="replace")
        logger.info(f"Message received on {msg.topic}: {payload}")
        
        # Parse JSON payload
        data = json.loads(payload)
        
        # Extract metadata
        device_id = data.get("ID", "unknown")
        device_type = data.get("Type", "MR")
        date_field = data.get("DATE", "")
        time_field = data.get("TIME", "")
        
        # Map your data points to readable sensor names
        # Based on your mapping: D1=Er, D2=ErTc, D3=Soil moisture, D4=Ec, D5=Temp, D6=Ei
        sensor_mapping = {
            "D1": {"name": "Er", "unit": ""},
            "D2": {"name": "ErTc", "unit": ""},
            "D3": {"name": "Soil_Moisture", "unit": "%"},
            "D4": {"name": "Ec", "unit": "dS/m"},
            "D5": {"name": "Temperature", "unit": "°C"},
            "D6": {"name": "Ei", "unit": ""},
            "D7": {"name": "D7", "unit": ""},
            "D8": {"name": "D8", "unit": ""},
            "D9": {"name": "D9", "unit": ""},
            "D10": {"name": "D10", "unit": ""},
            "D11": {"name": "D11", "unit": ""},
            "D12": {"name": "D12", "unit": ""},
            "D13": {"name": "D13", "unit": ""},
            "D14": {"name": "D14", "unit": ""},
            "D15": {"name": "D15", "unit": ""},
        }
        
        # Extract and insert each sensor reading
        for key in range(1, 16):
            data_key = f"D{key}"
            if data_key in data:
                try:
                    value = float(data[data_key])
                    sensor_info = sensor_mapping.get(data_key, {})
                    sensor_name = sensor_info.get("name", data_key)
                    unit = sensor_info.get("unit", "")
                    
                    insert_reading(device_id, device_type, sensor_name, value, unit, date_field, time_field)
                except ValueError:
                    logger.warning(f"Could not convert {data_key}={data[data_key]} to float")
    
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON payload: {payload}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning(f"Unexpected disconnection: {rc}")
    else:
        logger.info("Disconnected from broker")

# Main MQTT client setup
def start_mqtt_consumer():
    client = create_mqtt_client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Add authentication
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    logger.info(f"Connecting to {BROKER_HOST}:{BROKER_PORT}")
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        client.loop_forever()  # Blocking call
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        logger.info("Make sure your MQTT broker is running!")

if __name__ == "__main__":
    init_database()
    start_mqtt_consumer()
