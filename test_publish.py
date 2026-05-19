"""
Test Script - Publish sample data to MQTT broker
Run this to test if the consumer is working correctly
"""
import paho.mqtt.client as mqtt
import json
import time

# MQTT Configuration (same as in mqtt_consumer.py)
BROKER_HOST = "mqtt.dehat.co"
BROKER_PORT = 1883
MQTT_USERNAME = "charan"
MQTT_PASSWORD = "mqtt@2026"
MQTT_TOPIC = "devices/device001/data"


def create_mqtt_client():
    """Create a paho client compatible with both 1.x and 2.x releases."""
    client_kwargs = {}
    if hasattr(mqtt, "CallbackAPIVersion"):
        client_kwargs["callback_api_version"] = mqtt.CallbackAPIVersion.VERSION1

    try:
        return mqtt.Client(**client_kwargs)
    except TypeError:
        return mqtt.Client()

def publish_test_data():
    """Publish sample sensor data"""
    client = create_mqtt_client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    try:
        print(f"Connecting to {BROKER_HOST}:{BROKER_PORT}...")
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        client.loop_start()
        
        # Test data 1 - Temperature and humidity focused
        test_message_1 = {
            "Type": "MR",
            "ID": "2002",
            "DATE": "07/01/00",
            "TIME": "23:56:34",
            "SL_ID": "1",
            "RegAd": "1",
            "Length": "15",
            "D1": "1.09",      # Er
            "D2": "1.12",      # ErTc
            "D3": "45.5",      # Soil Moisture
            "D4": "0.8",       # Ec
            "D5": "26.3",      # Temperature
            "D6": "2.1",       # Ei
            "D7": "0",
            "D8": "0",
            "D9": "0",
            "D10": "0",
            "D11": "0",
            "D12": "0",
            "D13": "0",
            "D14": "0",
            "D15": "1"
        }
        
        print("\n📤 Publishing Test Message 1...")
        client.publish(MQTT_TOPIC, json.dumps(test_message_1))
        print(f"✅ Published: {json.dumps(test_message_1, indent=2)}")
        time.sleep(2)
        
        # Test data 2 - Different values
        test_message_2 = {
            "Type": "MR",
            "ID": "2002",
            "DATE": "07/01/00",
            "TIME": "23:57:34",
            "SL_ID": "1",
            "RegAd": "1",
            "Length": "15",
            "D1": "1.15",
            "D2": "1.18",
            "D3": "48.2",
            "D4": "0.85",
            "D5": "27.1",
            "D6": "2.3",
            "D7": "0",
            "D8": "0",
            "D9": "0",
            "D10": "0",
            "D11": "0",
            "D12": "0",
            "D13": "0",
            "D14": "0",
            "D15": "1"
        }
        
        print("\n📤 Publishing Test Message 2...")
        client.publish(MQTT_TOPIC, json.dumps(test_message_2))
        print(f"✅ Published: {json.dumps(test_message_2, indent=2)}")
        time.sleep(2)
        
        # Test data 3 - Another set
        test_message_3 = {
            "Type": "MR",
            "ID": "2002",
            "DATE": "07/01/00",
            "TIME": "23:58:34",
            "SL_ID": "1",
            "RegAd": "1",
            "Length": "15",
            "D1": "1.11",
            "D2": "1.14",
            "D3": "46.8",
            "D4": "0.82",
            "D5": "25.9",
            "D6": "2.0",
            "D7": "0",
            "D8": "0",
            "D9": "0",
            "D10": "0",
            "D11": "0",
            "D12": "0",
            "D13": "0",
            "D14": "0",
            "D15": "1"
        }
        
        print("\n📤 Publishing Test Message 3...")
        client.publish(MQTT_TOPIC, json.dumps(test_message_3))
        print(f"✅ Published: {json.dumps(test_message_3, indent=2)}")
        
        print("\n✅ All test messages published!")
        print("\nNow:")
        print("1. Check if mqtt_consumer.py shows these messages")
        print("2. Open dashboard at http://localhost:8501")
        print("3. You should see Device 2002 with sensor data")
        
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure:")
        print("  - Broker is accessible")
        print("  - Credentials are correct")
        print("  - Network allows connection")

if __name__ == "__main__":
    publish_test_data()
