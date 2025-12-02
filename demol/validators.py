"""
Enhanced Validation Module for DeMoL
Based on formal semantics defined in SEMANTICS.md

This module implements:
- Well-formedness rules (Section 4 of SEMANTICS.md)
- Safety properties (Section 8.1 of SEMANTICS.md)
- Type checking (Section 7 of SEMANTICS.md)
- Constraint validation (Section 4.1 of SEMANTICS.md)
"""

from textx import get_location, TextXSemanticError
from typing import List, Set, Dict, Optional, Tuple
import re


class ValidationError(TextXSemanticError):
    """Custom validation error with location information"""
    pass


def raise_validation_error(obj, msg: str, error_type: str = "Validation"):
    """Raise a validation error with location information"""
    raise TextXSemanticError(
        f'[{error_type}] {msg}',
        **get_location(obj)
    )


# ============================================================================
# Power Connection Validation
# ============================================================================

def parse_voltage(power_type: str) -> Optional[float]:
    """
    Parse voltage from power type string.
    
    Examples:
        GND -> 0.0
        3V3 -> 3.3
        5V -> 5.0
        12V -> 12.0
        3.3V -> 3.3
        2.5V -> 2.5
    """
    power_type_upper = power_type.upper()
    
    if power_type_upper == 'GND':
        return 0.0
    elif power_type_upper == '3V3':
        return 3.3
    elif power_type_upper == '5V':
        return 5.0
    elif power_type_upper == '12V':
        return 12.0
    
    # Try to parse custom voltage format like "3.3V" or "2.5V"
    match = re.match(r'(\d+\.?\d*)V?', power_type_upper)
    if match:
        return float(match.group(1))
    
    return None


def are_voltages_compatible(v1: float, v2: float, tolerance: float = 0.5) -> bool:
    """
    Check if two voltages are compatible.
    
    From SEMANTICS.md Section 4.1:
        compatible(v₁, v₂) ≡ (v₁ = v₂) ∨ (v₁ = Custom(x) ∧ v₂ = Custom(y) ∧ |x - y| ≤ 0.5)
    """
    return abs(v1 - v2) <= tolerance


def validate_power_connection(board_pin, peripheral_pin, connection) -> None:
    """
    Validate power connection compatibility.
    
    Implements rules from SEMANTICS.md Section 4.1:
    - [T-PowerConn-GND]: Both pins must be GND
    - [T-PowerConn-VCC]: Voltages must be compatible
    """
    board_voltage = parse_voltage(board_pin.ptype)
    peripheral_voltage = parse_voltage(peripheral_pin.ptype)
    
    if board_voltage is None:
        raise_validation_error(
            connection,
            f"Invalid board power pin type: {board_pin.ptype}",
            "PowerTypeError"
        )
    
    if peripheral_voltage is None:
        raise_validation_error(
            connection,
            f"Invalid peripheral power pin type: {peripheral_pin.ptype}",
            "PowerTypeError"
        )
    
    # Rule [T-PowerConn-GND]: Both GND
    if board_voltage == 0.0 and peripheral_voltage == 0.0:
        return  # Valid GND connection
    
    # Rule [T-PowerConn-VCC]: Non-GND voltages must be compatible
    if board_voltage != 0.0 and peripheral_voltage != 0.0:
        if not are_voltages_compatible(board_voltage, peripheral_voltage):
            raise_validation_error(
                connection,
                f"Incompatible power connection: board pin {board_pin.name} "
                f"({board_voltage}V) cannot connect to peripheral pin "
                f"{peripheral_pin.name} ({peripheral_voltage}V). "
                f"Voltage difference exceeds 0.5V tolerance.",
                "VoltageIncompatibilityError"
            )
        return
    
    # One is GND and the other is not - invalid
    raise_validation_error(
        connection,
        f"Cannot connect GND pin to power pin: board pin {board_pin.name} "
        f"({board_voltage}V) to peripheral pin {peripheral_pin.name} "
        f"({peripheral_voltage}V)",
        "PowerConnectionError"
    )


# ============================================================================
# Connection Validation
# ============================================================================

