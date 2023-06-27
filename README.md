# demol
Device Modeling Language (DeMoL) - A DSL for modeling IoT devices.
Enables automated source code generation currently for RaspberryPi and RiotOS.

## Usage

The implementation of the grammar of the language can be found [here]().

The core Concepts of the language are:

- Device
- Board
- Peripheral
- Synthesis
- Connection
- CommunicationTransport

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

### Model a Board

```
Board ESP32Wroom32
	riot_name: "esp32-wroom-32"
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

### Model a Peripheral

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

### Create a Synthesis model

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
