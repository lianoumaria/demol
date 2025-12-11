"""Model-to-Text transformation for Raspberry Pi devices.

This module provides functionality to transform DeMoL device models into
Python code for Raspberry Pi, including sensor/actuator classes and MQTT
publisher/subscriber processes.
"""

import os
import warnings
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

import jinja2

from demol.definitions import TEMPLATES_RPI, REPO_PATH
from demol.lang import build_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeripheralTemplateMapper:
    """Maps peripheral types to their corresponding Jinja2 templates."""
    
    @classmethod
    def get_template(cls, peripheral_ref) -> Optional[str]:
        """Get template name for a peripheral from its templates section.
        
        Args:
            peripheral_ref: Reference to the peripheral object (has .name and .templates)
            
        Returns:
            Template filename for raspbian OS, or None if not found
        """
        # Check peripheral's templates section for raspbian
        if hasattr(peripheral_ref, 'templates') and peripheral_ref.templates:
            for template_mapping in peripheral_ref.templates:
                if template_mapping.os == 'raspbian':
                    return template_mapping.template
        
        # No template found
        logger.warning(
            f"No raspbian template found for peripheral '{peripheral_ref.name}'. "
            f"Please add a templates section with raspbian mapping to the peripheral model."
        )
        return None


class UnitConverter:
    """Utility class for unit conversions."""
    
    FREQUENCY_TO_HZ = {
        "ghz": 1_000_000_000,
        "mhz": 1_000_000,
        "khz": 1_000,
        "hz": 1,
    }
    
    DISTANCE_TO_CM = {
        "m": 0.01,
        "cm": 1,
        "mm": 10,
    }
    
    @classmethod
    def convert_frequency(cls, value: float, unit: str) -> float:
        """Convert frequency to Hz."""
        multiplier = cls.FREQUENCY_TO_HZ.get(unit.lower(), 1)
        return value * multiplier
    
    @classmethod
    def convert_distance(cls, value: float, unit: str) -> float:
        """Convert distance to cm."""
        multiplier = cls.DISTANCE_TO_CM.get(unit.lower(), 1)
        return value * multiplier


