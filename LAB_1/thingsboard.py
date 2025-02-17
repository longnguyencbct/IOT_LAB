print("Hello Core IOT")
import paho.mqtt.client as mqttclient
import time
import json

BROKER_ADDRESS = "app.coreiot.io"
PORT = 1883
CLIENT_ID = "longnguyencbct_device_1"
ACCESS_USERNAME = "cbct1"
ACCESS_PASSWORD = "qwerty"

def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client(CLIENT_ID)
client.username_pw_set(ACCESS_USERNAME, ACCESS_PASSWORD)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message


#########################################################################################
#                                   Send Data to Broker                                 #         
#########################################################################################

temp = 30
humi = 50
light_intesity = 100

#HCMUT
long=106.65789107082472
lat=10.772175109674038

counter = 0
while True:
    collect_data = {'temperature': temp, 
                    'humidity': humi, 
                    'light':light_intesity,
                    "long":long,
                    "lat":lat}
    temp += 1
    humi += 1
    light_intesity += 1
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(5)