def get_pin_functions(pin) -> Set[str]:
    """Extract all function types from a pin"""
    functions = set()
    
    if not hasattr(pin, 'funcs'):
        return functions
    
    for func in pin.funcs:
        if hasattr(func, 'ptype'):
            # For I2C, SPI, UART, PWM functions with bus/channel
            functions.add(func.ptype)
        else:
            # For simple functions like GPIO, ADC, DAC
            functions.add('gpio')  # Default interpretation
    
    return functions


def validate_gpio_connection(board_pin, peripheral_pin, connection) -> None:
    """
    Validate GPIO connection.
    
    Implements [T-GPIO-Conn] from SEMANTICS.md Section 4.1:
        pin₁ : IOPin(_, _, funcs₁, _, _, _)    GPIO ∈ funcs₁
        pin₂ : IOPin(_, _, funcs₂, _, _, _)    GPIO ∈ funcs₂
    """
    board_funcs = get_pin_functions(board_pin)
    peripheral_funcs = get_pin_functions(peripheral_pin)
    
    # Check if both pins have GPIO functionality
    if 'gpio' not in board_funcs and not any('gpio' in str(f).lower() for f in board_funcs):
        raise_validation_error(
            connection,
            f"Board pin {board_pin.name} does not have GPIO functionality. "
            f"Available functions: {', '.join(board_funcs)}",
            "GPIOFunctionError"
        )
    
    if 'gpio' not in peripheral_funcs and not any('gpio' in str(f).lower() for f in peripheral_funcs):
        raise_validation_error(
            connection,
            f"Peripheral pin {peripheral_pin.name} does not have GPIO functionality. "
            f"Available functions: {', '.join(peripheral_funcs)}",
            "GPIOFunctionError"
        )


def validate_i2c_connection(board_sda, board_scl, peripheral_sda, peripheral_scl, 
                           slave_addr: int, connection) -> None:
    """
    Validate I2C connection.
    
    Implements [T-I2C-Conn] from SEMANTICS.md Section 4.1:
        - Board pins must have SDA/SCL functions
        - Peripheral pins must have SDA/SCL functions
        - Slave address must be in range 0x00-0x7F
    """
    # Validate slave address range
    if not (0x00 <= slave_addr <= 0x7F):
        raise_validation_error(
            connection,
            f"I2C slave address 0x{slave_addr:02X} out of valid range [0x00-0x7F]",
            "I2CAddressError"
        )
    
    # Check board SDA pin
    board_sda_funcs = get_pin_functions(board_sda)
    if not any('sda' in str(f).lower() for f in board_sda_funcs):
        raise_validation_error(
            connection,
            f"Board pin {board_sda.name} does not have SDA (I2C) functionality",
            "I2CFunctionError"
        )
    
    # Check board SCL pin
    board_scl_funcs = get_pin_functions(board_scl)
    if not any('scl' in str(f).lower() for f in board_scl_funcs):
        raise_validation_error(
            connection,
            f"Board pin {board_scl.name} does not have SCL (I2C) functionality",
            "I2CFunctionError"
        )
    
    # Check peripheral SDA pin
    peripheral_sda_funcs = get_pin_functions(peripheral_sda)
    if not any('sda' in str(f).lower() for f in peripheral_sda_funcs):
        raise_validation_error(
            connection,
            f"Peripheral pin {peripheral_sda.name} does not have SDA (I2C) functionality",
            "I2CFunctionError"
        )
    
    # Check peripheral SCL pin
    peripheral_scl_funcs = get_pin_functions(peripheral_scl)
    if not any('scl' in str(f).lower() for f in peripheral_scl_funcs):
        raise_validation_error(
            connection,
            f"Peripheral pin {peripheral_scl.name} does not have SCL (I2C) functionality",
            "I2CFunctionError"
        )