class DeviceModelExtractor:
    """Extracts information from DeMoL device models."""
    
    def __init__(self, device_model):
        """Initialize extractor with device model.
        
        Args:
            device_model: Parsed DeMoL device model
        """
        self.device_model = device_model
        self.broker_config: Dict[str, Any] = {}
        self.peripherals: List[Dict[str, Any]] = []
    
    def extract(self) -> None:
        """Extract all information from the device model."""
        self._extract_broker_config()
        self._extract_peripherals()
    
    def _extract_broker_config(self) -> None:
        """Extract broker configuration."""
        broker = self.device_model.broker
        
        if type(broker).__name__ != "MQTTBroker":
            raise TypeError(
                "This transformation does not support other Broker types than MQTTBroker."
            )
        
        self.broker_config = {
            "host": broker.host,
            "port": broker.port,
            "ssl": getattr(broker, "ssl", False),
            "username": "",
            "password": "",
        }
        
        # Extract authentication
        auth_type = type(broker.auth).__name__
        
        if auth_type == "AuthPlain":
            self.broker_config["username"] = getattr(broker.auth, "username", "")
            self.broker_config["password"] = getattr(broker.auth, "password", "")
        elif auth_type in ("AuthCert", "AuthApiKey"):
            raise TypeError(
                "This transformation uses commlib-py library and only supports "
                "plain authentication for MQTTBroker."
            )
        else:
            # Warn about missing authentication for remote brokers
            if (self.broker_config["host"] != "localhost" and 
                not (self.broker_config["username"] and self.broker_config["password"])):
                warnings.warn(
                    "You are using a remote broker without authentication. "
                    "This is not secure. Add username and password to your .dev file."
                )
    
    def _extract_peripherals(self) -> None:
        """Extract peripheral configurations."""
        for conn in self.device_model.connections:
            # Extract pins first to get bus information
            pins = self._extract_pins(conn.dataConns)
            
            peripheral_info = {
                "instance": conn.peripheral.name,
                "name": conn.peripheral.ref.name,
                "class": conn.peripheral.ref.type,
                "type": type(conn.peripheral.ref).__name__,
                "peripheral_ref": conn.peripheral.ref,  # Pass the full peripheral reference
                "board_ref": self.device_model.components.board,  # Pass the board reference
                "pins": pins,
                "attributes": self._extract_attributes(conn.peripheral.ref.attributes),
                "topic": conn.remote,
            }
            
            # Add bus information to top level for easy access in templates
            if "i2c_bus" in pins:
                peripheral_info["i2c_bus"] = pins["i2c_bus"]
            if "spi_bus" in pins:
                peripheral_info["spi_bus"] = pins["spi_bus"]
            if "uart_port" in pins:
                peripheral_info["uart_port"] = pins["uart_port"]
            
            # Apply settings (override attributes)
            self._apply_settings(peripheral_info["attributes"], conn.settings)
            
            self.peripherals.append(peripheral_info)
    
    def _extract_pins(self, data_conns) -> Dict[str, Any]:
        """Extract pin mappings from data connections."""
        pins = {}
        
        # Get board reference to access pin definitions
        board = self.device_model.components.board
        board_pins_map = {pin.name: pin for pin in board.pins}
        
        for data_conn in data_conns:
            conn_type = data_conn.type
            conn_name = None
            
            # Extract connection name if provided
            for prop in data_conn.props:
                if prop.name == "name":
                    conn_name = prop.value
                    break
            
            if conn_type == "gpio":
                # Extract GPIO properties
                gpio_props = {}
                for prop in data_conn.props:
                    if prop.name in ["mode", "pullup", "pulldown"]:
                        gpio_props[prop.name] = prop.value
                
                # Handle pins based on peripheral pin name
                for pin_map in data_conn.pins:
                    key = pin_map.peripheralPin
                    pins[key] = pin_map.boardPin
                    pins[f"{key}_props"] = gpio_props
                    
            elif conn_type == "spi":
                # Extract SPI properties
                spi_props = {}
                for prop in data_conn.props:
                    if prop.name in ["bus_speed", "mode"]:
                        spi_props[prop.name] = prop.value
                
                for pin_map in data_conn.pins:
                    board_pin = board_pins_map.get(pin_map.boardPin)
                    
                    if pin_map.function == "mosi":
                        pins["mosi"] = pin_map.boardPin
                        # Extract SPI bus from board pin's function definition
                        if board_pin:
                            pins["spi_bus"] = self._get_bus_from_pin(board_pin, "mosi")
                    elif pin_map.function == "miso":
                        pins["miso"] = pin_map.boardPin
                    elif pin_map.function == "sck":
                        pins["sck"] = pin_map.boardPin
                    elif pin_map.function == "cs":
                        pins["cs"] = pin_map.boardPin
                    pins[f"{pin_map.function}_props"] = spi_props
                
            elif conn_type == "i2c":
                # Extract I2C properties
                i2c_props = {}
                for prop in data_conn.props:
                    if prop.name in ["slave_address", "bus_speed"]:
                        i2c_props[prop.name] = prop.value

                for pin_map in data_conn.pins:
                    board_pin = board_pins_map.get(pin_map.boardPin)
                    
                    if pin_map.function == "sda":
                        pins["sda"] = pin_map.boardPin
                        # Extract I2C bus from board pin's function definition
                        if board_pin:
                            pins["i2c_bus"] = self._get_bus_from_pin(board_pin, "sda")
                    elif pin_map.function == "scl":
                        pins["scl"] = pin_map.boardPin
                    pins[f"{pin_map.function}_props"] = i2c_props
                
            elif conn_type == "uart":
                # Extract UART properties
                uart_props = {}
                for prop in data_conn.props:
                    if prop.name in ["baudrate", "parity", "stop_bits", "data_bits"]:
                        uart_props[prop.name] = prop.value

                for pin_map in data_conn.pins:
                    board_pin = board_pins_map.get(pin_map.boardPin)
                    
                    if pin_map.function == "tx":
                        pins["tx"] = pin_map.boardPin
                        # Extract UART port from board pin's function definition
                        if board_pin:
                            pins["uart_port"] = self._get_bus_from_pin(board_pin, "tx")
                    elif pin_map.function == "rx":
                        pins["rx"] = pin_map.boardPin
                    pins[f"{pin_map.function}_props"] = uart_props
                
            else:
                raise TypeError(f"Not a valid IO Connection Type: {conn_type}")
        
        return pins
    
    def _get_bus_from_pin(self, board_pin, function_type: str) -> int:
        """Extract bus number from board pin's function definition.
        
        Args:
            board_pin: Board pin object with funcs attribute
            function_type: Type of function to look for (e.g., 'sda', 'mosi', 'tx')
            
        Returns:
            Bus number as integer, defaults to 0 if not found
        """
        if hasattr(board_pin, 'funcs'):
            for func in board_pin.funcs:
                # Check if this function matches the type we're looking for
                if hasattr(func, 'ptype') and func.ptype == function_type:
                    # Return the bus number from the function definition
                    if hasattr(func, 'bus'):
                        return func.bus
        return 0
    
    def _extract_attributes(self, attributes) -> Dict[str, Any]:
        """Extract attributes from peripheral."""
        result = {}
        
        for attr in attributes:
            attr_type = type(attr).__name__
            
            if attr_type == "DictAttribute":
                result[attr.name] = self._convert_dict_attribute(attr)
            else:
                result[attr.name] = attr.default
        
        return result
    
    def _convert_dict_attribute(self, attribute) -> Dict[str, Any]:
        """Recursively convert DictAttribute to dict."""
        result = {}
        
        for item in attribute.items:
            item_type = type(item).__name__
            
            if item_type in ("DictAttribute", "DictSetting"):
                result[item.name] = self._convert_dict_attribute(item)
            else:
                result[item.name] = item.default
        
        return result
    
    def _apply_settings(self, attributes: Dict[str, Any], settings) -> None:
        """Apply settings to attributes (in-place modification)."""
        for setting in settings:
            setting_type = type(setting).__name__
            
            if setting_type == "DictSetting":
                attributes[setting.name] = self._convert_dict_attribute(setting)
            else:
                attributes[setting.name] = setting.default

