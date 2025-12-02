import time

from TempSensor import BME680
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
#from commlib.msg import MessageHeader, PubSubMessage
from MQTTMessages import EnvMessage 

FREQUENCY = 1

def sample(msg):
    global FREQUENCY
    sensor = BME680()
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
    node = Node(node_name='sensors.BME680', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=EnvMessage, topic="smartwindow.sensor.env.tempsensor")
    node.run()
    msg = EnvMessage()
    sample(msg = msg)