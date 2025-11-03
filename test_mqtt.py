import json
import time
import random
import pandas as pd
from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT Configuration
BROKER = "test.mosquitto.org"
TOPIC = "geo/live"
PORT = 1883

def publish_csv_data(csv_file):
    print(f"Reading data from {csv_file}...")
    
    df = pd.read_csv(csv_file)

    # Take only first 100 rows for testing to avoid overwhelming the system
    # test_df = df.head(100)

    print(f"Publishing {len(df)} test messages...")
    
    for index, row in df.iterrows():
        is_operating = row.get("is_operating", 1)
        if is_operating == 0:
            print(f"Skipping facility {row['facility']} as it is not operating.")
            continue

        timestamp = pd.to_datetime(row["timestamp"], utc=True, errors="coerce")
        if pd.isna(timestamp):
            print(f"Skipping facility {row['facility_name']} due to invalid timestamp: {row['timestamp']}")
            continue

        power_mw = row.get("power_mw", 0) if not pd.isna(row.get("power_mw")) else 0
        emissions_t = row.get("emissions_t", 0) if not pd.isna(row.get("emissions_t")) else 0

        if power_mw != 0 or emissions_t != 0:
            test_message = {
                "timestamp": timestamp.isoformat(),
                "facility_code": str(row["facility_code"]),
                "facility_name": str(row["facility_name"]),
                "network_id": str(row["network_id"]),
                "network_region": str(row["network_region"]),
                "unit_code": str(row["unit_code"]),
                "fuel_tech": str(row["fuel_tech"]),
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
                "power_mw": float(power_mw),
                "emissions_t": float(emissions_t),
                "price": float(row["price"]),
                "demand": float(row["demand"]),
            }
            
            payload = json.dumps(test_message)
            mqtt_client.publish(TOPIC, payload)
            print(f"Published message {index + 1}: {row['facility_name']} at {test_message['timestamp']}")
            # Delay between messages
            time.sleep(2)


if __name__ == "__main__":
    client_id = f'test-publisher-{random.randint(0, 1000)}'
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()

    csv_file = "data/NEM_facilities_sorted.csv"
    publish_csv_data(csv_file)

    time.sleep(5)  # Give time for messages to send
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("Test complete! Published CSV data.")