from .base_generator import BaseCodeGenerator


class RPiCodeGenerator(BaseCodeGenerator):
    """Generates Raspberry Pi code from device model."""
    
    def __init__(self, device_model, output_dir: Path):
        """Initialize code generator with device model.
        
        Args:
            device_model: Parsed textX device model
            output_dir: Output directory for generated code
        """
        super().__init__(device_model, output_dir)
        self.env = self.setup_template_environment()
    
    def setup_template_environment(self) -> jinja2.Environment:
        """Setup Jinja2 environment with RPI-specific templates.
        
        Returns:
            Configured Jinja2 Environment
        """
        fsloader = jinja2.FileSystemLoader(TEMPLATES_RPI)
        return jinja2.Environment(loader=fsloader)
    
    
    def build_template_context(self, connection) -> Dict[str, Any]:
        """Build structured context dictionary by querying model.
        
        Args:
            connection: Connection object from device model
            
        Returns:
            Structured context dictionary for templates
        """
        # Query model for all needed information
        peripheral_ref = connection.peripheral.ref
        board = self.get_board()
        broker_config = self.get_broker_config()
        pins = self.get_pin_mappings(connection.dataConns, board)
        attributes = self.get_peripheral_attributes(peripheral_ref)
        
        # Apply settings to override attributes
        self._apply_settings(attributes, connection.settings)
        
        # Build base context
        context = {
            "name": peripheral_ref.name,
            "instance": connection.peripheral.name,
            "type": type(peripheral_ref).__name__,
            "class": peripheral_ref.type,
            "board": board,
            "peripheral": peripheral_ref,
            "broker": broker_config,
            "conn": {},
            "attributes": attributes
        }
        
        # Build structured connection info
        context["conn"] = self._build_conn_info(pins, board)
        
        return context
    
    def _build_conn_info(self, pins: Dict[str, Any], board) -> Dict[str, Any]:
        """Build structured connection information dictionary.
        
        Args:
            pins: Pin mappings dictionary
            board: Board object
            
        Returns:
            Structured connection dictionary organized by type
        """
        conn = {}
        board_pins_map = {pin.name: pin for pin in board.pins}
        
        # GPIO connection
        gpio_pins = {}
        gpio_props = {}
        for key, value in pins.items():
            if key.endswith("_props") and "gpio" in key.lower():
                gpio_props.update(value if isinstance(value, dict) else {})
            elif not key.endswith("_props") and key not in ["sda", "scl", "mosi", "miso", "sck", "cs", "tx", "rx", "i2c_bus", "spi_bus", "uart_port"]:
                # Add pin name and id
                board_pin = board_pins_map.get(value)
                gpio_pins[key] = {
                    "name": value,
                    "id": board_pin.number if board_pin else None
                }
        
        if gpio_pins or gpio_props:
            conn["gpio"] = {**gpio_props, "pins": gpio_pins}
        
        # I2C connection
        if "sda" in pins or "scl" in pins:
            i2c_pins = {}
            i2c_props = {}
            if "i2c_bus" in pins:
                i2c_props["bus"] = pins["i2c_bus"]
            
            # Add SDA pin with id
            if "sda" in pins:
                board_pin = board_pins_map.get(pins["sda"])
                i2c_pins["sda"] = {
                    "name": pins["sda"],
                    "id": board_pin.number if board_pin else None
                }
            
            # Add SCL pin with id
            if "scl" in pins:
                board_pin = board_pins_map.get(pins["scl"])
                i2c_pins["scl"] = {
                    "name": pins["scl"],
                    "id": board_pin.number if board_pin else None
                }
            
            # Add I2C properties
            for key, value in pins.items():
                if "sda_props" in key or "scl_props" in key:
                    i2c_props.update(value if isinstance(value, dict) else {})
            conn["i2c"] = {**i2c_props, "pins": i2c_pins}
        
        # SPI connection
        if "mosi" in pins or "miso" in pins or "sck" in pins:
            spi_pins = {}
            spi_props = {}
            if "spi_bus" in pins:
                spi_props["bus"] = pins["spi_bus"]
            
            # Add pin mappings with ids
            for pin_name in ["mosi", "miso", "sck", "cs"]:
                if pin_name in pins:
                    board_pin = board_pins_map.get(pins[pin_name])
                    spi_pins[pin_name] = {
                        "name": pins[pin_name],
                        "id": board_pin.number if board_pin else None
                    }
            
            # Add SPI properties
            for key, value in pins.items():
                if any(x in key for x in ["mosi_props", "miso_props", "sck_props", "cs_props"]):
                    spi_props.update(value if isinstance(value, dict) else {})
            conn["spi"] = {**spi_props, "pins": spi_pins}
        
        # UART connection
        if "tx" in pins or "rx" in pins:
            uart_pins = {}
            uart_props = {}
            if "uart_port" in pins:
                uart_props["port"] = pins["uart_port"]
            
            # Add TX pin with id
            if "tx" in pins:
                board_pin = board_pins_map.get(pins["tx"])
                uart_pins["tx"] = {
                    "name": pins["tx"],
                    "id": board_pin.number if board_pin else None
                }
            
            # Add RX pin with id
            if "rx" in pins:
                board_pin = board_pins_map.get(pins["rx"])
                uart_pins["rx"] = {
                    "name": pins["rx"],
                    "id": board_pin.number if board_pin else None
                }
            
            # Add UART properties
            for key, value in pins.items():
                if "tx_props" in key or "rx_props" in key:
                    uart_props.update(value if isinstance(value, dict) else {})
            conn["uart"] = {**uart_props, "pins": uart_pins}
        
        return conn
    
    def generate(self) -> None:
        """Generate all RPI code from device model."""
        logger.info("Generating RPI code...")
        self.generate_peripheral_classes()
        self.generate_common()
        self.generate_messages()
        logger.info("Code generation complete!")
    
    def generate_peripheral_classes(self) -> None:
        """Generate peripheral class files by querying model."""
        for connection in self.get_connections():
            self._generate_peripheral_class(connection)
    
    def _generate_peripheral_class(self, connection) -> None:
        """Generate a single peripheral class file.
        
        Args:
            connection: Connection object from device model
        """
        peripheral_ref = connection.peripheral.ref
        
        # Get template using peripheral reference
        template_name = PeripheralTemplateMapper.get_template(peripheral_ref)
        
        if not template_name:
            logger.warning(
                f"Skipping peripheral {connection.peripheral.name}: no template available"
            )
            return
        
        template = self.env.get_template(template_name)
        
        # Build context by querying model
        context = self.build_template_context(connection)
        
        # Render and write
        output = template.render(**context)
        output_path = self.output_dir / f"{connection.peripheral.name}.py"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        
        logger.info(f"Generated peripheral class: {output_path}")
    
    def generate_mqtt_processes(
        self,
        peripherals: List[Dict[str, Any]],
        broker_config: Dict[str, Any]) -> None:
        """Generate MQTT publisher/subscriber processes.
        
        Args:
            peripherals: List of peripheral configurations
            broker_config: Broker configuration
        """
        for peripheral in peripherals:
            self._generate_mqtt_process(peripheral, broker_config)
        
        # Generate messages module
        self._generate_messages_module()
    
    def _generate_mqtt_process(
        self,
        peripheral: Dict[str, Any],
        broker_config: Dict[str, Any]) -> None:
        """Generate MQTT process files for a peripheral."""
        ptype = peripheral["type"]
        instance = peripheral["instance"]
        
        # Determine if sensor or actuator
        if ptype == "Sensor":
            self._generate_sensor_mqtt(peripheral, broker_config)
        elif ptype == "Actuator":
            self._generate_actuator_mqtt(peripheral, broker_config)
    
    def _generate_sensor_mqtt(
        self,
        sensor: Dict[str, Any],
        broker_config: Dict[str, Any]) -> None:
        """Generate MQTT files for sensor."""
        context = {
            "sensor_name": sensor["instance"],
            "sensor_type": sensor["name"],
            "sensorMsg": sensor["type"],
            "topic": sensor["topic"],
            **broker_config,
            **sensor["attributes"],
        }
        
        # Publisher
        template = self.env.get_template("MQTTSensorPublisher.py.tmpl")
        self._write_template(
            template,
            context,
            self.output_dir / f"{sensor['instance']}publisher.py"
        )
    
    def _generate_actuator_mqtt(
        self,
        actuator: Dict[str, Any],
        broker_config: Dict[str, Any]) -> None:
        """Generate MQTT files for actuator."""
        context = {
            "actuator_name": actuator["instance"],
            "actuator_type": actuator["name"],
            "actuatorMsg": actuator["type"],
            "topic": actuator["topic"],
            **broker_config,
            **actuator["attributes"],
        }
        
        # Subscriber
        template = self.env.get_template("MQTTActuatorSubscriber.py.tmpl")
        self._write_template(
            template,
            context,
            self.output_dir / f"{actuator['instance']}subscriber.py"
        )
    
    def generate_messages(self) -> None:
        """Generate MQTT messages module."""
        template = self.env.get_template("msg.py.tmpl")
        self._write_template(
            template,
            {},
            self.output_dir / "msg.py"
        )
        
    def generate_common(self) -> None:
        """Generate common module."""
        template = self.env.get_template("common.py.tmpl")
        self._write_template(
            template,
            {},
            self.output_dir / "common.py"
        )
    
    def _write_template(
        self,
        template: jinja2.Template,
        context: Dict[str, Any],
        output_path: Path) -> None:
        """Render template and write to file.
        
        Args:
            template: Jinja2 template
            context: Template context
            output_path: Output file path
        """
        output = template.render(**context)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        
        logger.debug(f"Generated: {output_path}")


def transform_device_model(device_model_path: str, output_dir: str) -> None:
    """Transform a DeMoL device model to Raspberry Pi code.
    
    Args:
        device_model_path: Path to .dev model file (relative to examples/)
        output_dir: Output directory (relative to REPO_PATH)
    """
    # Build paths
    model_path = Path(device_model_path)
    output_path = Path('.') / output_dir
    
    logger.info(f"Transforming: {model_path}")
    
    # Parse device model
    device_model = build_model(str(model_path))
    
    # Generate code using new architecture
    generator = RPiCodeGenerator(device_model, output_path)
    generator.generate()
    
    logger.info("Transformation complete!")


def main(dev_model: str, output_dir: str) -> None:
    """Main entry point for the transformation.
    
    Args:
        dev_model: Path to device model file
        output_dir: Output directory for generated code
    """
    transform_device_model(dev_model, output_dir)