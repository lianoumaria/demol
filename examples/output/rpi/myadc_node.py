from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from .msg import ADCMessage
from .adcdifferentialpi import ADCDifferentialPi


if __name__ == "__main__":
    sensor = ADCDifferentialPi(attributes={'num_channels': 8, 'resolution': <textx:common.ListValue instance at 0x1aed18def90>, 'gain': <textx:common.ListValue instance at 0x1aed107a490>, 'voltage_reference': 2.048}, conn={'i2c': {'bus': 0, 'slave_address': '0x68', 'pins': {'sda': {'name': 'GPIO2', 'id': 3}, 'scl': {'name': 'GPIO3', 'id': 5}}}})
    sensor.initialize()
    conn_params = ConnectionParameters(host="localhost", port=1883, ssl=False)
    node = Node(node_name='sensors.ADC', connection_params=conn_params, heartbeats=False)
    pub = node.create_publisher(msg_type=ADCMessage, topic="my_raspi.sensors.adc.MyADC")
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