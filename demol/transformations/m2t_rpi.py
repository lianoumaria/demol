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
    
    TEMPLATE_MAP = {
        "SRF05": "DistanceSensor.py.tmpl",
        "HCSR04": "DistanceSensor.py.tmpl",
        "VL53L1X": "ToFSensor.py.tmpl",
        "HW006": "TrackerSensor.py.tmpl",
        "TCRT5000": "TrackerSensor.py.tmpl",
        "BME680": "EnvSensor.py.tmpl",
        "TFMini": "TFMiniSensor.py.tmpl",
        "ADCDifferentialPi": "ADCDifferentialPi.py.tmpl",
        "WS2812": "WS2812.py.tmpl",
        "PCA9685": "PCA9685.py.tmpl",
    }
    
    @classmethod
    def get_template(cls, peripheral_type: str, custom_template: Optional[str] = None) -> str:
        """Get template name for a peripheral type.
        
        Args:
            peripheral_type: Type of the peripheral
            custom_template: Optional custom template path
            
        Returns:
            Template filename
        """
        if custom_template:
            return custom_template
        
        template = cls.TEMPLATE_MAP.get(peripheral_type)
        if not template:
            logger.warning(f"No template found for peripheral type: {peripheral_type}")
        return template


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
            peripheral_info = {
                "ref_name": conn.peripheral.name,
                "real_name": conn.peripheral.ref.name,
                "type": type(conn.peripheral.ref).__name__,
                "pins": self._extract_pins(conn.ioConns),
                "attributes": self._extract_attributes(conn.peripheral.ref.attributes),
                "topic": conn.endpoint.topic,
                "message": conn.peripheral.ref.operational.msg,
                "custom_template": getattr(conn.peripheral.ref, "piTpl", None) or None,
            }
            
            # Apply settings (override attributes)
            self._apply_settings(peripheral_info["attributes"], conn.settings)
            
            self.peripherals.append(peripheral_info)
    
    def _extract_pins(self, io_conns) -> Dict[str, Any]:
        """Extract pin configurations from IO connections."""
        pins = {}
        
        for io_conn in io_conns:
            conn_type = io_conn.type
            
            if conn_type == "gpio":
                # Handle special GPIO names
                if io_conn.name == "trigger":
                    pins["trigger"] = io_conn.pinConn.boardPin
                elif io_conn.name == "echo":
                    pins["echo"] = io_conn.pinConn.boardPin
                else:
                    pins["gpio"] = io_conn.pinConn.boardPin
                    
            elif conn_type == "spi":
                pins.update({
                    "mosi": io_conn.mosi.boardPin,
                    "miso": io_conn.miso.boardPin,
                    "sck": io_conn.sck.boardPin.clock,
                    "cs": io_conn.cs.boardPin,
                })
                
            elif conn_type == "i2c":
                pins.update({
                    "sda": io_conn.sda.boardPin,
                    "scl": io_conn.scl.boardPin,
                    "slaveAddr": io_conn.slaveAddr,
                })
                
            elif conn_type == "uart":
                pins.update({
                    "baudrate": io_conn.baudrate,
                    "tx": io_conn.tx.boardPin,
                    "rx": io_conn.rx.boardPin,
                })
                
            else:
                raise TypeError(f"Not a valid IO Connection Type: {conn_type}")
        
        return pins
    
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
    
    def _extract_constraints(self, constraints) -> Dict[str, float]:
        """Extract and normalize constraints."""
        result = {}
        
        for constraint in constraints:
            if constraint.name == "max_frequency":
                result[constraint.name] = UnitConverter.convert_frequency(
                    constraint.value, constraint.unit
                )
            else:
                # Assume distance constraint
                result[constraint.name] = UnitConverter.convert_distance(
                    constraint.value, constraint.unit
                )
        
        return result
    
    def _apply_settings(self, attributes: Dict[str, Any], settings) -> None:
        """Apply settings to attributes (in-place modification)."""
        for setting in settings:
            setting_type = type(setting).__name__
            
            if setting_type == "DictSetting":
                attributes[setting.name] = self._convert_dict_attribute(setting)
            else:
                attributes[setting.name] = setting.default


