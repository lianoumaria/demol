from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from .msg import DistanceMessage
from .tfmini import TFMini


if __name__ == "__main__":
    sensor = TFMini(attributes={'serial_port': '/dev/ttyAMA0'}, conn={'uart': {'port': 0, 'baudrate': 115200, 'pins': {'tx': {'name': 'GPIO14', 'id': 8}, 'rx': {'name': 'GPIO15', 'id': 10}}}})
    sensor.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(node_name='sensors.Distance', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=DistanceMessage, topic="my_raspi.sensors.tfmini")
    try:
        node.run()
        while True:
            sensor.read()
            pub.send(self.msg)
            self._rate.sleep()
    except KeyboardInterrupt:
        sensor.disconnect()
    except Exception as e:
        print(e)