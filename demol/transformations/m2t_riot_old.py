import os
import sys
import argparse
import pydot
import shutil
import jinja2
import codecs

from demol.definitions import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

fsloader = jinja2.FileSystemLoader(TEMPLATES)
env = jinja2.Environment(loader=fsloader)


def gen_src_riot(connection_model, device_models, out_dir):
    """ Produce source code from templates """

    # Load C template
    template1 = env.get_template(
        'base.c.tmpl')

    # Load Makefile template
    template2 = env.get_template(
        'Makefile.tmpl')

    peripheral_name_tmp = {}
    peripheral_type_tmp = {}
    id_tmp = {}
    frequency_tmp = {}
    module_tmp = {}
    args_tmp = {}
    topic_tmp = {}
    num_of_peripherals_tmp = len(connection_model.connections)

    # Name of board
    board_name_tmp = connection_model.connections[0].board.device
    if board_name_tmp == 'esp32_wroom_32':
        board_name_tmp = 'esp32-wroom-32'
    elif board_name_tmp == 'wemos_d1_mini':
        board_name_tmp = 'esp8266-esp-12x'

    # Wifi credentials
    wifi_ssid_tmp = connection_model.connections[0].com_endpoint.wifi_ssid[:-1]
    wifi_passwd_tmp = connection_model.connections[0].com_endpoint.wifi_passwd[:-1]

    for i in range(len(connection_model.connections)):

        # Parse info from the created models
        address_tmp = connection_model.connections[i].com_endpoint.addr
        id_tmp[i] = i + 1
        mqtt_port = connection_model.connections[i].com_endpoint.port
        peripheral_name_tmp[i] = connection_model.connections[i].peripheral.device
        peripheral_type_tmp[peripheral_name_tmp[i]] = device_models[peripheral_name_tmp[i]].type
        module_tmp[i] = connection_model.connections[i].peripheral.device
        topic_tmp[i] = connection_model.connections[i].com_endpoint.topic[:-1]

        # Publishing frequency (always convert to Hz)
        # If not given, default value is 1Hz
        if( hasattr(connection_model.connections[i].com_endpoint.freq, 'val') ):
            frequency_tmp[i] = connection_model.connections[i].com_endpoint.freq.val
            frequency_unit = connection_model.connections[i].com_endpoint.freq.unit
            if (frequency_unit == "khz"):
                frequency_tmp[i] = (10**3) * frequency_tmp[i]
            elif (frequency_unit == "mhz"):
                frequency_tmp[i] = (10**6) * frequency_tmp[i]
            elif (frequency_unit == "ghz"):
                frequency_tmp[i] = (10**9) * frequency_tmp[i]
        else:
            frequency_tmp[i] = 1

        # Hardware connection args
        args_tmp[i] = {}

        if (connection_model.connections[i].hw_conns[0].type == 'gpio'):
            for hw_conn in connection_model.connections[i].hw_conns:
                args_tmp[i][hw_conn.peripheral_int] = (hw_conn.board_int).split("_",1)[1]
        elif (connection_model.connections[i].hw_conns[0].type == 'i2c'):
            args_tmp[i]["sda"] = (connection_model.connections[i].hw_conns[0].board_int[0]).split("_",1)[1]
            args_tmp[i]["scl"] = (connection_model.connections[i].hw_conns[0].board_int[1]).split("_",1)[1]
            args_tmp[i]["slave_address"] = connection_model.connections[i].hw_conns[0].slave_addr
            if(connection_model.connections[i].peripheral.device == 'bme680'):
                module_tmp[i] = module_tmp[i] + '_i2c'

    # Check if a template exists for each given peripheral
    all_tmpl_exist = True
    for peripheral in peripheral_name_tmp.values():
        file = TEMPLATES + peripheral + '.c.tmpl'
        if os.path.isfile(file) == False:
            print("No template for peripheral " + peripheral + " found!")
            all_tmpl_exist = False
            if peripheral_type_tmp[peripheral] == 'sensor':
                shutil.copyfile(TEMPLATES + 'unsupported_sensor.txt', file)
            elif peripheral_type_tmp[peripheral] == 'actuator':
                shutil.copyfile(TEMPLATES + 'unsupported_actuator.txt', file)

    if all_tmpl_exist == False:
        sys.exit('\nA template for each one of the peripheral(s) mentioned above' + \
                 '\nwas created. You need to fill it with appropriate code ...')

    # C template
    rt = template1.render(address=address_tmp,
                          id=id_tmp,
                          port=mqtt_port,
                          peripheral_name=peripheral_name_tmp,
                          peripheral_type=peripheral_type_tmp,
                          args=args_tmp,
                          topic=topic_tmp,
                          frequency=frequency_tmp,
                          num_of_peripherals = num_of_peripherals_tmp,
                          templates = TEMPLATES)
    filepath = os.path.join(out_dir, RIOT_SOURCE_DIRNAME, 'main.c')
    ofh = codecs.open(filepath, "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()

    # Makefile template
    rt = template2.render(filepath=filepath,
                          module=module_tmp,
                          board_name=board_name_tmp,
                          wifi_ssid=wifi_ssid_tmp,
                          wifi_passwd=wifi_passwd_tmp)
    filepath = os.path.join(out_dir, RIOT_SOURCE_DIRNAME, 'Makefile')
    ofh = codecs.open(filepath, "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()


def generate_diagrams(out_dir, model):
    generate_class_diagram(out_dir, model)
    generate_system_diagram(out_dir, model)


def generate_system_diagram(out_dir: str, model):
    # Export model to PlantUML (.pu) and then png
    filename = 'system_diagram.pu'
    model_to_system_diagram(
        model,
        os.path.join(out_dir, DIAGRAMS_DIRNAME, filename)
    )
    os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 ' +
              os.path.join(out_dir, DIAGRAMS_DIRNAME, filename))


def generate_class_diagram(out_dir: str, model):
    filename = 'class_diagram.pu'
    model_to_class_diagram(
        model,
        os.path.join(out_dir, DIAGRAMS_DIRNAME, filename)
    )
    os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 ' +
              os.path.join(out_dir, DIAGRAMS_DIRNAME, filename))


