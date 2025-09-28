import os, sys
from demol.definitions import *
from demol.lang import utils
from demol.transformations import m2t_riot_old, device_to_plantuml
import jinja2
import codecs
import warnings

fsloader = jinja2.FileSystemLoader(CLASS_TEMPLATES)
env = jinja2.Environment(loader=fsloader)
peripheral_ref_name = {} #Name given in the .dev file
peripheral_real_name = {} #actual name/type of the peripheral
peripheral_type = {} 
pins = {}
attr = {}
template = []
topic = []
host = ""
port = 0
ssl = False
username = ""
password = ""
constraints = {}
peripheralMsg = []

def convert_DictAttribute_to_dict(attribute):
    temp_dict = {}
    for item in attribute.items:
        if (item.__class__.__name__ == "DictAttribute") | (item.__class__.__name__ == "DictSetting"):
            temp_dict[item.name] = convert_DictAttribute_to_dict(item)
        else:
            temp_dict[item.name] = item.default
    return temp_dict

def get_info(device_model):
    # device_model is the .dev (parsed file) 
    # component_models is a list of all the board and peripherals used
    #device_to_plantuml.device_to_plantuml(device_model)
    board_name = device_model.components.board.name

    global host, port, ssl, username, password

    if str(device_model.broker.__class__.__name__) == "MQTTBroker":
        host = device_model.broker.host
        port = device_model.broker.port
        if hasattr(device_model.broker, 'ssl'):
            ssl = device_model.broker.ssl
        #Check if it is the supported auth method for commlib-py
        if device_model.broker.auth.__class__.__name__ == "AuthPlain":
            if hasattr(device_model.broker.auth, 'username'):
                username = device_model.broker.auth.username
            if hasattr(device_model.broker.auth, 'password'):
                password = device_model.broker.auth.password
        #Raise type error if not supported
        elif device_model.broker.auth.__class__.__name__ == "AuthCert" or device_model.broker.auth.__class__.__name__ == "AuthApiKey":
            raise TypeError("This transformation uses commlib-py library and only supports plain authentication for MQTTBroker.")
        #Prompt user to add username and password if not given and remote broker is used
        else:
            if (host != "localhost") and ((not hasattr(device_model.broker.auth, 'username')) or (not hasattr(device_model.broker.auth, 'password'))):
                warnings.warn("You are using a remote broker without authentication. This is not secure. Add username and password to your .dev file.")

    else:
        raise TypeError("This transformation does not support other Broker types than MQTTBroker.")


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
            if attribute.__class__.__name__ == "DictAttribute":
                temp_dict = convert_DictAttribute_to_dict(attribute)
                '''temp_dict = {}
                for item in attribute.items:
                    temp_dict[item.name] = item.default'''
                attr[i] = attr[i] | {attribute.name: temp_dict}
            else:
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
        peripheralMsg.append(device_model.connections[i].peripheral.ref.msg)

        for setting in device_model.connections[i].settings:
            if setting.__class__.__name__ == "DictSetting":
                temp_setting_value = convert_DictAttribute_to_dict(setting)
                if setting.name in attr[i].keys():
                    attr[i][setting.name] = temp_setting_value
                else:
                    attr[i] = attr[i] | {setting.name: temp_setting_value}
            else:
                if setting.name in attr[i].keys():
                    attr[i][setting.name] = setting.default
                else:
                    attr[i] = attr[i] | {setting.name: setting.default}
                 

