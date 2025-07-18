import os, sys
from demol.definitions import *
from demol.lang import utils
from demol.transformations import m2t_riot_old, device_to_plantuml
import jinja2
import codecs

# Collect .hwd models

ToF_path = os.path.join(PERIPHERAL_MODEL_REPO_PATH, "VL53L1X.hwd")
rpi5_path = os.path.join(BOARD_MODEL_REPO_PATH, "rpi_5.hwd")

# collect .dev models
rpi5_device_path = os.path.join(REPO_PATH, "examples", "rpi5_ToF.dev")

# Build the component models

VL53L1X = utils.build_model(ToF_path)
rpi5 = utils.build_model(rpi5_path)

# Build the device model
rpi5_device = utils.build_model(rpi5_device_path)

#Then try to call the function that generates riot 
out_dir = os.path.join(REPO_PATH, "rpi5_out")

fsloader = jinja2.FileSystemLoader(CLASS_TEMPLATES)
env = jinja2.Environment(loader=fsloader)
peripheral_ref_name = {}
peripheral_real_name = {}
peripheral_type = {}
pins = {}
attr = {}
template = []
topic = []
host = ""
port = 0
constraints = {}


def get_info(device_model, component_models, outputDir):
    # device_model is the .dev (parsed file) 
    # component_models is a list of all the board and peripherals used
    device_to_plantuml.device_to_plantuml(device_model)
    board_name = device_model.components.board.name

    global host, port 

    if str(device_model.broker.__class__.__name__) == "MQTTBroker":
        host = device_model.broker.host
        port = device_model.broker.port


    for i in range(len(device_model.connections)):
        peripheral_ref_name[i] = device_model.connections[i].peripheral.name
        peripheral_real_name[peripheral_ref_name[i]] = device_model.connections[i].peripheral.ref.name
        peripheral_type[peripheral_real_name[peripheral_ref_name[i]]] = type(device_model.connections[i].peripheral.ref).__name__
        pins[i] = {}
        for ioConn in device_model.connections[i].ioConns:
            if ioConn.type == 'gpio':
                if ioConn.name == "trigger":
                    pins[i]["trigger"] = ioConn.pinConn.boardPin
                elif ioConn.name == "echo":
                    pins[i]["echo"] = ioConn.pinConn.boardPin
                else:
                    pins[i]["gpio"] = ioConn.pinConn.boardPin
            elif ioConn.type == 'spi':
                pins[i]["mosi"] = ioConn.mosi.boardPin
                pins[i]["miso"] = ioConn.miso.boardPin
                pins[i]["sck"] = ioConn.sck.boardPin.clock
                pins[i]["cs"] = ioConn.cs.boardPin
            elif ioConn.type == 'i2c':
                pins[i]["sda"] = ioConn.sda.boardPin
                pins[i]["scl"] = ioConn.scl.boardPin      
                pins[i]["slaveAddr"] = ioConn.slaveAddr  #or slave_address
            elif ioConn.type == 'uart':
                pins[i]["baudrate"] = ioConn.baudrate
                pins[i]["tx"] = ioConn.tx.boardPin
                pins[i]["rx"] = ioConn.rx.boardPin
            else:
                raise TypeError("Not a valid IO Connection Type")
        
        attr[i] = {}
        for attribute in device_model.connections[i].peripheral.ref.attributes:
            attr[i] = attr[i] | {attribute.name: attribute.default}
        constraints[i] = {}
        for constraint in device_model.connections[i].peripheral.ref.constraints:
            # Here i have to add code to bring all attributes to Hz and m and then create the dictrionary
            if constraint.name == "max_frequency": #Consider Hz the base
                if constraint.unit == "ghz" :
                    constraints[i] = constraints[i] | {constraint.name: constraint.value * 1000000000}
                elif constraint.unit == "mhz" :
                    constraints[i] = constraints[i] | {constraint.name: constraint.value * 1000000}
                elif constraint.unit == "khz" :
                    constraints[i] = constraints[i] | {constraint.name: constraint.value * 1000}
                else:
                    constraints[i] = constraints[i] | {constraint.name: constraint.value}
            else: #Consider cm as the base
                if constraint.unit == "mm" :
                    constraints[i] = constraints[i] | {constraint.name: constraint.value * 10}
                elif constraint.unit == "cm" :
                    constraints[i] = constraints[i] | {constraint.name: constraint.value}
                else:
                    constraints[i] = constraints[i] | {constraint.name: constraint.value / 100}
        print(device_model.connections[i].endpoint.topic)
        topic.append(device_model.connections[i].endpoint.topic)

        
        # Εδώ στα attributes για απλότητα θα μπορούσα να κάνω έλεγχο για κατάληψη ίδιων pins από
        # διαφορετικούς αισθητήρες. Υπενθύμιση ότι στα i2c επιτρέπεται αλλά εκεί πρέπει να γίνει 
        # έλεγχος για ίδια slave_addresses
                   
    #modules = list(peripheral_real_name.values())

