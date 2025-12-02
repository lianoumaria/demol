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
  - [📐 Formal Semantics](#-formal-semantics)
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

Boards are defined in `.hwd` files and describe microcontroller/SBC specifications:

```
Board ESP32Wroom32
    vcc: 3V3
    memory:
        flash: 4 mb
        ram: 520 kb  // optional
        rom: 448 kb  // optional
    cpu:
        cpu_family: ESP32  // ESP32, ESP8266, PiArmCortex
        max_freq: 240 mhz
        fpu: false
    networking:
    - wifi:
        name: wifi_1
        freq: 2.5 ghz
    - ethernet:  // optional
        name: eth0
    bluetooth: BT4  // BT3, BT4, BT5, NA
    ioVcc: 3V3  // optional IO voltage
    pins:
    - power:
        name: power_3v3
        number: 1
        type: 3V3
    - io_pin:
        functions: gpio, adc, pwm-1
        name: p_32
        number: 7
        vmin: 0  // optional
        vmax: 3.3  // optional
        signalLevel: 3.3  // optional
end
```

**Pin Functions:** `gpio`, `adc`, `dac`, `pwm-<channel>`, `sda-<bus>`, `scl-<bus>`, `mosi-<bus>`, `miso-<bus>`, `sck-<bus>`, `cs-<bus>`, `tx-<bus>`, `rx-<bus>`, `fs`, `din`, `dout`

**Power Types:** `GND`, `3V3`, `5V`, `12V`, or custom (e.g., `2.5V`, `1.8V`)

#### Peripheral Models (Sensors)

```
Sensor BME680
    vcc: 5V
    msg: Env  // Message type: Distance, Temperature, Humidity, Gas, Pressure, Env, Acceleration, IMU, Tracker, ADC
    piTpl: "bme680"  // optional - RaspberryPi template
    riotTpl: "bme680"  // optional - RiotOS template
    ioVcc: 3V3  // optional
    pins:
        - power:
            name: VCC
            number: 1
            type: 5V
        - power:
            name: GND
            number: 5
            type: GND
        - io_pin:
            functions: sda-0
            name: sda
            number: 2
        - io_pin:
            functions: scl-0
            name: scl
            number: 3
    attributes:
        - poll_period: int = 10
        - humidity_oversample: int = 2
        - temperature_oversample: int = 8
    constraints:
        - max_frequency: 20 hz
        - min_distance: 2 cm  // for distance sensors
        - max_distance: 400 cm  // for distance sensors
    powerConsumption: 3 mW  // optional
end
```

#### Peripheral Models (Actuators)

```
Actuator ServoMotor
    vcc: 5V
    msg: ServoController  // MotorController, ServoController, LedArray
    pins:
        - power:
            name: VCC
            number: 1
            type: 5V
        - power:
            name: GND
            number: 2
            type: GND
        - io_pin:
            functions: pwm-0
            name: control
            number: 3
    attributes:
        - min_angle: int = 0
        - max_angle: int = 180
    powerConsumption: 500 mW
end
```

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
```


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

## 🔧 Usage

1. Save your .dev file in examples directory.

2. Create an output directory.

3. Move to demol/transformations directory.

4. Start python.

```sh
python
```

5. Import m2t and/or m2m transformation files.

```sh 
import m2t, m2m
```

6. Run the transformations as m2t.main(model,directory) and m2m.main(model,directory).
The first argument should be the path to the .dev file starting from examples directory. 
The second argument should be the name of (or the path to) the output directory.

For example to run the transformations for ThesisExample.dev which is saved in examples/ThesisExamples directory you should run
```sh
m2t.main("ThesisExamples/ThesisExample.dev", "rpi5_out/ThesisExample")
m2m.main("ThesisExamples/ThesisExample.dev", "rpi5_out/ThesisExample")
```
And the results will be stored in rpi5_out/ThesisExample directory.

### CLI

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

### REST API

TODO...

## 📜 License

Commlib-py is protected under the [MIT ](https://choosealicense.com/licenses/mit/) License. For more details, refer to the [MIT LICENSE](https://choosealicense.com/licenses/mit/) uri.

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
