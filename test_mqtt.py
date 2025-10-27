import json
import time
import random
import pandas as pd
from datetime import datetime, timezone, timedelta
import paho.mqtt.client as mqtt

# MQTT Configuration
BROKER = "test.mosquitto.org"
TOPIC = "geo/live"
PORT = 1883

client_id = f'test-publisher-{random.randint(0, 1000)}'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

def publish_csv_data():
    csv_file = "data/example.csv"
    print(f"Reading data from {csv_file}...")
    
    df = pd.read_csv(csv_file)
    
    # Take only first 10 rows for testing to avoid overwhelming the system
    test_df = df.head(10)

    print(f"Publishing {len(test_df)} test messages...")
    
    for index, row in test_df.iterrows():
        # Create message with current timestamp (so it appears as "new" data)
        current_time = datetime.now(timezone.utc)
        # Add a few seconds offset for each message to simulate real-time streaming
        offset_time = current_time + timedelta(seconds=index)
        
        test_message = {
            "timestamp": offset_time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            "facility": str(row["facility"]),
            "lat": float(row["lat"]),
            "lng": float(row["lng"]),
            "emissions_t": float(row["emissions_t"]),
            "power_mw": float(row["power_mw"]),
            "region_id": str(row["region_id"]),
            "region_code": str(row["region_code"]),
            "demand_mw": float(row["demand_mw"]),
            "price_aud": float(row["price_aud"])
        }
        
        payload = json.dumps(test_message)
        mqtt_client.publish(TOPIC, payload)
        print(f"📡 Published message {index + 1}: {row['facility']} at {test_message['timestamp']}")
        # Small delay between messages
        time.sleep(0.5)

publish_csv_data()

time.sleep(1)  # Give time for messages to send
mqtt_client.loop_stop()
mqtt_client.disconnect()
print("✅ Test complete! Published CSV data with current timestamps.")