#Add try/except to create template if not found
def create_classes():
    i = 0
    for sensor_name, sensor_type in peripheral_real_name.items():
        sensor_attr = {}
        if sensor_type == "SRF05" or sensor_type == "HC_SR04":
            template = env.get_template('DistanceSensor.py.tmpl')
        elif sensor_type == "VL53L1X":
            template = env.get_template('ToFSensor.py.tmpl')
        elif sensor_type == "HW006" or sensor_type == "TCRT5000":
            template = env.get_template('TrackerSensor.py.tmpl')
        elif sensor_type == "BME680":
            template = env.get_template('EnvSensor.py.tmpl')
        elif sensor_type == "TFMini":
            template = env.get_template('TFMiniSensor.py.tmpl')
        else:
            print("Not a prebuilt sensor. Add your template")

        sensor_attr = {"sensor_type": sensor_type}
        sensor_attr = sensor_attr | pins[i]
        sensor_attr = sensor_attr | attr[i]
        sensor_attr = sensor_attr | constraints[i]
                    
        print(sensor_attr)

        rt = template.render(**sensor_attr)
        filepath = os.path.join(out_dir, f"{sensor_name}.py")
        ofh = codecs.open(filepath, "w", encoding="utf-8")
        ofh.write(rt)
        ofh.close()   
        i += 1  

def generate_process():
    '''
    For every sensor there must be a process created by
    using a new template MQTT class.

    There must be a check for weather the frequency is supported by the sensor.

    Add in sensor classes a Constant MAX_FREQUENCY that has a default value that can be overwritten
    '''
    
    i = 0
    for sensor_name, sensor_type in peripheral_real_name.items():
        sensor_attr = {
            "sensor_name": sensor_name,
            "sensor_type": sensor_type,
            "topic": topic[i],
            "host": host,
            "port": port
        } | attr[i]
            
        
        template = env.get_template("MQTTpublisher.py.tmpl")
        rt = template.render(**sensor_attr)
        filepath = os.path.join(out_dir, f"{sensor_name}publisher.py")
        ofh = codecs.open(filepath, "w", encoding="utf-8")
        ofh.write(rt)
        ofh.close()  

        template = env.get_template("MQTTsubscriber.py.tmpl")
        rt = template.render(**sensor_attr)
        filepath = os.path.join(out_dir, f"{sensor_name}subscriber.py")
        ofh = codecs.open(filepath, "w", encoding="utf-8")
        ofh.write(rt)
        ofh.close() 
        
        i += 1  


def main():
    print("Collecting info")
    get_info(rpi5_device, [rpi5,VL53L1X], out_dir) 
    print(pins)
    print(peripheral_ref_name)
    print(peripheral_real_name)
    print(peripheral_type)
    print("Attributes")
    print(attr)
    print("Constarints")
    print(constraints)
    print("Creating classes")
    create_classes()
    print("/n")
    print("Generating processes")
    generate_process()
    print(topic)
    print(host)
    print(port)


if __name__ == "__main__":
    main()