import os, sys
from demol.definitions import *
from demol.lang import utils
from demol.transformations import m2t_riot_old, device_to_plantuml
import jinja2
import codecs

fsloader = jinja2.FileSystemLoader(SMAUTO_TEMPLATES)
env = jinja2.Environment(loader=fsloader)

def get_info(device_model):
    #Gather Broker info
    broker_type = device_model.broker.__class__.__name__
    # keep only the type name, without the "Broker" suffix
    broker_type = broker_type.replace("Broker", "")
    broker_host = device_model.broker.host
 
    broker_port = device_model.broker.port
    broker_name = device_model.broker.name

    if hasattr(device_model.broker, "auth") and str(device_model.broker.auth.__class__.__name__) == "AuthPlain":
        broker_username = device_model.broker.auth.username
        broker_password = device_model.broker.auth.password
    else:
        warnings.warn(
        "SmAuto currently supports only plain authentication for all brokers.",
        category=UserWarning
        )
        broker_username = None
        broker_password = None
    
    if broker_type == "AMQP" and hasattr(device_model.broker, "vhost"):
        broker_vhost = device_model.broker.vhost
    if broker_type == "AMQP" and hasattr(device_model.broker, "topicExchange"):
        broker_topicExchange = device_model.broker.topicExchange

    if broker_type == "Redis" and hasattr(device_model.broker, "db"):
        broker_db = device_model.broker.db

    print(f"Broker type: {broker_type}")
    print(f"Broker host: {broker_host}")
    print(f"Broker port: {broker_port}")
    print(f"Broker name: {broker_name}")
    print(f"Broker username: {broker_username}")
    print(f"Broker password: {broker_password}")


def main(dev_model):
    rpi5_device_path = os.path.join(REPO_PATH, "examples", dev_model)
    rpi5_device = utils.build_model(rpi5_device_path)
    print("Collecting info...")
    get_info(rpi5_device) 

if __name__ == "__main__":
    main("RPi_gas_led.dev")