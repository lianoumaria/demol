import time
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from MQTTMessages import LedArrayMessage
from MyLedRing import WS2812

def on_message(msg):
    try:
        # Create parameters dictionary from the message
        attr_names = list(LedArrayMessage.__annotations__.keys())
        attr_names = [name for name in attr_names if name != "header"]

        params = {}
        for name in attr_names:
            params[name] = getattr(msg, name)

        # Control the LED array using **params unpacking
        actuator.set_action(**params)

    except Exception as e:
        print(f"Error controlling actuator: {e}")

if __name__ == '__main__':
    actuator = WS2812()
    try:
        conn_params = ConnectionParameters(host="localhost", port=1883)

        node = Node(node_name='actuators.WS2812', connection_params=conn_params, heartbeats=False)

        node.create_subscriber(msg_type=LedArrayMessage,
                               topic="my_raspi.actuator.ledarray.myledring",
                               on_message=on_message)  # Define a callback function
  
        node.run_forever(sleep_rate=1)  # Define a process-level sleep rate in hz
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal. Shutting down...")