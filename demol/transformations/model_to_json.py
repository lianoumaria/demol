import json
from typing import Dict
from textx.lang import PRIMITIVE_PYTHON_TYPES

def pins2dict(pins):
    power_pins = []
    io_pins = []
    for pin in pins:
        if pin.__class__.__name__ == "PowerPin":
            p = pin.to_dict()
            power_pins.append(p)
        else:
            funcs = []
            for fun in pin.funcs:
                f = fun.to_dict()
                # print(fun.to_dict())
                funcs.append(f)
            p = pin.to_dict()
            p['funcs'] = funcs
            io_pins.append(p)
    return {
        'power': power_pins,
        'io': io_pins
    }


def board2dict(board):
    return {
        'name': board.name,
        'cpu': board.cpu.to_dict(),
        'memory': board.memory.to_dict(),
        'vcc': board.vcc,
        'bluetooth': board.bluetooth,
        'pins': pins2dict(board.pins)
    }


def peripheral2dict(peripheral):
    _d = {
        'name': peripheral.name,
        'pins': pins2dict(peripheral.pins),
        'msg': peripheral.msg,
        'attributes': peripheral.attributes,
        'riotTpl': peripheral.riotTpl,
        'piTpl': peripheral.piTpl,
    }
    return _d


def conn2dict(conn):
    # print(conn.__dict__)
    board = board2dict(conn.board)
    peripheral = peripheral2dict(conn.peripheral.ref)
    endpoint = {
        'topic': conn.endpoint.topic,
        'type': conn.endpoint.type,
    }
    power_conns = []
    io_conns = []
    for con in conn.powerConns:
        c = {
            'boardPin': con.boardPin,
            'peripheralPin': con.peripheralPin,
        }
        power_conns.append(c)
    for con in conn.ioConns:
        if con.__class__.__name__ == 'GPIOConnection':
            c = {
                'type': con.type,
                'name': con.name,
                'pinConn': {
                    'boardPin': con.pinConn.boardPin,
                    'peripheralPin': con.pinConn.peripheralPin
                },
            }
            io_conns.append(c)
        elif con.__class__.__name__ == 'SPIConnection':
            c = {
                'type': con.type,
                'name': con.name,
                'mosi': {
                    'boardPin': con.mosi.boardPin,
                    'peripheralPin': con.mosi.peripheralPin
                },
                'miso': {
                    'boardPin': con.miso.boardPin,
                    'peripheralPin': con.miso.peripheralPin
                },
                'sck': {
                    'boardPin': con.sck.boardPin,
                    'peripheralPin': con.sck.peripheralPin
                },
                'cs': {
                    'boardPin': con.cs.boardPin,
                    'peripheralPin': con.cs.peripheralPin
                },
            }
            io_conns.append(c)
        elif con.__class__.__name__ == 'I2CConnection':
            c = {
                'type': con.type,
                'name': con.name,
                'slaveAddr': con.slaveAddr,
                'sda': {
                    'boardPin': con.sda.boardPin,
                    'peripheralPin': con.sda.peripheralPin
                },
                'scl': {
                    'boardPin': con.scl.boardPin,
                    'peripheralPin': con.scl.peripheralPin
                },
            }
            io_conns.append(c)
    return {
        'board': board,
        'peripheral': peripheral,
        'powerConns': power_conns,
        'ioConns': io_conns,
        'endpoint': endpoint,
    }


def model2json(model, output: str = "model.json") -> Dict:
    # print(PRIMITIVE_PYTHON_TYPES)
    metadata = model.metadata.to_dict()
    network = model.network.to_dict()
    comm = model.broker.to_dict()
    conns = []

    for conn in model.connections:
        c = conn2dict(conn)
        conns.append(c)

    _json = {
        'metadata': metadata,
        'network': network,
        'communication': comm,
        'connections': conns
    }
    with open(output, 'w') as f:
        json.dump(_json, f)
    return _json