def validate_spi_connection(board_pins: Dict[str, object], peripheral_pins: Dict[str, object],
                           connection) -> None:
    """
    Validate SPI connection.
    
    Checks that all required SPI pins (MOSI, MISO, SCK, CS) have appropriate functionality.
    """
    spi_pin_types = ['mosi', 'miso', 'sck', 'cs']
    
    for pin_type in spi_pin_types:
        # Check board pin
        board_pin = board_pins[pin_type]
        board_funcs = get_pin_functions(board_pin)
        if not any(pin_type in str(f).lower() for f in board_funcs):
            raise_validation_error(
                connection,
                f"Board pin {board_pin.name} does not have {pin_type.upper()} (SPI) functionality",
                "SPIFunctionError"
            )
        
        # Check peripheral pin
        peripheral_pin = peripheral_pins[pin_type]
        peripheral_funcs = get_pin_functions(peripheral_pin)
        if not any(pin_type in str(f).lower() for f in peripheral_funcs):
            raise_validation_error(
                connection,
                f"Peripheral pin {peripheral_pin.name} does not have {pin_type.upper()} (SPI) functionality",
                "SPIFunctionError"
            )


def validate_uart_connection(board_tx, board_rx, peripheral_tx, peripheral_rx,
                            baudrate: int, connection) -> None:
    """
    Validate UART connection.
    
    Checks:
    - TX/RX pin functionality
    - Valid baudrate (common values)
    """
    # Validate baudrate
    valid_baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    if baudrate not in valid_baudrates:
        raise_validation_error(
            connection,
            f"Unusual UART baudrate {baudrate}. Common values: {valid_baudrates}",
            "UARTBaudrateWarning"
        )
    
    # Check TX pins
    board_tx_funcs = get_pin_functions(board_tx)
    if not any('tx' in str(f).lower() for f in board_tx_funcs):
        raise_validation_error(
            connection,
            f"Board pin {board_tx.name} does not have TX (UART) functionality",
            "UARTFunctionError"
        )
    
    peripheral_tx_funcs = get_pin_functions(peripheral_tx)
    if not any('tx' in str(f).lower() for f in peripheral_tx_funcs):
        raise_validation_error(
            connection,
            f"Peripheral pin {peripheral_tx.name} does not have TX (UART) functionality",
            "UARTFunctionError"
        )
    
    # Check RX pins
    board_rx_funcs = get_pin_functions(board_rx)
    if not any('rx' in str(f).lower() for f in board_rx_funcs):
        raise_validation_error(
            connection,
            f"Board pin {board_rx.name} does not have RX (UART) functionality",
            "UARTFunctionError"
        )
    
    peripheral_rx_funcs = get_pin_functions(peripheral_rx)
    if not any('rx' in str(f).lower() for f in peripheral_rx_funcs):
        raise_validation_error(
            connection,
            f"Peripheral pin {peripheral_rx.name} does not have RX (UART) functionality",
            "UARTFunctionError"
        )


# ============================================================================
# Safety Properties
# ============================================================================

def validate_no_pin_conflicts(connections: List) -> None:
    """
    Validate Safety-Unique-Pins invariant.
    
    From SEMANTICS.md Section 6.7:
        Inv-Unique-Pins: ∀k₁, k₂ ∈ connections, k₁ ≠ k₂. usedPins(k₁) ∩ usedPins(k₂) = ∅
    """
    board_pin_usage: Dict[str, List[str]] = {}
    
    for connection in connections:
        peripheral_name = connection.peripheral.name
        
        # Collect all board pins used in this connection
        used_pins = []
        
        # Power connections
        for pconn in connection.powerConns:
            used_pins.append(pconn.boardPin)
        
        # IO connections
        for ioconn in connection.ioConns:
            if ioconn.__class__.__name__ == 'GPIOConnection':
                used_pins.append(ioconn.pinConn.boardPin)
            elif ioconn.__class__.__name__ == 'I2CConnection':
                used_pins.append(ioconn.sda.boardPin)
                used_pins.append(ioconn.scl.boardPin)
            elif ioconn.__class__.__name__ == 'SPIConnection':
                used_pins.append(ioconn.mosi.boardPin)
                used_pins.append(ioconn.miso.boardPin)
                used_pins.append(ioconn.sck.boardPin)
                used_pins.append(ioconn.cs.boardPin)
            elif ioconn.__class__.__name__ == 'UARTConnection':
                used_pins.append(ioconn.tx.boardPin)
                used_pins.append(ioconn.rx.boardPin)
        
        # Check for conflicts
        for pin in used_pins:
            if pin in board_pin_usage:
                raise_validation_error(
                    connection,
                    f"Pin conflict detected: Board pin '{pin}' is already used by "
                    f"peripheral(s): {', '.join(board_pin_usage[pin])}. "
                    f"Cannot reuse for peripheral '{peripheral_name}'.",
                    "PinConflictError"
                )
            else:
                board_pin_usage.setdefault(pin, []).append(peripheral_name)


