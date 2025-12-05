import os
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers
from textx import get_location, TextXSemanticError
from demol.definitions import *


GRAMMAR_BULTINS = {}


def raise_validation_error(obj, msg):
    raise TextXSemanticError(
        f'{msg}',
        **get_location(obj)
    )


def model_proc(model, metamodel):
    """
    Enhanced model processor with comprehensive validation based on formal semantics.
    
    Implements validation rules from SEMANTICS.md:
    - Section 4.1: Well-formedness rules
    - Section 6.7: Invariants
    - Section 8.1: Safety properties
    - Section 8.4: Well-formedness conditions
    """
    from demol.lang.semantics import (
        raise_validation_error,
        validate_power_connection,
        validate_gpio_connection,
        validate_i2c_connection,
        validate_spi_connection,
        validate_uart_connection,
        validate_no_pin_conflicts,
        validate_i2c_address_uniqueness,
        validate_voltage_limits,
        validate_all_peripherals_connected,
        validate_broker_requirements,
        validate_io_voltage_compatibility,
        validate_common_ground,
    )
    
    device_name = model.metadata.name.strip('"')

    print(f'[*] Processing model: {model._tx_filename}')
    
    # ========================================================================
    # Well-Formedness: All peripherals must be connected
    # ========================================================================
    validate_all_peripherals_connected(model)
    
    # ========================================================================
    # Well-Formedness: Broker requirements
    # ========================================================================
    validate_broker_requirements(model)
    
    # ========================================================================
    # Well-Formedness: Common ground check
    # ========================================================================
    validate_common_ground(model)
    
    board_name = model.components.board.name
    # ========================================================================
    # Process each connection
    # ========================================================================
    for c in model.connections:
        board = model.components.board
        # Set the board for easy navigation in M2M and M2T transformations
        setattr(c, 'board', model.components.board)
        peripheral = c.peripheral.ref
        
        # Get pin mappings
        board_pins_map = {p.name: p for p in board.pins}
        peripheral_pins_map = {p.name: p for p in peripheral.pins}
        board_pin_names = set(board_pins_map.keys())
        peripheral_pin_names = set(peripheral_pins_map.keys())
        
        # ====================================================================
        # Validate Power Connections
        # ====================================================================
        for pconn in c.powerConns:
            # Check if pins exist
            if pconn.boardPin not in board_pin_names:
                raise_validation_error(
                    pconn,
                    f'Board {board.name} does not have a pin named {pconn.boardPin}'
                )
            if pconn.peripheralPin not in peripheral_pin_names:
                raise_validation_error(
                    pconn,
                    f'Peripheral {c.peripheral.name} does not have a pin named {pconn.peripheralPin}'
                )
            
            # Enhanced validation: Check power compatibility
            board_pin = board_pins_map[pconn.boardPin]
            peripheral_pin = peripheral_pins_map[pconn.peripheralPin]
            
            # Only validate if both are power pins
            if (hasattr(board_pin, 'ptype') and hasattr(peripheral_pin, 'ptype')):
                validate_power_connection(board_pin, peripheral_pin, pconn)
        
        # ====================================================================
        # Validate IO Connections
        # ====================================================================
        for ioconn in c.ioConns:
            conn_type = ioconn.__class__.__name__
            
            if conn_type == 'GPIOConnection':
                pin_conn = ioconn.pinConn
                
                # Check if pins exist
                if pin_conn.boardPin not in board_pin_names:
                    raise_validation_error(
                        pin_conn,
                        f'Board {board.name} does not have a pin named {pin_conn.boardPin}'
                    )
                if pin_conn.peripheralPin not in peripheral_pin_names:
                    raise_validation_error(
                        pin_conn,
                        f'Peripheral {peripheral.name} does not have a pin named {pin_conn.peripheralPin}'
                    )
                
                # Enhanced validation: Check GPIO functionality
                board_pin = board_pins_map[pin_conn.boardPin]
                peripheral_pin = peripheral_pins_map[pin_conn.peripheralPin]
                validate_gpio_connection(board_pin, peripheral_pin, ioconn)
                
            elif conn_type == 'I2CConnection':
                sda = ioconn.sda
                scl = ioconn.scl
                
                # Check if pins exist
                pin_conns = [sda, scl]
                for pc in pin_conns:
                    if pc.boardPin not in board_pin_names:
                        raise_validation_error(
                            pc,
                            f'Board {board.name} does not have a pin named {pc.boardPin}'
                        )
                    if pc.peripheralPin not in peripheral_pin_names:
                        raise_validation_error(
                            pc,
                            f'Peripheral {peripheral.name} does not have a pin named {pc.peripheralPin}'
                        )
                
                # Enhanced validation: Check I2C functionality and address range
                board_sda = board_pins_map[sda.boardPin]
                board_scl = board_pins_map[scl.boardPin]
                peripheral_sda = peripheral_pins_map[sda.peripheralPin]
                peripheral_scl = peripheral_pins_map[scl.peripheralPin]
                validate_i2c_connection(
                    board_sda, board_scl, peripheral_sda, peripheral_scl,
                    ioconn.slaveAddr, ioconn
                )
                
            elif conn_type == 'SPIConnection':
                miso = ioconn.miso
                mosi = ioconn.mosi
                sck = ioconn.sck
                cs = ioconn.cs
                
                # Check if pins exist
                pin_conns = [miso, mosi, sck, cs]
                for pc in pin_conns:
                    if pc.boardPin not in board_pin_names:
                        raise_validation_error(
                            pc,
                            f'Board {board.name} does not have a pin named {pc.boardPin}'
                        )
                    if pc.peripheralPin not in peripheral_pin_names:
                        raise_validation_error(
                            pc,
                            f'Peripheral {peripheral.name} does not have a pin named {pc.peripheralPin}'
                        )
                
                # Enhanced validation: Check SPI functionality
                board_spi_pins = {
                    'mosi': board_pins_map[mosi.boardPin],
                    'miso': board_pins_map[miso.boardPin],
                    'sck': board_pins_map[sck.boardPin],
                    'cs': board_pins_map[cs.boardPin]
                }
                peripheral_spi_pins = {
                    'mosi': peripheral_pins_map[mosi.peripheralPin],
                    'miso': peripheral_pins_map[miso.peripheralPin],
                    'sck': peripheral_pins_map[sck.peripheralPin],
                    'cs': peripheral_pins_map[cs.peripheralPin]
                }
                validate_spi_connection(board_spi_pins, peripheral_spi_pins, ioconn)
                
            elif conn_type == 'UARTConnection':
                tx = ioconn.tx
                rx = ioconn.rx
                
                # Check if pins exist
                pin_conns = [tx, rx]
                for pc in pin_conns:
                    if pc.boardPin not in board_pin_names:
                        raise_validation_error(
                            pc,
                            f'Board {board.name} does not have a pin named {pc.boardPin}'
                        )
                    if pc.peripheralPin not in peripheral_pin_names:
                        raise_validation_error(
                            pc,
                            f'Peripheral {peripheral.name} does not have a pin named {pc.peripheralPin}'
                        )
                
                # Enhanced validation: Check UART functionality and baudrate
                board_tx = board_pins_map[tx.boardPin]
                board_rx = board_pins_map[rx.boardPin]
                peripheral_tx = peripheral_pins_map[tx.peripheralPin]
                peripheral_rx = peripheral_pins_map[rx.peripheralPin]
                validate_uart_connection(
                    board_tx, board_rx, peripheral_tx, peripheral_rx,
                    ioconn.baudrate, ioconn
                )
        
        # ====================================================================
        # Auto-generate topic if not specified
        # ====================================================================
        if c.endpoint and not c.endpoint.topic:
            peripheral_def = c.peripheral
            peripheral_ref = peripheral_def.ref
            peripheral_def_name = peripheral_def.name
            peripheral_type = type(peripheral_ref).__name__
            peripheral_msg = peripheral_ref.type
            
            default_topic = f'"{device_name}.{peripheral_type}.{peripheral_msg}.{peripheral_def_name}"'
            c.endpoint.topic = default_topic.lower().strip('""')
    
    # ========================================================================
    # Global Safety Validations
    # ========================================================================
    
    # Safety: No pin conflicts (unique pins per connection)
    validate_no_pin_conflicts(model.connections)
    
    # Safety: I2C addresses must be unique on the same bus
    validate_i2c_address_uniqueness(model.connections)
    
    # Safety: Voltage limits must not be exceeded
    validate_voltage_limits(model)
    
    # Safety: IO Voltage compatibility
    validate_io_voltage_compatibility(model)
    
    # Safety: Common ground connection
    validate_common_ground(model)
    
    print("[✓] All validation checks passed!")


def get_device_mm(debug: bool = False, global_repo: bool = False):
    mm = metamodel_from_file(
        os.path.join(METAMODEL_REPO_PATH, 'device.tx'),
        auto_init_attributes=True,
        global_repository=global_repo,
        textx_tools_support=True,
        debug=debug
    )

    mm.register_scope_providers(
        {
            "*.*": scoping_providers.FQN(),
            "*.*": scoping_providers.FQNImportURI(importAs=True),
            "Components.peripherals": scoping_providers.FQNGlobalRepo(
                os.path.join(PERIPHERAL_MODEL_REPO_PATH, '*.hwd')
            ),
            "Components.board": scoping_providers.FQNGlobalRepo(
                os.path.join(BOARD_MODEL_REPO_PATH, '*.hwd')
            ),

        }
    )

    mm.register_model_processor(model_proc)

    mm.register_obj_processors({

        # EMPTY
    })

    return mm
