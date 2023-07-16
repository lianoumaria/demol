import os
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers
from textx import get_location, TextXSemanticError
from .definitions import *


def create_output_dirs(out_dir: str):
    diagrams_dir = os.path.join(out_dir, DIAGRAMS_DIRNAME)
    if not os.path.exists(diagrams_dir):
        # If it doesn't exist, create it
        os.makedirs(diagrams_dir)
    riot_src_dir = os.path.join(out_dir, RIOT_SOURCE_DIRNAME)
    if not os.path.exists(riot_src_dir):
        # If it doesn't exist, create it
        os.makedirs(riot_src_dir)


def get_device_metamodel():
    # Get meta-model from language description
    mm= metamodel_from_file(
        os.path.join(METAMODEL_REPO_PATH, 'devices.tx'),
        global_repository=True,
        debug=False
    )

    mm.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(
                importAs=True,
            )
        }
    )
    mm.register_obj_processors({
        # EMPTY
    })

    return mm


def get_synthesis_metamodel():
    mm= metamodel_from_file(
        os.path.join(METAMODEL_REPO_PATH, 'synthesis.tx'),
        global_repository=True,
        debug=False
    )

    mm.register_scope_providers(
        {
            # "*.*": scoping_providers.FQNImportURI(
            #     importAs=True,
            # ),
            "*.*": scoping_providers.FQN(),
            "DevicesBag.board": scoping_providers.FQNGlobalRepo(
                os.path.join(BOARD_MODEL_REPO_PATH, '*.hwd')
            ),
            "DevicesBag.peripherals": scoping_providers.FQNGlobalRepo(
                os.path.join(PERIPHERAL_MODEL_REPO_PATH, '*.hwd')
            ),
            # 'Connection.board': 'devices.board'
            # "Connection.board": scoping_providers.PlainName(
            #     "devices.board"
            # ),
        }
    )

    def model_proc(model, metamodel):
        for c in model.connections:
            board_pins = [p.name for p in c.board.pins]
            per_pins = [p.name for p in c.peripheral.pins]
            if c.peripheral not in model.deviceBag.peripherals:
                raise TextXSemanticError(
                    f'Peripheral {c.peripheral.name} not defined in Bag of devices!'
                )
            if c.board != model.deviceBag.board:
                raise TextXSemanticError(
                    f'Board {c.board.name} not defined in Bag of devices!'
                )
            for pconn in c.powerConns:
                print(
                    f'PowerPinConnection:\n'
                    f'  {pconn.boardPin} -> {pconn.peripheralPin}'
                )
                if pconn.boardPin not in board_pins:
                    raise TextXSemanticError(
                        f'Board {c.board.name} does not have a pin '
                        'named {pconn.boardPin}'
                    )
                if pconn.peripheralPin not in per_pins:
                    raise TextXSemanticError(
                        f'Peripheral {c.peripheral.name} does not have a '
                        'pin named {pconn.peripheralPin}'
                    )

            for ioconn in c.ioConns:
                if ioconn.__class__.__name__ == 'GPIOConnection':
                    pin_conn = ioconn.pinConn
                    print(
                        f'GPIO-Connection:\n'
                        f'  {pin_conn.boardPin} -> {pin_conn.peripheralPin}'
                    )
                    if pin_conn.boardPin not in board_pins:
                        raise TextXSemanticError(
                            f'Board {c.board.name} does not have a pin '
                            f'named {pin_conn.boardPin}'
                        )
                    if pin_conn.peripheralPin not in per_pins:
                        raise TextXSemanticError(
                            f'Peripheral {c.peripheral.name} does not have a '
                            f'pin named {pin_conn.peripheralPin}'
                        )

                elif ioconn.__class__.__name__ == 'SPIConnection':
                    miso = ioconn.miso
                    mosi = ioconn.mosi
                    sck = ioconn.sck
                    cs = ioconn.cs
                    print(
                        f'SPI-Connection: \n'
                        f'  {miso.boardPin} -> {miso.peripheralPin}\n'
                        f'  {mosi.boardPin} -> {mosi.peripheralPin}\n'
                        f'  {sck.boardPin} -> {sck.peripheralPin}\n'
                        f'  {cs.boardPin} -> {cs.peripheralPin}'
                    )
                    pin_conns = [miso, mosi, sck, cs]
                    for pc in pin_conns:
                        if pc.boardPin not in board_pins:
                            raise TextXSemanticError(
                                f'Board {c.board.name} does not have a pin '
                                f'named {pc.boardPin}'
                            )
                        if pc.peripheralPin not in per_pins:
                            raise TextXSemanticError(
                                f'Peripheral {c.peripheral.name} does not have a '
                                f'pin named {pc.peripheralPin}'
                            )
                elif ioconn.__class__.__name__ == 'I2CConnection':
                    sda = ioconn.sda
                    scl = ioconn.scl
                    print(
                        f'I2C-Connection:\n'
                        f'  SDA: {sda.boardPin} -> {sda.peripheralPin}\n'
                        f'  SCL: {scl.boardPin} -> {scl.peripheralPin}'
                    )
                    pin_conns = [sda, scl]
                    for pc in pin_conns:
                        if pc.boardPin not in board_pins:
                            raise TextXSemanticError(
                                f'Board {c.board.name} does not have a pin '
                                f'named {pc.boardPin}'
                            )
                        if pc.peripheralPin not in per_pins:
                            raise TextXSemanticError(
                                f'Peripheral {c.peripheral.name} does not have a '
                                f'pin named {pc.peripheralPin}'
                            )


    mm.register_model_processor(model_proc)

    mm.register_obj_processors({
        # EMPTY
    })

    return mm


def get_device_model(model_path):
    return get_device_metamodel().model_from_file(model_path)


def get_synthesis_model(model_path):
    return get_connection_metamodel().model_from_file(model_path)

def build_device_model(moel_path):
    return get_device_model(model_path)

def build_synthesis_model(moel_path):
    return get_device_model(model_path)