def validate_i2c_address_uniqueness(connections: List) -> None:
    """
    Validate Safety-I2C-Address-Unique property.
    
    From SEMANTICS.md Section 6.7:
        Inv-I2C-Address: On the same I2C bus, all slave addresses must be unique
    """
    i2c_addresses: Dict[int, List[str]] = {}
    
    for connection in connections:
        for ioconn in connection.ioConns:
            if ioconn.__class__.__name__ == 'I2CConnection':
                addr = ioconn.slaveAddr
                peripheral_name = connection.peripheral.name
                
                if addr in i2c_addresses:
                    raise_validation_error(
                        connection,
                        f"I2C address conflict: Address 0x{addr:02X} is already used by "
                        f"peripheral(s): {', '.join(i2c_addresses[addr])}. "
                        f"Cannot reuse for peripheral '{peripheral_name}'.",
                        "I2CAddressConflictError"
                    )
                else:
                    i2c_addresses.setdefault(addr, []).append(peripheral_name)


def validate_voltage_limits(model) -> None:
    """
    Validate Safety-Voltage-Limits property.
    
    From SEMANTICS.md Section 8.1:
        Safety-Voltage-Limits: ∀k ∈ connections, p = k.peripheral.
            voltage(p) ≤ p.vcc.toVolts()
    """
    for connection in model.connections:
        peripheral = connection.peripheral.ref
        peripheral_vcc = parse_voltage(peripheral.vcc)
        
        if peripheral_vcc is None:
            continue
        
        # Check if any power connections exceed peripheral's VCC rating
        for pconn in connection.powerConns:
            board_pin = next((p for p in model.components.board.pins 
                            if p.name == pconn.boardPin), None)
            if board_pin and hasattr(board_pin, 'ptype'):
                board_voltage = parse_voltage(board_pin.ptype)
                if board_voltage and board_voltage > peripheral_vcc + 0.5:
                    raise_validation_error(
                        connection,
                        f"Voltage limit exceeded: Board pin {pconn.boardPin} provides "
                        f"{board_voltage}V but peripheral {peripheral.name} is rated for "
                        f"{peripheral_vcc}V maximum.",
                        "VoltageLimitError"
                    )

# ============================================================================
# Well-Formedness Validation
# ============================================================================

def validate_all_peripherals_connected(model) -> None:
    """
    Validate WF-All-Peripherals-Connected.
    
    From SEMANTICS.md Section 8.4:
        ∀p ∈ components.peripherals. ∃k ∈ connections. k.peripheral = p
    """
    connected_peripherals = {conn.peripheral.name for conn in model.connections}
    all_peripherals = {p.name for p in model.components.peripherals}
    
    unconnected = all_peripherals - connected_peripherals
    
    if unconnected:
        raise_validation_error(
            model,
            f"Unconnected peripherals detected: {', '.join(unconnected)}. "
            f"All peripherals must have at least one connection defined.",
            "UnconnectedPeripheralError"
        )


def validate_broker_requirements(model) -> None:
    """
    Validate Inv-Broker-Connection.
    
    From SEMANTICS.md Section 6.7:
        (∃k. k.endpoint.type ∈ {Publisher, Subscriber}) ⇒ (broker ≠ None)
    """
    has_endpoint = any(
        hasattr(conn, 'endpoint') and conn.endpoint is not None
        for conn in model.connections
    )
    
    if has_endpoint and not hasattr(model, 'broker'):
        raise_validation_error(
            model,
            "Broker configuration required: One or more connections define endpoints "
            "(Publisher/Subscriber), but no broker is configured in the model.",
            "MissingBrokerError"
        )
