import time
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
#from commlib.msg import MessageHeader, PubSubMessage
from MQTTMessages import DistanceMessage

def on_message(msg):
    print(f'Received data: {msg}')

if __name__ == '__main__':
    conn_params = ConnectionParameters(host="locsys.issel.ee.auth.gr", port=1883, ssl=False, username="sensors", password="issel.sensors")

    node = Node(node_name='node.SRF05', connection_params=conn_params, heartbeats=False)

    node.create_subscriber(msg_type=DistanceMessage,
                           topic="parkingsensor.sensor.distance.parkingdistance",
                           on_message=on_message)  # Define a callback function

    node.run_forever(sleep_rate=1)  # Define a process-level sleep rate in hz