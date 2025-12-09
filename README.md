<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

![image](https://github.com/robotics-4-all/demol/blob/main/assets/demol_logo.png)


<em></em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/Redis-FF4438.svg?style=default&logo=Redis&logoColor=white" alt="Redis">
<img src="https://img.shields.io/badge/MQTT-606?logo=mqtt&logoColor=fff&style=plastic" alt="MQTT">
<img src="https://img.shields.io/badge/RabbitMQ-F60?logo=rabbitmq&logoColor=fff&style=plastic" alt="RabbitMQ">
<br>
<img src="https://img.shields.io/badge/textX-2496ED.svg?style=default&logo=textx&logoColor=white" alt="textX">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/FastAPI-2496ED.svg?style=default&logo=FastAPI&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=default&logo=Docker&logoColor=white" alt="Docker">

</div>
<br>

---

# DeMoL - A DSL for modeling IoT Devices

## 📜 Table of Contents

- [DeMoL - A DSL for modeling IoT Devices](#demol---a-dsl-for-modeling-iot-devices)
  - [📜 Table of Contents](#-table-of-contents)
  - [📖 Overview](#-overview)
  - [👾 Features](#-features)
  - [🚀 Getting Started](#-getting-started)
    - [🔖 Prerequisites](#-prerequisites)
    - [🛠️ Installation](#️-installation)
      - [Install from source](#install-from-source)
  - [📚 Language Reference](#-language-reference)
    - [Grammar Structure](#grammar-structure)
    - [Core Concepts](#core-concepts)
    - [Device Model Structure](#device-model-structure)
    - [Hardware Components](#hardware-components)
    - [Connections](#connections)
    - [Message Brokers](#message-brokers)
    - [Complete Example](#complete-example)
  - [🔌 Supported Sensors \u0026 Actuators](#-supported-sensors--actuators)
  - [📐 Formal Semantics](#-formal-semantics)
  - [🔍 Semantic Validations](#-semantic-validations)
  - [🔧 Usage](#-usage)
    - [CLI](#cli)
    - [Model Validation](#model-validation)
    - [Code Generation](#code-generation)
    - [REST API](#rest-api)
  - [📜 License](#-license)
  - [🎩 Acknowledgments](#-acknowledgments)
  - [🌟 Star History](#-star-history)

## 📖 Overview

Device Modeling Language (DeMoL) - A DSL for modeling IoT devices.

Enables automated source code generation currently for RaspberryPi and RiotOS.

...

## 👾 Features

|      |        Feature        | Summary                                                                                                                                                                                                                                                                     |
| :--- | :-------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ⚙️    | **Protocol-Agnostic** | <ul><li>Protocol/Transport-level abstraction</li><li>Currently supports Redis, AMQP and MQTT</li></ul>                                                                                                                                                                      |
| 📄    |   **Documentation**   | <ul><li>Rich documentation in various formats (YAML, TOML, Markdown)</li><li>Includes detailed installation commands for different package managers</li><li>Utilizes MkDocs for generating documentation</li></ul>                                                          |
| 🧩    |    **Modularity**     | <ul><li>Well-structured codebase with clear separation of concerns</li><li>Encourages code reusability and maintainability</li></ul>                                                                                                                                        |
| 📦    |   **Dependencies**    | <ul><li>Manages dependencies with Poetry and dependency lock files</li><li>Includes a variety of libraries for different functionalities</li><li>Dependency management with conda for environment setup</li><li>Dynamic imports of underlying transport libraries</li></ul> |

---

## 🚀 Getting Started

### 🔖 Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python 3.7+
- **Packages:** textX, jinja2
- **Package Manager:** Pip

### 🛠️ Installation

Download this repository and either use the CLI and the API of the DSL directly from source, or in docker container.

#### Install from source

1. Pull this repository locally

```sh
git clone https://github.com/lianoumaria/demol.git
```

2. Create a Virtual environment (Optional Step)

```sh
python -m venv venv && source ./venv/bin/activate
```

3. Install the DSL package in `develop` mode

```sh
python setup.py develop
```


## 📚 Language Reference

The DeMoL DSL is built using the [textX](http://textx.github.io/textX/) framework and provides a declarative approach to modeling IoT devices.

### Grammar Structure

The grammar is modular and split into **5 interconnected files** located in `demol/grammar/`:

| File               | Purpose                           | Key Concepts                        |
| ------------------ | --------------------------------- | ----------------------------------- |
| `device.tx`        | Main device model definition      | DeviceModel, Connection, Settings   |
| `component.tx`     | Board & peripheral hardware specs | Board, Sensor, Actuator, Pins       |
| `communication.tx` | Message broker configurations     | AMQPBroker, MQTTBroker, RedisBroker |
| `common.tx`        | Common utilities                  | FQN, Import, Comments               |
| `utils.tx`         | Additional utilities              | FQN handling, Keywords              |

### Core Concepts

The language is built around these fundamental concepts:

- **Device** - Complete IoT device definition with metadata and configuration
- **Board** - Microcontroller/SBC hardware (ESP32, Raspberry Pi, etc.)
- **Peripheral** - External sensors and actuators (BME680, SRF04, etc.)
- **Connection** - Defines how peripherals connect to boards (power + IO)
- **MessageBroker** - Communication infrastructure (MQTT, AMQP, Redis)
- **Network** - WiFi configuration

**File Extensions:**
- `.dev` - Device models (complete IoT device definitions)
- `.hwd` - Hardware component models (boards and peripherals)

### Device Model Structure

Every `.dev` file follows this structure:

```
Metadata
    name: "DeviceName"
    description: "Device description"
    author: "author_name"
    os: Raspbian  // or RiotOS
end

Network
    ssid: "WiFi_SSID"
    passwd: "password"
    address: 192.168.1.100  // optional
    channel: "6"  // optional
end

Broker<MQTT> BrokerName
    host: "mqtt.example.com"
    port: 1883
    ssl: False
    auth:
        username: "user"
        password: "pass"
end

Components
    board: BoardModelName
    peripherals:
        - PeripheralModel(InstanceName1)
        - PeripheralModel(InstanceName2)
end

Connection
    peripheral: InstanceName1
    powerConnections:
        - board_pin -- peripheral_pin
    ioConnections:
        - type: gpio
          pin: board_pin -- peripheral_pin
    endpoint:
        topic: "device/sensor/topic"
        type: Publisher
    settings:
        - setting_name: type = value
end
```

#### Metadata Block

Describes the device and target platform:

```
Metadata
    name: "SmartSensor"
    description: "Environmental monitoring sensor"
    author: "developer_name"
    os: Raspbian  // Raspbian or RiotOS
end
```

**Target Operating Systems:**
- `Raspbian` - For Raspberry Pi devices
- `RiotOS` - For embedded systems (ESP32, ESP8266, etc.)

#### Network Configuration

WiFi network settings:

```
Network
    ssid: "IoT_Network"
    passwd: "secure_password"
    address: 192.168.1.50  // optional static IP
    channel: "11"  // optional WiFi channel
end
```

#### Components

Specifies the hardware composition:

```
Components
    board: RaspberryPi_4B_4GB
    peripherals:
        - BME680(EnvSensor)
        - SonarSRF04(DistanceSensor)
        - WS2812(StatusLED)
end
```

**Features:**
- Board references are resolved from the global repository in `demol/builtin_models/boards/`
- Peripheral models are loaded from `demol/builtin_models/peripherals/`
- Supports multi-file imports using FQN (Fully Qualified Names)
- Named peripheral instances for easy reference in connections

### Hardware Components

#### Board Models

Boards are defined in `.hwd` files and describe microcontroller/SBC specifications using the `Board[Type] name` syntax:

```
Board[RPI] RaspberryPi_4B_4GB
    operational
        vcc: 5V
        memory:
            flash: 16 gb
            ram: 4 gb
        cpu:
            cpu_family: PiArmCortex
            max_freq: 1500 mhz
            fpu: true
        wifi:
            name: wifi_0
            freq: 2.4 ghz
        bluetooth: BT5
        ioVcc: 3V3
    end
    pins
        PPIN power_5v[5V] @ 2;
        PPIN gnd_1[GND] @ 6;
        DPIN p_21[gpio,sda-1] @ 40;
        DPIN p_22[gpio,scl-1] @ 38;
    end
end
```

**Board Types:** `RPI` (Raspberry Pi), `ESP` (ESP32/ESP8266), `ARDUINO`

**Pin Syntax:**
- `PPIN` - Power pins (VCC, GND)
- `DPIN` - Digital/IO pins with functions

**Pin Functions:** `gpio`, `adc`, `dac`, `pwm-<channel>`, `sda-<bus>`, `scl-<bus>`, `mosi-<bus>`, `miso-<bus>`, `sck-<bus>`, `cs-<bus>`, `tx-<bus>`, `rx-<bus>`

**Power Types:** `GND`, `3V3`, `5V`, `12V`

#### Peripheral Models (Sensors)

Sensors use the `Sensor[Type] name` syntax where Type indicates the sensor category and its message schema:

```
Sensor[Env] BME680
    operational
        vcc: 5V
        ioVcc: 3V3
        powerConsumption: 3 mW
        piTpl: "bme680"  // optional - RaspberryPi template
        riotTpl: "bme680"  // optional - RiotOS template
    end
    pins
        PPIN vcc[5V] @ 1;
        PPIN gnd[GND] @ 5;
        DPIN sda[sda-0] @ 2;
        DPIN scl[scl-0] @ 3;
    end
    attributes
        ATTR poll_period[int] = 10;
        ATTR humidity_oversample[int] = 2;
        ATTR temperature_oversample[int] = 8;
    end
end
```

**Available Sensor Types:** `Distance`, `Temperature`, `Humidity`, `Gas`, `Pressure`, `Env`, `AirQuality`, `Light`, `UV`, `Sound`, `Acceleration`, `Gyroscope`, `Magnetometer`, `IMU`, `Tracker`, `Proximity`, `Motion`, `Presence`, `ADC`, `Current`, `Voltage`, `Power`, `Flow`, `Level`, `Weight`, `Force`, `Vibration`, `Camera`, `RFID`, `Fingerprint`, `GPS`, `Color`

For complete sensor type documentation and message schemas, see **[SENSORS_ACTUATORS.md](SENSORS_ACTUATORS.md)**.

#### Peripheral Models (Actuators)

Actuators use the `Actuator[Type] name` syntax:

```
Actuator[ServoController] PCA9685
    operational
        vcc: 5V
        ioVcc: 5V
    end
    pins
        PPIN GND_1[GND] @ 1;
        DPIN SCL_1[scl-0] @ 2;
        DPIN SDA_1[sda-0] @ 3;
        PPIN VCC_1[5V] @ 4;
    end
    attributes
        ATTR num_servos[int] = 16;
        ATTR frequency[int] = 50;
    end
end
```

**Available Actuator Types:** `MotorController`, `ServoController`, `Relay`, `Switch`, `Led`, `LedArray`, `NeoPixel`, `Display`, `LCD`, `OLED`, `Buzzer`, `Speaker`, `Stepper`, `DCMotor`, `Pump`, `Valve`, `Heater`, `Cooler`, `Fan`

For complete actuator type documentation and command schemas, see **[SENSORS_ACTUATORS.md](SENSORS_ACTUATORS.md)**.

**Units:**
- **Memory:** `b`, `kb`, `mb`, `gb`
- **Frequency:** `hz`, `khz`, `mhz`, `ghz`
- **Distance:** `mm`, `cm`, `m`
- **Power:** `uW`, `mW`, `W`

### Connections

Connections define how peripherals connect to the board through power and IO pins:

#### GPIO Connection

```
Connection
    peripheral: DistanceSensor
    powerConnections:
        - gnd_1 -- gnd
        - power_5v -- vcc
    ioConnections:
        - type: gpio
          name: trigger  // optional
          pin: p_13 -- trigger
          input: False  // optional mode
          output: True
          pullup: False
          pulldown: False
          open_drain: False
        - type: gpio
          name: echo
          pin: p_14 -- echo
    endpoint:
        topic: "sensors/distance"
        type: Publisher
end
```

#### I2C Connection

```
Connection
    peripheral: EnvSensor
    powerConnections:
        - gnd_1 -- GND
        - power_5v -- VCC
    ioConnections:
        - type: i2c
          name: env_i2c  // optional
          slave_address: 0x76
          pins:
              sda: p_21 -- sda
              scl: p_22 -- scl
    endpoint:
        topic: "sensors/environment"
        type: Publisher
    settings:
        - poll_period: int = 5
        - enable_gas: bool = True
end
```

#### SPI Connection

```
Connection
    peripheral: DisplayModule
    powerConnections:
        - gnd_1 -- GND
        - power_3v3 -- VCC
    ioConnections:
        - type: spi
          name: display_spi  // optional
          pins:
              mosi: p_23 -- mosi
              miso: p_19 -- miso
              sck: p_18 -- sck
              cs: p_5 -- cs
    endpoint:
        type: Subscriber
end
```

#### UART Connection

```
Connection
    peripheral: GPSModule
    powerConnections:
        - gnd_1 -- GND
        - power_5v -- VCC
    ioConnections:
        - type: uart
          name: gps_uart  // optional
          pins:
              tx: p_1 -- tx
              rx: p_3 -- rx
              baudrate: 115200
    endpoint:
        topic: "sensors/gps"
        type: Publisher
end
```

#### Endpoint Types

```
endpoint:
    topic: "device/sensor/data"  // optional, auto-generated if omitted
    type: Publisher  // Publisher, Subscriber, RPC, Action
```

**Auto-generated Topics:** If topic is omitted, it's generated as `<device_name>.<peripheral_type>.<peripheral_msg>.<instance_name>` (e.g., `mydevice.sensor.env.mysensor`)

#### Connection Settings

Define peripheral-specific runtime configurations:

```
settings:
    - poll_rate: int = 10
    - threshold: float = 25.5
    - sensor_name: str = "BME680"
    - enable_filter: bool = True
    - thresholds: list = [10, 20, 30, 40]
    - config: dict = {
        timeout: int = 5000,
        retry: bool = True,
        max_attempts: int = 3
      }
end
```

**Setting Types:** `int`, `float`, `str`, `bool`, `list`, `dict`

### Message Brokers

DeMoL supports three message broker types:

#### MQTT Broker

```
Broker<MQTT> MyMqttBroker
    host: "mqtt.example.com"
    port: 1883
    ssl: False
    basePath: "/mqtt"  // optional
    webPath: "/ws"  // optional
    webPort: 8080  // optional
    auth:
        username: "sensor_client"
        password: "secure_pass"
end
```

#### AMQP Broker

```
Broker<AMQP> MyAmqpBroker
    host: "rabbitmq.example.com"
    port: 5672
    vhost: "/"  // optional
    topicExchange: "amq.topic"  // optional
    rpcExchange: "amq.rpc"  // optional
    ssl: False
    auth:
        username: "guest"
        password: "guest"
end
```

#### Redis Broker

```
Broker<Redis> MyRedisBroker
    host: "redis.example.com"
    port: 6379
    db: 0  // optional
    ssl: False
    auth:
        username: "default"
        password: "redis_pass"
end
```

**Authentication Methods:**
- **Username/Password:** `auth: username: "user" password: "pass"`
- **API Key:** `auth: key: "api_key_value"`
- **Certificate:** `auth: cert: "cert_string"` or `certPath: "/path/to/cert"`

### Complete Example

Here's a complete device model demonstrating all features:

```
Metadata
    name: "SmartEnvironmentMonitor"
    description: "Multi-sensor environmental monitoring device"
    author: "john_doe"
    os: Raspbian
end

Network
    ssid: "IoT_Network"
    passwd: "secure_password"
end

Broker<MQTT> SmartHomeBroker
    host: "mqtt.smarthome.local"
    port: 1883
    ssl: True
    auth:
        username: "sensor_node"
        password: "node_pass"
end

Components
    board: RaspberryPi_4B_4GB
    peripherals:
        - BME680(EnvSensor)
        - SonarSRF04(DistanceSensor)
        - WS2812(StatusLED)
end

Connection
    peripheral: EnvSensor
    powerConnections:
        - gnd_1 -- GND
        - power_5v -- VCC
    ioConnections:
        - type: i2c
          slave_address: 0x76
          pins:
              sda: p_21 -- sda
              scl: p_22 -- scl
    endpoint:
        topic: "home/environment/living_room"
        type: Publisher
    settings:
        - poll_period: int = 5
        - humidity_oversample: int = 2
        - pressure_oversample: int = 4
        - temperature_oversample: int = 8
end

Connection
    peripheral: DistanceSensor
    powerConnections:
        - gnd_2 -- gnd
        - power_5v -- vcc
    ioConnections:
        - type: gpio
          name: trigger
          pin: p_23 -- trigger
        - type: gpio
          name: echo
          pin: p_24 -- echo
    endpoint:
        topic: "home/distance/entrance"
        type: Publisher
end

Connection
    peripheral: StatusLED
    powerConnections:
        - gnd_3 -- GND
        - power_5v -- VCC
    ioConnections:
        - type: gpio
          name: LedControl
          pin: GPIO10 -- DIN
    endpoint:
        type: Subscriber
    settings:
        - colors: list = ['0xFF0000', '0x00FF00', '0x0000FF']
        - brightness: int = 128
        - num_leds: int = 12
end


## 🔌 Supported Sensors & Actuators

DeMoL supports **35 sensor types** and **23 actuator types** covering a wide range of IoT applications:

### Sensor Categories

- **Environmental**: Temperature, Humidity, Pressure, Gas, Env, AirQuality, Light, UV, Sound
- **Motion & Position**: Distance, Proximity, Motion, Presence, Acceleration, Gyroscope, Magnetometer, IMU, Tracker
- **Specialized**: ADC, Current, Voltage, Power, Flow, Level, Weight, Force, Vibration
- **Smart**: Camera, RFID, Fingerprint, GPS, Color

### Actuator Categories

- **Basic**: MotorController, ServoController, Relay, Switch
- **Display & Light**: Led, LedArray, NeoPixel, Display, LCD, OLED
- **Sound**: Buzzer, Speaker
- **Advanced**: Stepper, DCMotor, Pump, Valve, Heater, Cooler, Fan

### Message Schemas

Each sensor and actuator type has a defined message schema for standardized communication:

**Example Sensor Message (Environmental):**
```json
{
  "temperature": 23.5,
  "humidity": 65.2,
  "pressure": 1013.25,
  "gas": 450.0,
  "timestamp": 1638360000000
}
```

**Example Actuator Command (NeoPixel):**
```json
{
  "leds": [
    {"index": 0, "r": 255, "g": 0, "b": 0},
    {"index": 1, "r": 0, "g": 255, "b": 0}
  ],
  "brightness": 128,
  "mode": "static",
  "timestamp": 1638360000000
}
```

For complete documentation of all sensor and actuator types with their message schemas, see **[SENSORS_ACTUATORS.md](SENSORS_ACTUATORS.md)**.


## 📐 Formal Semantics

For a complete formal specification of the DeMoL language, see **[SEMANTICS.md](SEMANTICS.md)**, which provides:

- **Abstract Syntax**: Mathematical representation of DeMoL constructs using syntactic domains and abstract syntax trees
- **Formal Grammar**: Complete EBNF specification of the concrete syntax
- **Static Semantics**: Well-formedness rules, type checking, and validation using inference rules
- **Operational Semantics**: Runtime behavior defined via small-step transition systems covering device initialization, broker connections, GPIO/I2C/SPI/UART operations, and message passing
- **Axiomatic Semantics**: Hoare logic specifications with pre/post conditions and invariants for device operations
- **Type System**: Complete type judgments, typing rules, and subtyping relations
- **Verification Conditions**: Safety properties (no short-circuits, voltage limits), liveness properties (message delivery, sensor readings), and correctness conditions

This formal foundation enables rigorous reasoning about device models, verified code generation, and static analysis tools.

## 🔍 Semantic Validations

DeMoL implements comprehensive semantic validations based on the formal semantics defined in [SEMANTICS.md](SEMANTICS.md). These validations ensure device models are well-formed, safe, and correct before code generation.

### Validation Categories

#### 1. **Power Connection Validation**

Ensures electrical compatibility between board and peripheral power connections:

- **Voltage Compatibility**: Power pins must have compatible voltages (within 0.5V tolerance)
- **GND Connections**: Both pins must be GND when connecting ground
- **VCC Connections**: Non-GND voltages must match peripheral requirements
- **Voltage Limits**: Power supplied must not exceed peripheral's maximum rated voltage

**Example Error:**
```
[Conn-Power] Incompatible power connection: board pin power_5v (5.0V) cannot 
connect to peripheral pin vcc (3.3V). Voltage difference exceeds 0.5V tolerance.
```

#### 2. **IO Connection Validation**

Validates pin functionality and protocol-specific requirements:

**GPIO Connections:**
- Both pins must have GPIO functionality
- Valid properties: `mode` (input/output), `pullup`, `pulldown`
- Mode must be either 'input' or 'output'

**I2C Connections:**
- Board and peripheral pins must have SDA/SCL functionality
- Slave address must be in range 0x00-0x7F
- Valid properties: `slave_address`, `bus_speed`
- All I2C addresses on the same bus must be unique

**SPI Connections:**
- All required pins (MOSI, MISO, SCK, CS) must have SPI functionality
- Valid properties: `bus_speed`, `mode` (0-3)

**UART Connections:**
- TX/RX pins must have proper UART functionality
- Board TX connects to Peripheral RX (and vice versa)
- Baudrate must be a common value (9600, 115200, etc.)
- Valid properties: `baudrate`, `parity`, `stop_bits`, `data_bits`

**Example Errors:**
```
[Conn-GPIO] Board pin GPIO5 does not have GPIO functionality.

[Conn-I2C] I2C slave address 0x80 out of valid range [0x00-0x7F]

[Conn-UART] Board pin TX connects to Peripheral TX. UART requires 
connecting Board TX to Peripheral RX.
```

#### 3. **Safety Properties**

Critical safety validations to prevent hardware damage:

**Pin Conflict Detection:**
- Each board pin can only be used once (except I2C and power pins)
- I2C pins (SDA/SCL) can be shared (bus architecture)
- Power pins (GND/VCC) can be shared (common nets)

**IO Voltage Compatibility:**
- Board IO voltage must match peripheral IO voltage
- Prevents communication errors and potential damage
- Emits warnings for voltage mismatches

**Common Ground Validation:**
- Each peripheral should have at least one GND connection
- Ensures proper electrical reference and signal integrity
- Emits warnings when ground connection is missing

**Example Errors:**
```
[Safety-Pin-Conflicts] Pin conflict detected: Board pin 'GPIO4' is already 
used by peripheral 'Sensor1' as 'GPIO'. Cannot reuse for peripheral 'Sensor2'.

[Safety-I2C-Address] I2C address conflict: Address 0x76 is already used by 
peripheral(s): BME680. Cannot reuse for peripheral 'TempSensor'.

[Safety-IO-Voltage] IO Voltage Incompatibility: Board 'RaspberryPi_5_8GB' 
operates at 5.0V (IO), but peripheral 'BME680' operates at 3.3V (IO).
```

#### 4. **Well-Formedness Rules**

Structural validations ensuring model completeness:

- **All Peripherals Connected**: Every peripheral must have at least one connection
- **Unique Peripheral Names**: All peripheral instances must have unique names
- **Unique Pin Numbers**: Pin numbers must be unique within each component
- **Broker Requirements**: Broker must be configured if remote endpoints are used
- **Pin Existence**: All referenced pins must exist in component definitions

**Example Errors:**
```
[WF-All-Peripherals-Connected] Unconnected peripherals detected: DistanceSensor. 
All peripherals must have at least one connection defined.

[WF-Unique-Peripheral-Names] Duplicate peripheral name 'MySensor'. Peripheral 
names must be unique within the device.

[WF-Unique-Pin-Numbers] Duplicate pin number 4 used by pins: GPIO4, SDA1. Pin 
numbers must be unique within a component.
```

### Validation Workflow

1. **Syntax Validation**: textX parser validates grammar compliance
2. **Semantic Validation**: Custom validators check:
   - Power connection compatibility
   - IO connection functionality
   - Safety properties (pin conflicts, voltage limits)
   - Well-formedness rules
3. **Warning Generation**: Non-critical issues emit warnings:
   - IO voltage incompatibility
   - Missing ground connections
   - Unusual baudrates

### Running Validations

**Validate a single model:**
```sh
demol validate examples/rpi_iot_device.dev
```

**Validate all examples:**
```sh
python scripts/validate_examples.py
```

**Validate builtin hardware models:**
```sh
python scripts/validate_builtin_models.py
```

### Validation Output

**Successful validation:**
```
[*] Processing model: examples/rpi_iot_device.dev
[✓] All validation checks passed!
```

**Validation with warnings:**
```
[*] Processing model: examples/esp_iot_device.dev
⚠ [Safety-IO-Voltage] IO Voltage Incompatibility at examples/esp_iot_device.dev:26
[✓] Validation passed with warnings
```

**Validation failure:**
```
[*] Processing model: examples/invalid_device.dev
✗ [Conn-Power] Incompatible power connection: board pin power_5v (5.0V) 
  cannot connect to peripheral pin vcc (3.3V)
```

### Implementation

All semantic validations are implemented in `demol/lang/semantics.py` based on the formal semantics specification. The validation system uses:

- **Type checking** for pin functionality verification
- **Constraint validation** for safety properties
- **Well-formedness rules** for structural correctness
- **Location tracking** for precise error reporting

For the complete formal specification of validation rules, see [SEMANTICS.md](SEMANTICS.md) sections 4 (Well-Formedness), 7 (Type System), and 8 (Verification Conditions).

## 🔧 Usage



The DSL provides a command-line interface (CLI) for operating on models.

```sh
venv [I] ➜ demol --help
Usage: demol [OPTIONS] COMMAND [ARGS]...

  An example CLI for interfacing with a document

Options:
  --help  Show this message and exit.

Commands:
  gen
  validate

```

The `gen` command provides means of executing M2T transformations and provides subcommands, while the `validate` is used to validate input models.

To validate a device model, for example the `./examples/raspi_iot_device.dev`, head to the `examples` directory and execute:

```sh
demol validate raspi_iot_device.dev
```

You should see an output similar to the below, in case of successful validation of the model.

```sh
[*] Running validation for model rpi_iot_device.dev
PowerPinConnection:
  gnd_1 -> gnd
PowerPinConnection:
  power_5v -> vcc
I2C-Connection:
  SDA: p_21 -> sda
  SCL: p_22 -> scl
[*] Validation passed!
```

Otherwise, the parser will raise an error:

```sh
textx.exceptions.TextXSemanticError: rpi_iot_device.dev:29:17: Unknown object "MyBME2" of class "PeripheralDef"
```

### Development & Validation Scripts

The repository includes several utility scripts in the `scripts/` directory for validation and code generation testing:

#### Validate Builtin Models
Validates all builtin board and peripheral models (`.hwd` files) to ensure they comply with the DeMoL grammar and semantics.

```sh
python scripts/validate_builtin_models.py
```

#### Generate RPI Examples
Generates Raspberry Pi code for all example models in `examples/`, validating the code generation pipeline.

```sh
python scripts/generate_rpi_examples.py
```

#### Validate Examples
Validates all example models in `examples/` against the grammar.

```sh
python scripts/validate_examples.py
```

### REST API

TODO...

## 📜 License

DeMoL is protected under the [MIT ](https://choosealicense.com/licenses/mit/) License. For more details, refer to the [MIT LICENSE](https://choosealicense.com/licenses/mit/) uri.

---

## 🎩 Acknowledgments

TODO ...

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=robotics-4-all/demol&type=Date)](https://www.star-history.com/#robotics-4-all/demol&Date)

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
