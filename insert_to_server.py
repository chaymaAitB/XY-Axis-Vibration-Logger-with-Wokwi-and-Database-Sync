from supabase import create_client, Client
import paho.mqtt.client as mqtt
import json

# MQTT Settings
MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "wokwi/sensor_data"

# Supabase Settings
SUPABASE_URL = "TO_ADD"
SUPABASE_KEY = "TO_ADD"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def insert_sensor_data(load_value, speed_set, vibration_x, vibration_y, machine_id, is_active):
    data = {
        "load_value": load_value,
        "speed_set": speed_set,
        "vibration_x": vibration_x,
        "vibration_y": vibration_y,
        "machine_id": machine_id,
        "is_active": is_active
    }
    
    response = supabase.from_("sensor_data").insert(data).execute()
    print(f"✅ Data inserted into Supabase: {response}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    if reason_code == 0:
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed: {reason_code}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"📩 Received MQTT message: {payload}")
        
        # Parse the outer JSON
        payload_data = json.loads(payload)
        data = payload_data.get("data", {})

        # Extract values
        load_value = data.get("load_value", 0)
        speed_set = data.get("speed_set", 0)
        vibration_x = data.get("vibration_x", 0)
        vibration_y = data.get("vibration_y", 0)
        machine_id = data.get("machine_id", 1)
        is_active = data.get("is_active", 1)

        # Insert into Supabase
        insert_sensor_data(
            load_value=load_value,
            speed_set=speed_set,
            vibration_x=vibration_x,
            vibration_y=vibration_y,
            machine_id=machine_id,
            is_active=is_active
        )

    except json.JSONDecodeError:
        print("❌ Error: Received message is not valid JSON")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

# Initialize MQTT client (with version 2 callbacks)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, 1883)
    print(f"🚀 Connected to MQTT broker at {MQTT_BROKER}, subscribing to topic '{MQTT_TOPIC}'")
    client.loop_forever()
except Exception as e:
    print(f"❌ Connection error: {e}")