# PlantUML generation for connection model
def model_to_system_diagram(model, filename):

    f = open(filename, "w")

    tmp = '@startuml\n' + \
        '\nskinparam componentStyle rectangle' + \
        '\nskinparam linetype ortho' + \
        '\nskinparam NoteFontSize 15' + \
        '\nskinparam NoteFontStyle italics' + \
        '\nskinparam RectangleFontSize 16\n' + \
        '\n!define T2 \\t\\t' + \
        '\n!define T5 \\t\\t\\t\\t\\t' + \
        '\n!define NL2 \\n\\n' + \
        '\n!define NL4 \\n\\n\\n\\n\n\n'
    f.write(tmp)

    tmp = 'component [NL4 T5 **' + str(model.connections[0].board.device) + \
        '** T5 NL4] as ' + str(model.connections[0].board.device) + ' #FFF9C2\n'
    f.write(tmp)

    for i in range(len(model.connections)):
        tmp = 'component [' + (i%4 < 2)*'NL4 T2' + (i%4 >= 2)*'NL2 T5' + \
            ' **' + str(model.connections[i].peripheral.device) + \
            '** ' +  (i%4 < 2)*'T2 NL4' + (i%4 >= 2)*'T5 NL2' + \
            '] as ' + str(model.connections[i].peripheral.device) + \
            ' #CAE2C8\n'
        f.write(tmp)
    f.write('\n')

    note_directions = ['top', 'bottom', 'right', 'left']
    for i in range(len(model.connections)):
        tmp = 'note ' + note_directions[i%4] + ' of ' + \
            str(model.connections[i].peripheral.device) + \
            ' : topic - "' + str(model.connections[i].com_endpoint.topic[:-1]) + '"\n'
        f.write(tmp)
    f.write('\n')

    pin_directions = ['le', 'ri', 'up', 'down']
    for i in range(len(model.connections)):

        for j in range(len(model.connections[i].hw_conns)):
            if model.connections[i].hw_conns[j].type == 'gpio':
                tmp = str(model.connections[i].board.device) + \
                    ' "**' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '**" #--' + str(pin_directions[i]) + '--# "**' + \
                    str(model.connections[i].hw_conns[j].board_int) + \
                    '**" ' + str(model.connections[i].peripheral.device) + \
                    (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            elif model.connections[i].hw_conns[j].type == 'i2c':
                tmp = ''
                for k in range(2):
                    tmp = tmp + str(model.connections[i].board.device) + \
                        ' "**' + str(model.connections[i].hw_conns[j].peripheral_int[k]) + \
                        '**" #--' + str(pin_directions[i]) + '--# "**' + \
                        str(model.connections[i].hw_conns[j].board_int[k]) + \
                        '**" ' + str(model.connections[i].peripheral.device) + \
                        (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            f.write(tmp)

        for j in range(len(model.connections[i].power_conns)):
            tmp = str(model.connections[i].board.device) + \
                ' "**' + str(model.connections[i].power_conns[j].peripheral_power) + \
                '**" #--' + str(pin_directions[i]) + '--# "**' + \
                str(model.connections[i].power_conns[j].board_power) + \
                '**" ' + str(model.connections[i].peripheral.device) + \
                (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            f.write(tmp)

        f.write('\n')


    f.write('\nhide @unlinked\n@enduml')

    f.close()


def model_to_class_diagram(model, filename):
    f = open(filename, "w")
    f.write('@startuml\nset namespaceSeparator .\n\n\n')
    f.write('class connections.SYSTEM  {\n}\n\n\n')

    for i in range(len(model.includes)):
        tmp = 'class connections.INCLUDE_' + str(i) + \
            '  {\n  name: str=\'' + model.includes[i].name + \
            '\'\n}\n\n\n'
        f.write(tmp)

    for i in range(len(model.connections)):
        tmp = 'class connections.CONNECTION_' + str(i) + \
            '  {\n  name: ' + model.connections[i].name + \
            '\n}\n\n\n'
        f.write(tmp)

        tmp = 'class connections.BOARD_' + str(i) + \
            '  {\n  device: str=\'' + model.connections[i].board.device + '\'\n' + \
            '  number: int=' + str(model.connections[i].board.number) + '\n}\n\n\n'
        f.write(tmp)

        tmp = 'class connections.PERIPHERAL_' + str(i) + \
            '  {\n  device: str=\'' + model.connections[i].peripheral.device + '\'\n' + \
            '  number: int=' + str(model.connections[i].peripheral.number) + '\n}\n\n\n'
        f.write(tmp)

        for j in range(len(model.connections[i].power_conns)):
            tmp = 'class connections.POWER_CONNECTION_' + str(i) + '_' + str(j) + \
                '  {\n  board_power: str=\'' + model.connections[i].power_conns[j].board_power + '\'\n' + \
                '  peripheral_power: str=\'' + str(model.connections[i].power_conns[j].peripheral_power) + \
                '\'\n}\n\n\n'
            f.write(tmp)

        for j in range(len(model.connections[i].hw_conns)):

            if model.connections[i].hw_conns[j].type == 'gpio':
                tmp = 'class connections.GPIO_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '\'\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'i2c':
                tmp = 'class connections.I2C_' + str(i) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: list=[\'' + \
                        model.connections[i].hw_conns[j].board_int[0] + '\',\'' + \
                        model.connections[i].hw_conns[j].board_int[1]+ '\']\n' + \
                    '  peripheral_int: list=[\'' + \
                        model.connections[i].hw_conns[j].peripheral_int[0] + '\',\'' + \
                        model.connections[i].hw_conns[j].peripheral_int[1]+ '\']\n' + \
                    '  slave_addr: int=' + str(model.connections[i].hw_conns[j].slave_addr) + \
                    '\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'pwm':
                tmp = 'class connections.PWM_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '\'\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'spi':
                tmp = 'class connections.SPI_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '\'\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'uart':
                tmp = 'class connections.UART_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + '\'\n' + \
                    '  baudrate: int=' + str(model.connections[i].hw_conns[j].baudrate) + '\n}\n\n\n'
                f.write(tmp)

        tmp = 'class connections.COM_ENDPOINT_' + str(i) + \
            '  {\n  topic: str=\'' + model.connections[i].com_endpoint.topic[:-1] + '\'\n' + \
            '  addr: str=\'' + model.connections[i].com_endpoint.addr + '\'\n' + \
            '  port: int=' + str(model.connections[i].com_endpoint.port) + '\n}\n\n\n'
        f.write(tmp)

        msg_entries = ''
        for j in range(len(model.connections[i].com_endpoint.msg.msg_entries)):
            msg_entries += '\'' + model.connections[i].com_endpoint.msg.msg_entries[j] + '\','
        msg_entries = msg_entries[:-1]

        tmp = 'class connections.MSG_ENTRIES_' + str(i) + \
            '  {\n  msg_entries: list=[' + msg_entries + ']' + '\n}\n\n\n'
        f.write(tmp)

        if( hasattr(model.connections[i].com_endpoint.freq, 'val') ):
            tmp = 'class connections.FREQUENCY_' + str(i) + \
                '  {\n  val: int=' + str(model.connections[i].com_endpoint.freq.val) + '\n' + \
                '  unit: str=\'' + model.connections[i].com_endpoint.freq.unit + \
                '\'\n}\n\n\n'
            f.write(tmp)

    # Relations

    for i in range(len(model.includes)):
        tmp = 'connections.SYSTEM *-- "includes:' + str(i) + \
            '" connections.INCLUDE_' + str(i) + '\n'
        f.write(tmp)

    for i in range(len(model.connections)):
        tmp = 'connections.SYSTEM *-- "connections:' + str(i) + \
            '" connections.CONNECTION_' + str(i) + '\n'
        f.write(tmp)

        tmp = 'connections.CONNECTION_' + str(i) + \
            ' *-- "board" connections.BOARD_' + str(i) + '\n'
        f.write(tmp)

        tmp = 'connections.CONNECTION_' + str(i) + \
            ' *-- "peripheral" connections.PERIPHERAL_' + str(i) + '\n'
        f.write(tmp)

        for j in range(len(model.connections[i].power_conns)):
            tmp = 'connections.CONNECTION_' + str(i) + ' *-- "power_conns:' + str(j) + \
                '" connections.POWER_CONNECTION_' + str(i) + '_' + str(j) + '\n'
            f.write(tmp)

        for j in range(len(model.connections[i].hw_conns)):

            if model.connections[i].hw_conns[j].type == 'gpio':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.GPIO_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'i2c':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.I2C_' + str(i) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'pwm':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.PWM_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'spi':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.SPI_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'uart':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.UART_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)

        tmp = 'connections.CONNECTION_' + str(i) + \
            ' *-- "com_endpoint" connections.COM_ENDPOINT_' + str(i) + '\n'
        f.write(tmp)

        tmp = 'connections.COM_ENDPOINT_' + str(i) + \
            ' *-- "msg" connections.MSG_ENTRIES_' + str(i) + '\n'
        f.write(tmp)

        if( hasattr(model.connections[i].com_endpoint.freq, 'val') ):
            tmp = 'connections.COM_ENDPOINT_' + str(i) + \
                ' *-- "freq" connections.FREQUENCY_' + str(i) + '\n'
            f.write(tmp)

    f.write('\n@enduml')

    f.close()