class RPiCodeGenerator:
    """Generates Raspberry Pi code from device model."""
    
    def __init__(self, output_dir: Path):
        """Initialize code generator.
        
        Args:
            output_dir: Output directory for generated code
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        fsloader = jinja2.FileSystemLoader(TEMPLATES_RPI)
        self.env = jinja2.Environment(loader=fsloader)
    
    def generate_peripheral_classes(
        self, 
        peripherals: List[Dict[str, Any]]
    ) -> None:
        """Generate peripheral class files.
        
        Args:
            peripherals: List of peripheral configurations
        """
        for peripheral in peripherals:
            self._generate_peripheral_class(peripheral)
    
    def _generate_peripheral_class(self, peripheral: Dict[str, Any]) -> None:
        """Generate a single peripheral class file."""
        # Get template
        template_name = PeripheralTemplateMapper.get_template(
            peripheral["real_name"],
            peripheral.get("custom_template")
        )
        
        if not template_name:
            logger.warning(
                f"Skipping peripheral {peripheral['ref_name']}: no template available"
            )
            return
        
        template = self.env.get_template(template_name)
        
        # Prepare template context
        context = {
            f"{peripheral['type'].lower()}_type": peripheral["real_name"],
        }
        context.update(peripheral["pins"])
        context.update(peripheral["attributes"])
        
        # Render and write
        output = template.render(**context)
        output_path = self.output_dir / f"{peripheral['ref_name']}.py"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        
        logger.info(f"Generated peripheral class: {output_path}")
    
    def generate_mqtt_processes(
        self,
        peripherals: List[Dict[str, Any]],
        broker_config: Dict[str, Any]
    ) -> None:
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
        broker_config: Dict[str, Any]
    ) -> None:
        """Generate MQTT process files for a peripheral."""
        ptype = peripheral["type"]
        ref_name = peripheral["ref_name"]
        
        # Determine if sensor or actuator
        if ptype == "Sensor":
            self._generate_sensor_mqtt(peripheral, broker_config)
        elif ptype == "Actuator":
            self._generate_actuator_mqtt(peripheral, broker_config)
    
    def _generate_sensor_mqtt(
        self,
        sensor: Dict[str, Any],
        broker_config: Dict[str, Any]
    ) -> None:
        """Generate MQTT files for sensor."""
        context = {
            "sensor_name": sensor["ref_name"],
            "sensor_type": sensor["real_name"],
            "sensorMsg": sensor["message"],
            "topic": sensor["topic"],
            **broker_config,
            **sensor["attributes"],
        }
        
        # Publisher
        template = self.env.get_template("MQTTSensorPublisher.py.tmpl")
        self._write_template(
            template,
            context,
            self.output_dir / f"{sensor['ref_name']}publisher.py"
        )
        
        # Subscriber
        template = self.env.get_template("MQTTSensorSubscriber.py.tmpl")
        self._write_template(
            template,
            context,
            self.output_dir / f"{sensor['ref_name']}subscriber.py"
        )
    
    def _generate_actuator_mqtt(
        self,
        actuator: Dict[str, Any],
        broker_config: Dict[str, Any]
    ) -> None:
        """Generate MQTT files for actuator."""
        context = {
            "actuator_name": actuator["ref_name"],
            "actuator_type": actuator["real_name"],
            "actuatorMsg": actuator["message"],
            "topic": actuator["topic"],
            **broker_config,
            **actuator["attributes"],
        }
        
        # Publisher
        template = self.env.get_template("MQTTActuatorPublisher.py.tmpl")
        self._write_template(
            template,
            context,
            self.output_dir / f"{actuator['ref_name']}publisher.py"
        )
        
        # Subscriber
        template = self.env.get_template("MQTTActuatorSubscriber.py.tmpl")
        self._write_template(
            template,
            context,
            self.output_dir / f"{actuator['ref_name']}subscriber.py"
        )
    
    def _generate_messages_module(self) -> None:
        """Generate MQTT messages module."""
        template = self.env.get_template("MQTTMessages.py.tmpl")
        self._write_template(
            template,
            {},
            self.output_dir / "MQTTMessages.py"
        )
    
    def _write_template(
        self,
        template: jinja2.Template,
        context: Dict[str, Any],
        output_path: Path
    ) -> None:
        """Render template and write to file.
        
        Args:
            template: Jinja2 template
            context: Template context
            output_path: Output file path
        """
        output = template.render(**context)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        
        logger.info(f"Generated: {output_path}")


def transform_device_model(device_model_path: str, output_dir: str) -> None:
    """Transform a DeMoL device model to Raspberry Pi code.
    
    Args:
        device_model_path: Path to .dev model file (relative to examples/)
        output_dir: Output directory (relative to REPO_PATH)
    """
    # Build paths
    model_path = Path(REPO_PATH) / "examples" / device_model_path
    output_path = Path(REPO_PATH) / output_dir
    
    logger.info(f"Loading device model from: {model_path}")
    
    # Parse device model
    device_model = build_model(str(model_path))
    
    # Extract information
    logger.info("Extracting device model information...")
    extractor = DeviceModelExtractor(device_model)
    extractor.extract()
    
    # Log extracted info
    logger.info(f"Found {len(extractor.peripherals)} peripheral(s)")
    logger.info(f"Broker: {extractor.broker_config['host']}:{extractor.broker_config['port']}")
    
    # Generate code
    logger.info(f"Generating code to: {output_path}")
    generator = RPiCodeGenerator(output_path)
    
    logger.info("Generating peripheral classes...")
    generator.generate_peripheral_classes(extractor.peripherals)
    
    logger.info("Generating MQTT processes...")
    generator.generate_mqtt_processes(extractor.peripherals, extractor.broker_config)
    
    logger.info("Code generation complete!")


def main(dev_model: str, output_dir: str) -> None:
    """Main entry point for the transformation.
    
    Args:
        dev_model: Path to device model file
        output_dir: Output directory for generated code
    """
    transform_device_model(dev_model, output_dir)


if __name__ == "__main__":
    # Use forward slashes for cross-platform compatibility
    main("ThesisExamples/ThesisExample.dev", "rpi5_out/ThesisExample")