import random
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta, timezone
import os
import signal
import sys

# Constants
VOLTAGE_NOMINAL = 400  # Volts (typical inverter output)
CURRENT_MAX = 250  # Amps
POWER_MAX = VOLTAGE_NOMINAL * CURRENT_MAX  # Watts
IMPORT_MAX = 10  # kWh (small import during night maybe)
EXPORT_MAX = 1000  # kWh (large export during day)

# MQTT Configuration (use environment variables for Docker compatibility)
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "solar")
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", 5))
RUNNING = True

# Define timezone offset for +7
TIMEZONE_OFFSET = timedelta(hours=7)
TZ = timezone(TIMEZONE_OFFSET)

def simulate_solar_data(timestamp):
    hour = timestamp.hour
    
    # Simulate sun intensity by hour (simple bell curve)
    if 6 <= hour <= 18:
        sun_factor = max(0, 1 - abs(12 - hour) / 6)
    else:
        sun_factor = 0

    voltage = round(random.uniform(380, 410), 2)  # Voltage slightly fluctuates
    current = round(sun_factor * random.uniform(0.7, 1.0) * CURRENT_MAX, 2)
    power = round(voltage * current / 1000, 2)  # Power in kW

    return { "voltage": voltage, "current": current, "power": power }

def simulate_power_line_data(timestamp):
    hour = timestamp.hour
    
    # Simulate demand factor depending on time (simplified daily load profile)
    if 0 <= hour < 6:
        demand_factor = 0.3  # low usage at night
    elif 6 <= hour < 10:
        demand_factor = 0.8  # morning peak
    elif 10 <= hour < 17:
        demand_factor = 0.5  # daytime moderate usage
    elif 17 <= hour < 22:
        demand_factor = 1.0  # evening peak
    else:
        demand_factor = 0.4  # late night

    voltage = round(random.uniform(220, 240), 2)  # typical single-phase household voltage
    current = round(demand_factor * random.uniform(0.5, 1.0) * 50, 2)  # assume max 50A household
    power = round(voltage * current / 1000, 2)  # Power in kW

    return {"voltage": voltage, "current": current, "power": power}

def publish_to_mqtt(client, data):
    payload = json.dumps(data)
    client.publish(MQTT_TOPIC, payload)

def stop_gracefully(signum, frame):
    global RUNNING
    RUNNING = False

# Register signal handlers for Docker stop
signal.signal(signal.SIGTERM, stop_gracefully)
signal.signal(signal.SIGINT, stop_gracefully)

# Setup MQTT Client
client = mqtt.Client()
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}, publishing to topic '{MQTT_TOPIC}'")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    sys.exit(1)

# Simulate continuous data publishing
while RUNNING:
    timestamp = datetime.now(TZ)
    data = { "solar": simulate_solar_data(timestamp), "grid": simulate_power_line_data(timestamp) }
    publish_to_mqtt(client, data)
    print(f"Published: {data} at {timestamp.isoformat()}")
    time.sleep(PUBLISH_INTERVAL)

client.loop_stop()
client.disconnect()
print("Simulation stopped.")