# This method produces both actuator and sensor classes  from corresponding templates
def create_classes(out_dir):
    i = 0
    for per_name, per_type in peripheral_real_name.items():
        peripheral_attr = {}
        if per_type == "SRF05" or per_type == "HC_SR04":
            template = env.get_template('DistanceSensor.py.tmpl')
        elif per_type == "VL53L1X":
            template = env.get_template('ToFSensor.py.tmpl')
        elif per_type == "HW006" or per_type == "TCRT5000":
            template = env.get_template('TrackerSensor.py.tmpl')
        elif per_type == "BME680":
            template = env.get_template('EnvSensor.py.tmpl')
        elif per_type == "TFMini":
            template = env.get_template('TFMiniSensor.py.tmpl')
        elif per_type == "ADCDifferentialPi":
            template = env.get_template('ADCDifferentialPi.py.tmpl')
        elif per_type == "WS2812":
            template = env.get_template('WS2812.py.tmpl')
        elif per_type == "PCA9685":
            template = env.get_template('PCA9685.py.tmpl')
        else:
            print("Not a prebuilt sensor or actuator. Add your template")

        if peripheral_type[per_type] == "Sensor":
            peripheral_attr = {"sensor_type": per_type}
        else:
            peripheral_attr = {"actuator_type": per_type}
        peripheral_attr = peripheral_attr | pins[i]
        peripheral_attr = peripheral_attr | attr[i]
        peripheral_attr = peripheral_attr | constraints[i]

        print(peripheral_attr)

        rt = template.render(**peripheral_attr)
        filepath = os.path.join(out_dir, f"{per_name}.py")
        ofh = codecs.open(filepath, "w", encoding="utf-8")
        ofh.write(rt)
        ofh.close()   
        i += 1  

def generate_process(out_dir):
    
    i = 0
    for per_name, per_type in peripheral_real_name.items():
        if peripheral_type[per_type] == "Sensor":
            sensor_attr = {
                "sensor_name": per_name,
                "sensor_type": per_type,
                "sensorMsg": peripheralMsg[i],
                "topic": topic[i],
                "host": host,
                "port": port,
                "ssl": ssl,
                "username": username,
                "password": password
            } | attr[i]
                  
            template = env.get_template("MQTTSensorPublisher.py.tmpl")
            rt = template.render(**sensor_attr)
            filepath = os.path.join(out_dir, f"{per_name}publisher.py")
            ofh = codecs.open(filepath, "w", encoding="utf-8")
            ofh.write(rt)
            ofh.close()  

            template = env.get_template("MQTTSensorSubscriber.py.tmpl")
            rt = template.render(**sensor_attr)
            filepath = os.path.join(out_dir, f"{per_name}subscriber.py")
            ofh = codecs.open(filepath, "w", encoding="utf-8")
            ofh.write(rt)
            ofh.close() 
            
            i += 1  
        
        elif peripheral_type[per_type] == "Actuator":
            actuator_attr = {
                "actuator_name": per_name,
                "actuator_type": per_type,
                "actuatorMsg": peripheralMsg[i],
                "topic": topic[i],
                "host": host,
                "port": port,
                "ssl": ssl,
                "username": username,
                "password": password
            } | attr[i]         
                
            template = env.get_template("MQTTActuatorPublisher.py.tmpl")
            rt = template.render(**actuator_attr)
            filepath = os.path.join(out_dir, f"{per_name}publisher.py")
            ofh = codecs.open(filepath, "w", encoding="utf-8")
            ofh.write(rt)
            ofh.close()  

            template = env.get_template("MQTTActuatorSubscriber.py.tmpl")
            rt = template.render(**actuator_attr)
            filepath = os.path.join(out_dir, f"{per_name}subscriber.py")
            ofh = codecs.open(filepath, "w", encoding="utf-8")
            ofh.write(rt)
            ofh.close() 
            
            i += 1  

    template = env.get_template("MQTTMessages.py.tmpl")
    rt = template.render()
    filepath = os.path.join(out_dir, f"MQTTMessages.py")
    ofh = codecs.open(filepath, "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()  

def main(dev_model, output_dir):
    # collect .dev models
    rpi5_device_path = os.path.join(REPO_PATH, "examples", dev_model)

    # Build the device model
    rpi5_device = utils.build_model(rpi5_device_path)

    output = os.path.join(REPO_PATH, output_dir)

    print("Collecting info...")
    get_info(rpi5_device) 
    print(f"pins : {pins}") 
    print(f"peripheral_ref_name : {peripheral_ref_name}") 
    print(f"peripheral_real_name : {peripheral_real_name}")
    print(f"peripheral_type : {peripheral_type}")
    print(f"Attributes : {attr}")
    print(f"Constraints : {constraints}")
    print(f"MESSAGES : {peripheralMsg}")
    print("Creating classes...")
    create_classes(out_dir=output)
    print("Generating processes")
    generate_process(out_dir=output)
    print(f"topic: {topic}, host: {host}, port: {port}, ssl: {ssl}, username: {username}, password: {password}")


if __name__ == "__main__":
    main("ThesisExample.dev", "rpi5_out")