import time
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
#from commlib.msg import MessageHeader, PubSubMessage
from MQTTMessages import TrackerMessage

def on_message(msg):
    print(f'Received data: {msg}')

if __name__ == '__main__':
    conn_params = ConnectionParameters(host="node.mqtt.local", port=1883, ssl=False, username="sensors", password="sensors")

    node = Node(node_name='node.TCRT5000', connection_params=conn_params, heartbeats=False)

    node.create_subscriber(msg_type=TrackerMessage,
                           topic="my_raspi.sensors.tracker.TCRT5000",
                           on_message=on_message)  # Define a callback function

    node.run_forever(sleep_rate=1)  # Define a process-level sleep rate in hz