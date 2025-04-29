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
    - [🧪 Modeling Devices](#-modeling-devices)
      - [Example model of an ESP32 board](#example-model-of-an-esp32-board)
      - [Example model of a peripheral sensor](#example-model-of-a-peripheral-sensor)
      - [Example Device model](#example-device-model)
    - [CLI](#cli)
    - [REST API](#rest-api)
  - [📜 License](#-license)
  - [🎩 Acknowledgments](#-acknowledgments)
  - [🌟 Star History](#-star-history)

## 📖 Overview

Device Modeling Language (DeMoL) - A DSL for modeling IoT devices.

Enables automated source code generation currently for RaspberryPi and RiotOS.

...

## 👾 Features

|      | Feature         | Summary       |
| :--- | :---:           | :---          |
| ⚙️  | **Protocol-Agnostic**  | <ul><li>Protocol/Transport-level abstraction</li><li>Currently supports Redis, AMQP and MQTT</li></ul> |
| 📄 | **Documentation** | <ul><li>Rich documentation in various formats (YAML, TOML, Markdown)</li><li>Includes detailed installation commands for different package managers</li><li>Utilizes MkDocs for generating documentation</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Well-structured codebase with clear separation of concerns</li><li>Encourages code reusability and maintainability</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Manages dependencies with Poetry and dependency lock files</li><li>Includes a variety of libraries for different functionalities</li><li>Dependency management with conda for environment setup</li><li>Dynamic imports of underlying transport libraries</li></ul> |

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
git clone git@github.com:robotics-4-all/demol.git
```

2. Create a Virtual environment (Optional Step)

```sh
python -m venv venv && source ./venv/bin/activate
```

3. Install the DSL package in `develop` mode

```sh
python setup.py develop
```


### 🧪 Modeling Devices

The implementation of the grammar of the language can be found [here]().

The core Concepts of the language are:

- **Device**
- **Board**
- **Peripheral**
- **Synthesis**
- **Connection**
- **CommunicationTransport**

The language allows multi-file model imports and also uses a global local
repository for loading and referencing existing Board, Peripheral and Synthesis models.

```
import srf04.hwd
import esp32_wroom_32.hwd

Connection SonarESP32
    board: ESP32Wroom32
    peripheral: SonarSRF04
    powerConnections:
    - ESP32Wroom32.gnd_1 -- SonarSRF04.gnd
    - ESP32Wroom32.power_5v -- SonarSRF04.vcc
    ...
end
```

#### Example model of an ESP32 board

```
Board ESP32Wroom32
    vcc: 3.3
    operating_voltage: 3.3
    memory:
    flash: 4 mb
    cpu:
        cpu_family: ESP32
        max_freq: 240 mhz
        fpu: false
    network:
    - wifi:
	name: wifi_1
	freq: 2.5 ghz
	bluetooth:
        version: 4.2
    pins:
    - power:
        name: power_3v3
        number: 1
        type: 3v3
    - io_pin:
        functions:
        name: en_rst
        number: 2
    - io_pin:
        functions: gpio, adc
        name: svp
        number: 3
    ...
end
```

#### Example model of a peripheral sensor

```
Peripheral SonarSRF04
    type: Sensor
    riot_name: "srf04"
    operating_voltage: 5
    vcc: 5
    pins:
    - power:
        name: vcc
        number: 1
        type: 5v
    - power:
        name: gnd
        number: 4
        type: gnd
    - io_pin:
        functions: gpio
        name: trigger
        number: 2
    - io_pin:
        functions: gpio
        name: echo
        number: 3
end
```

#### Example Device model

```
Network
    ssid: "Guest_Network_2.4GHz"
    passwd: "guest"
end

Communication<MQTT>
    host: "node.mqtt.local"
    port: 1885
    auth:
        username: "guest"
        password: "guest"
end

Connection SonarESP32
    board: ESP32Wroom32
    peripheral: SonarSRF04
    powerConnections:
    - ESP32Wroom32.gnd_1 -- SonarSRF04.gnd
    - ESP32Wroom32.power_5v -- SonarSRF04.vcc
    ioConnections:
    - gpio: ESP32Wroom32.p_13 -- SonarSRF04.trigger
    - gpio: ESP32Wroom32.p_14 -- SonarSRF04.echo
    endpoint:
	topic: "my_esp.sensors.srf04"
	msg: Distance
	frequency: 5 hz
end

Connection Bme680Esp32
    board: ESP32Wroom32
    peripheral: BME680
    powerConnections:
    - ESP32Wroom32.gnd_1 -- BME680.gnd
    - ESP32Wroom32.power_5v -- BME680.vcc
    ioConnections:
    - i2c:
        sda: ESP32Wroom32.p_21 -- BME680.sda
        scl: ESP32Wroom32.p_22 -- BME680.scl
        slave_address: 0x76
    endpoint:
	topic: "my_esp.sensors.bme680"
	msg: Env
	frequency: 2 hz
end
```

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
