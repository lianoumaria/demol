import time

from EntranceSRF import SRF05
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
#from commlib.msg import MessageHeader, PubSubMessage
from MQTTMessages import DistanceMessage 

FREQUENCY = 10.0

def sample(msg):
    global FREQUENCY
    sensor = SRF05()
    if FREQUENCY == 0:
        raise ValueError("Frequency zero is not valid")
    elif FREQUENCY > sensor.get_max_frequency():
        FREQUENCY = sensor.get_max_frequency()
        print(f"Sampling at {FREQUENCY} Hz.")
    period = 1/FREQUENCY
    try:
        while True:
            pub.publish(msg)
            data = sensor.read_data()
            for key,value in data.items():
                key = key.strip('""')
                setattr(msg, key, value)
            time.sleep(period)
    except KeyboardInterrupt:
            sensor.disconnect()
    
if __name__ == "__main__":
    conn_params = ConnectionParameters(host="locsys.issel.ee.auth.gr", port=1883, ssl=False, username="sensors", password="issel.sensors")
    node = Node(node_name='sensors.SRF05', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=DistanceMessage, topic="entranceleds.sensor.distance.entrancesrf")
    node.run()
    msg = DistanceMessage()
    sample(msg = msg)