import time
import sys
from commlib.node import Node
from commlib.transports.mqtt import ConnectionParameters
from MQTTMessages import ServoControllerMessage
import ast

if __name__ == "__main__":
    attr_values = {}

    # If new message values are given, update the message
    if len(sys.argv) > 1:
        
        # Process each argument
        for i, arg in enumerate(sys.argv[1:], 1):
            print(f"  Argument {i}: {arg}")

            # get attribute names
            attr_names = list(ServoControllerMessage.__annotations__.keys())
            # filter out "header"
            attr_names = [name for name in attr_names if name != "header"]
            # build the CLI-style strings
            cli_args = [f"--{name}=" for name in attr_names]
            
            attr_i = 0
            for cli_arg, attr_name in zip(cli_args, attr_names):
                if arg.startswith(cli_arg):
                    raw_val = arg.split('=')[1]
                    expected_type = ServoControllerMessage.__annotations__[attr_name]

                    try:
                        # Try to parse as a Python literal first
                        parsed_val = ast.literal_eval(raw_val)
                    except Exception:
                        parsed_val = raw_val  # fallback to string

                    # Try casting if necessary
                    try:
                        attr_values[attr_name] = expected_type(parsed_val)
                    except Exception:
                        attr_values[attr_name] = parsed_val

    print(attr_values)
    conn_params = ConnectionParameters(host="locsys.issel.ee.auth.gr", port=8883)
    node = Node(node_name='actuators.PCA9685', connection_params=conn_params)
    pub = node.create_publisher(msg_type=ServoControllerMessage, topic="rpifan.actuator.servocontroller.fancontroller")
    node.run()
    msg = ServoControllerMessage()

    try:
        while True:
            for key,value in attr_values.items():
                msg.__setattr__(key, value)
            pub.publish(msg)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping publisher...")
        node.stop()
