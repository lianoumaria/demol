'''
This one is my currently working generator
'''

import os, sys
from definitions import *
from demol.lang import utils
from transformations import m2t_riot_old, device_to_plantuml
import jinja2
import codecs

# Collect .hwd models
TCRT_path = os.path.join(PERIPHERAL_MODEL_REPO_PATH, "TCRT5000.hwd")
SRF_path = os.path.join(PERIPHERAL_MODEL_REPO_PATH, "SRF05.hwd")
ToF_path = os.path.join(PERIPHERAL_MODEL_REPO_PATH, "VL53L1X.hwd")
TFMini_path = os.path.join(PERIPHERAL_MODEL_REPO_PATH, "TFMini.hwd")
rpi5_path = os.path.join(BOARD_MODEL_REPO_PATH, "rpi_5.hwd")

# collect .dev models
rpi5_device_path = os.path.join(REPO_PATH, "examples", "rpi_5_TCRT.dev")

# Build the component models
TCRT = utils.build_model(TCRT_path)
SRF = utils.build_model(TCRT_path)
VL53L1X = utils.build_model(ToF_path)
TFMini = utils.build_model(TFMini_path)
rpi5 = utils.build_model(rpi5_path)

# Build the device model
rpi5_device = utils.build_model(rpi5_device_path)

#Then try to call the function that generates riot 
out_dir = os.path.join(REPO_PATH, "rpi5_out")

fsloader = jinja2.FileSystemLoader(TEMPLATES_RASPI)
env = jinja2.Environment(loader=fsloader)


def generate_code(device_model, component_models, outputDir):
    # device_model is the .dev (parsed file) 
    # component_models is a list of all the board and peripherals used
    device_to_plantuml.device_to_plantuml(device_model)
    board_name = device_model.components.board.name
    peripheral_ref_name = {}
    peripheral_real_name = {}
    peripheral_type = {}
    pins = {}
    attr = {}

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
        
        attr[i] = []
        for attribute in device_model.connections[i].peripheral.ref.attributes:
            attr[i].append({attribute.name: attribute.default})
        
        # Εδώ στα attributes για απλότητα θα μπορούσα να κάνω έλεγχο για κατάληψη ίδιων pins από
        # διαφορετικούς αισθητήρες. Υπενθύμιση ότι στα i2c επιτρέπεται αλλά εκεί πρέπει να γίνει 
        # έλεγχος για ίδια slave_addresses
                   
    #modules = list(peripheral_real_name.values())
    print(pins)
    print(peripheral_ref_name, peripheral_real_name, peripheral_type)
    print(attr)


    template1 = env.get_template(
    'main.py.tmpl')

    rt = template1.render(ref_periph = peripheral_real_name,
                          pins = pins, 
                          attribute = attr,
                          templates = TEMPLATES_RASPI,
                          peripheral_types = peripheral_type)
    filepath = os.path.join(outputDir, "main.py")
    ofh = codecs.open(filepath, "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()


def main():
    generate_code(rpi5_device, [rpi5, TCRT, SRF, VL53L1X, TFMini], out_dir)


if __name__ == "__main__":
    main()
