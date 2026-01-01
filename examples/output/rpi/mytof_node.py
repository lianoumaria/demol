from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from .msg import DistanceMessage
from .vl53l1x import VL53L1X


if __name__ == "__main__":
    sensor = VL53L1X(attributes={}, conn={'i2c': {'bus': 0, 'slave_address': '0x29', 'pins': {'sda': {'name': 'GPIO2', 'id': 3}, 'scl': {'name': 'GPIO3', 'id': 5}}}})
    sensor.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(node_name='sensors.Distance', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=DistanceMessage, topic="my_raspi.sensors.tof.vl53l1x")
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