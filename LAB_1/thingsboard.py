import paho.mqtt.client as mqtt
import time
import json
import random

BROKER_ADDRESS = "app.coreiot.io"
PORT = 1883
CLIENT_ID = "iot_simulation_device"
ACCESS_TOKEN = "oW5herDtyc1H6Buc2BCF"  # Replace with your token

# Constants
LED_PIN = 48
BLINKING_INTERVAL_MS_MIN = 10
BLINKING_INTERVAL_MS_MAX = 60000
DEFAULT_BLINKING_INTERVAL = 1000

# Global variables
led_state = False
blinking_interval = DEFAULT_BLINKING_INTERVAL

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to ThingsBoard!")
        client.subscribe("v1/devices/me/rpc/request/+")
        client.subscribe("v1/devices/me/attributes")
    else:
        print("Failed to connect, return code %d\n" % rc)

def on_message(client, userdata, msg):
    global led_state, blinking_interval
    print(f"Received message: {msg.payload.decode('utf-8')} on topic {msg.topic}")
    try:
        payload = json.loads(msg.payload)
        if "method" in payload:
            if payload["method"] == "setLedSwitchValue":
                led_state = payload["params"]
                print(f"LED state set to: {led_state}")
                client.publish("esp/attributes", json.dumps({"ledState": led_state}), 1)
            elif payload["method"] == "setBlinkingInterval":
                new_interval = payload["params"]
                if BLINKING_INTERVAL_MS_MIN <= new_interval <= BLINKING_INTERVAL_MS_MAX:
                    blinking_interval = new_interval
                    print(f"Blinking interval set to: {blinking_interval} ms")
                    client.publish("esp/attributes", json.dumps({"blinkingInterval": blinking_interval}), 1)
    except Exception as e:
        print(f"Error processing message: {e}")

# Initialize MQTT client
client = mqtt.Client(CLIENT_ID)
client.username_pw_set(ACCESS_TOKEN)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_ADDRESS, PORT, 60)
client.loop_start()

def send_telemetry():
    # Only temperature and humidity as telemetry
    temperature = random.uniform(20.0, 30.0)
    humidity = random.uniform(40.0, 60.0)
    telemetry_data = {
        "temperature": temperature,
        "humidity": humidity
    }
    client.publish("esp/telemetry", json.dumps(telemetry_data), 1)
    print(f"\nSent telemetry: {telemetry_data}")

    # Publish other data as attributes
    attribute_data = {
        "rssi": random.randint(-70, -30),
        "channel": random.randint(1, 11),
        "bssid": "00:11:22:33:44:55",
        "localIp": "192.168.1.100",
        "ssid": "Ngaow"
    }
    client.publish("esp/attributes", json.dumps(attribute_data), 1)
    print(f"Sent attributes: {attribute_data}")

# Main loop
try:
    while True:
        send_telemetry()
        time.sleep(blinking_interval / 1000.0)
except KeyboardInterrupt:
    print("Simulation stopped.")
    client.loop_stop()
    client.disconnect()
