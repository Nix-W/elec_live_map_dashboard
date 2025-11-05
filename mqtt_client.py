import json
import threading
import paho.mqtt.client as mqtt
import random

latest_points = []
# Flag to prevent multiple background loops
_background_started = False 

BROKER = "broker.emqx.io"
TOPIC = "Tutor21Group07/facility"
PORT = 1883

client_id = f'dash-subscriber-{random.randint(0, 1000)}'

def connect_mqtt() -> mqtt.Client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_disconnect(client, userdata, rc):
        print(f"Disconnected from MQTT Broker with code {rc}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    print(f"Attempting to connect to {BROKER}:{PORT} with client ID: {client_id}")
    client.connect(BROKER, PORT)
    return client

def subscribe(client: mqtt.Client):
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            latest_points.append(payload)
            print(f"Added point to list. Total points: {len(latest_points)}")
            if len(latest_points) > 200:  # limit memory
                latest_points.pop(0)
        except Exception as e:
            print(f"Error parsing MQTT message: {e}")

    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"Subscribed to topic '{TOPIC}' with QoS {granted_qos}")

    print(f"Subscribing to topic: {TOPIC}")
    client.subscribe(TOPIC)
    client.on_message = on_message
    client.on_subscribe = on_subscribe

def run_mqtt():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

def start_background_loop():
    global _background_started
    if _background_started:
        print("MQTT background loop already started, skipping...")
        return

    print("Starting MQTT background loop...")
    t = threading.Thread(target=run_mqtt, daemon=True)
    t.start()
    _background_started = True
    print("MQTT background thread started")
