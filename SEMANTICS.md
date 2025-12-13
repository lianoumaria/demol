# Formal Semantics of DeMoL (Device Modeling Language)

This document outlines the formal semantics and validation rules implemented in the DeMoL language, as defined in `demol/lang/semantics.py`. The validation process ensures that device models are well-formed, safe, and logically consistent before code generation or deployment.

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Hardware Component Definitions](#2-hardware-component-definitions)
    - [Energy Property](#21-energy-property)
    - [Templates Section](#22-templates-section)
    - [Attributes](#23-attributes)
3.  [Power Connection Validation](#3-power-connection-validation)
4.  [Data Connection Validation](#4-data-connection-validation)
    - [GPIO Connections](#41-gpio-connections)
    - [I2C Connections](#42-i2c-connections)
    - [SPI Connections](#43-spi-connections)
    - [UART Connections](#44-uart-connections)
5.  [Safety Properties](#5-safety-properties)
    - [Pin Conflicts (Inv-Unique-Pins)](#51-pin-conflicts-inv-unique-pins)
    - [I2C Address Uniqueness (Safety-I2C-Address-Unique)](#52-i2c-address-uniqueness-safety-i2c-address-unique)
    - [Voltage Limits (Safety-Voltage-Limits)](#53-voltage-limits-safety-voltage-limits)
    - [IO Voltage Compatibility](#54-io-voltage-compatibility)
    - [Common Ground](#55-common-ground)
    - [Topic Format Validation (Safety-Topic-Format)](#56-topic-format-validation-safety-topic-format)
6.  [Well-Formedness Rules](#6-well-formedness-rules)
    - [All Peripherals Connected (WF-All-Peripherals-Connected)](#61-all-peripherals-connected-wf-all-peripherals-connected)
    - [Broker Requirements (Inv-Broker-Connection)](#62-broker-requirements-inv-broker-connection)
    - [Unique Pin Numbers (WF-Unique-Pin-Numbers)](#63-unique-pin-numbers-wf-unique-pin-numbers)
    - [Unique Peripheral Names (WF-Unique-Peripheral-Names)](#64-unique-peripheral-names-wf-unique-peripheral-names)

---

## 1. Introduction

The semantic validation in DeMoL is a critical step that checks the correctness of a device model against a set of predefined rules. These rules are derived from electrical engineering principles and software design best practices. The validator, implemented in `demol/lang/semantics.py`, analyzes the abstract syntax tree (AST) of a DeMoL model and raises errors or warnings if any rules are violated.

The primary goals of semantic validation are:

-   **Preventing Hardware Damage**: Ensuring that electrical connections are compatible and do not exceed component ratings.
-   **Ensuring Correct Functionality**: Verifying that communication protocols are correctly configured and that all components are properly connected.
-   **Enforcing Best Practices**: Promoting robust and maintainable device designs.

---

## 2. Hardware Component Definitions

Hardware components (boards and peripherals) are defined in `.hwd` files with specific properties that affect validation and code generation.

### 2.1. Energy Property

The `energy` property specifies power consumption characteristics with three values: minimum, maximum, and average power consumption. Each value must include a unit.

**Syntax:**
```
energy: <min> <unit>, <max> <unit>, <avg> <unit>
```

**Example - Board:**
```
Board[RPI] RaspberryPi_4B_4GB
  operational
    energy: 1.4 W, 7.6 W, 3.5 W
    vcc: 5V
    ioVcc: 3V3
    ...
  end
  ...
end
```

**Example - Peripheral:**
```
Sensor[Env] BME680
  operational
    energy: 0.01 mW, 39.6 mW, 3 mW
    vcc: 3V3
    ioVcc: 3V3
    ...
  end
  ...
end
```

**Validation:**
- All three values must be positive numbers
- Values represent: [minimum, maximum, average] power consumption
- Units must be valid power units (W, mW, uW)

### 2.2. Templates Section

The `templates` section maps operating systems/platforms to their corresponding code generation templates.

**Syntax:**
```
templates
  <os_name>: "<template_file>",
  ...
end
```

**Example:**
```
Sensor[Env] BME680
  ...
  templates
    raspbian: "bme680.py.tmpl",
    riotos: "bme680_riot.c.tmpl"
  end
end
```

**Validation:**
- Template files must exist in the appropriate templates directory
- OS names must be valid identifiers
- Used by code generators to select appropriate templates

### 2.3. Attributes

Attributes define configurable parameters for peripherals. They can be specified in the peripheral definition (defaults) or overridden in the Components block.

**Syntax in Peripheral Definition:**
```
attributes
  <name> [<type>] = <default_value>,
  ...
end
```

**Syntax in Components Block:**
```
Components
  peripherals:
    <instance>(<Type>) [
      <attribute> = <value>,
      ...
    ]
end
```

**Example - Peripheral Definition:**
```
Sensor[Env] BME680
  ...
  attributes
    poll_period[int] = 10,
    humidity_oversample[int] = 2,
    filter_size[int] = 3
  end
end
```

**Example - Components Block:**
```
Components
  board: RaspberryPi_4B_4GB
  peripherals:
    BME680(MyBME) [
        poll_period = 5,
        filter_size = 7
      ]
end
```

**Validation:**
- Attribute names must be valid identifiers
- Values must match declared types
- Attributes in Components block override peripheral defaults

---

## 3. Power Connection Validation

Power connections are fundamental to the operation of any electronic device. The validator enforces strict rules to ensure that power is supplied correctly and safely.

### Voltage Compatibility

The core principle of power connection validation is voltage compatibility. Voltages are parsed from pin types (e.g., `5V`, `3V3`, `GND`).

-   **Rule `[T-PowerConn-GND]`**: A `GND` pin can only be connected to another `GND` pin.
-   **Rule `[T-PowerConn-VCC]`**: A voltage-supplying pin (e.g., `5V`) can only be connected to another voltage-supplying pin if their voltages are compatible.

**Compatibility Definition**: Two voltages, `v₁` and `v₂`, are considered compatible if the absolute difference between them is within a tolerance of `0.5V`.
`compatible(v₁, v₂) ≡ |v₁ - v₂| ≤ 0.5`

This tolerance allows for slight variations in voltage levels between different components.

---

## 4. Data Connection Validation

Data connections enable communication between the main board and its peripherals. The validator checks that the pins used for data connections have the required functionality and that the protocol-specific properties are correctly defined.

### 4.1. GPIO Connections

-   **Rule `[T-GPIO-Conn]`**: Both the board pin and the peripheral pin involved in a GPIO connection must have `GPIO` functionality.
-   **Properties**:
    -   `mode`: Must be either `'input'` or `'output'`.
    -   `pullup`/`pulldown`: Must be a boolean value.
    -   `name` is a **deprecated** property.

### 4.2. I2C Connections

-   **Rule `[T-I2C-Conn]`**:
    -   The board and peripheral pins must have the appropriate `SDA` (Serial Data) and `SCL` (Serial Clock) functions.
    -   The `slave_address` must be within the valid I2C address range of `0x00` to `0x7F`.
-   **Properties**:
    -   `bus_speed`: Must be a positive integer (e.g., `100000` for 100kHz).
    -   `name` is a **deprecated** property.

### 4.3. SPI Connections

-   **Functionality**: The validator checks that all four SPI pins (`MOSI`, `MISO`, `SCK`, `CS`) on both the board and the peripheral have the corresponding SPI functionality.
-   **Properties**:
    -   `bus_speed`: Must be a positive integer.
    -   `mode`: Must be an integer from `0` to `3`.
    -   `name` is a **deprecated** property.

### 4.4. UART Connections

-   **Functionality**: The connection must correctly map `TX` (Transmit) to `RX` (Receive).
    -   Board `TX` must connect to Peripheral `RX`.
    -   Board `RX` must connect to Peripheral `TX`.
-   **Properties**:
    -   `baudrate`: Must be a positive integer. A warning is issued for non-standard baud rates.
    -   `parity`: Must be one of `'none'`, `'even'`, `'odd'`, `'mark'`, or `'space'`.
    -   `stop_bits`: Must be `1` or `2`.
    -   `data_bits`: Must be an integer from `5` to `8`.
    -   `name` is a **deprecated** property.

---

## 5. Safety Properties

Safety properties are invariants that must hold to prevent hardware damage and ensure stable operation.

### 5.1. Pin Conflicts (Inv-Unique-Pins)

-   **Rule**: A single board pin cannot be used for multiple conflicting purposes simultaneously.
-   **Invariant**: `∀k₁, k₂ ∈ connections, k₁ ≠ k₂. usedPins(k₁) ∩ usedPins(k₂) = ∅`
-   **Exceptions**:
    -   **Power Pins (`GND`, `VCC`)**: Multiple peripherals can connect to the same power pins.
    -   **I2C Pins (`SDA`, `SCL`)**: I2C is a bus protocol, so multiple devices can share the same `SDA` and `SCL` pins.

### 5.2. I2C Address Uniqueness (Safety-I2C-Address-Unique)

-   **Rule**: On a shared I2C bus, every peripheral must have a unique `slave_address`.
-   **Invariant**: `∀k₁, k₂. sameBus(k₁, k₂) ⇒ k₁.slaveAddr ≠ k₂.slaveAddr`

### 5.3. Voltage Limits (Safety-Voltage-Limits)

-   **Rule**: The voltage supplied to a peripheral must not exceed its maximum rated voltage (`vcc`).
-   **Invariant**: `∀k ∈ connections, p = k.peripheral. voltage(p) ≤ p.vcc.toVolts()`
-   A tolerance of `0.5V` is allowed.

### 5.4. IO Voltage Compatibility

-   **Rule**: The I/O voltage level of the board (`ioVcc`) must be compatible with the I/O voltage level of the connected peripheral.
-   **Warning**: If the I/O voltages are not compatible (i.e., differ by more than `0.5V`), a warning is issued. This may lead to communication errors or, in worst-case scenarios, damage the hardware.

### 5.5. Common Ground

-   **Rule**: Every peripheral must share a common ground (`GND`) connection with the board.
-   **Warning**: If a peripheral has no defined power connections or lacks a `GND` connection, a warning is issued. A common ground is essential for creating a complete electrical circuit and ensuring signal integrity.

### 5.6. Topic Format Validation (Safety-Topic-Format)

-   **Rule**: Remote topics specified in connections must conform to the format requirements of the configured broker type.
-   **Validation**: Topics are validated based on the broker protocol to prevent runtime errors and ensure compatibility with the message broker.

#### MQTT Topic Validation

When using an **MQTT broker** (`Broker[MQTT]`), topics must follow MQTT protocol specifications:

**Requirements:**
-   Use forward slashes (`/`) as level separators
-   Cannot start with `$` (reserved for system topics like `$SYS`)
-   Maximum length: 1000 characters
-   No null characters (`\x00`)
-   Wildcards (for subscriptions):
    -   `+` : Single-level wildcard (must be alone in its level)
    -   `#` : Multi-level wildcard (must be last level and alone)

**Valid Examples:**
```
sensors/temperature/room1
home/living_room/light
devices/+/status
sensor/#
```

**Invalid Examples:**
```
$SYS/broker/stats          // System topic (starts with $)
sensors/temp+/room         // Wildcard not alone
sensors/room/#/temp        // # must be last level
```

#### AMQP Routing Key Validation

When using an **AMQP broker** (`Broker[AMQP]`), routing keys must follow AMQP topic exchange rules:

**Requirements:**
-   Use dots (`.`) as word separators
-   Maximum length: 255 characters
-   Allowed characters: alphanumeric, underscore (`_`), hyphen (`-`)
-   No empty segments (double dots `..`)
-   Wildcards (for bindings):
    -   `*` : Matches exactly one word
    -   `#` : Matches zero or more words

**Valid Examples:**
```
sensors.temperature.room1
home.living_room.light
devices.*.status
sensor.#
```

**Invalid Examples:**
```
sensors/temperature/room   // Uses slashes instead of dots
sensors..room              // Empty segment (double dots)
sensors.temp@.room         // Invalid character (@)
```

#### Redis Channel Validation

When using a **Redis broker** (`Broker[Redis]`), channels have flexible naming:

**Requirements:**
-   Cannot be empty
-   Maximum length: 512 characters
-   Supports glob-style pattern matching (`*`, `?`)
-   Convention: Use colons (`:`) or dots (`.`) as separators

**Valid Examples:**
```
sensors:temperature:room1
home.living_room.light
device:*:status
sensor*
```

**Implementation:**
The validation is performed in `demol/lang/semantics.py` via the `validate_topic_format()` function, which automatically selects the appropriate validator based on the broker type defined in the device model.

**Error Example:**
```
[TopicValidationError] [Topic-Validation] Invalid MQTT topic at 
ParkingSensor.dev:27: Peripheral 'Sensor1' has topic '$SYS/broker/stats'. 
MQTT topic cannot start with '$' (reserved for system topics)
```


## 6. Well-Formedness Rules

Well-formedness rules ensure that the device model is complete and logically sound.

### 6.1. All Peripherals Connected (WF-All-Peripherals-Connected)

-   **Rule**: Every peripheral declared in the `Components` section must be used in at least one `Connection`.
-   **Invariant**: `∀p ∈ components.peripherals. ∃k ∈ connections. k.peripheral = p`

### 6.2. Broker Requirements (Inv-Broker-Connection)

-   **Rule**: If any connection defines a remote endpoint (e.g., for MQTT `Publisher` or `Subscriber`), a `Broker` must be configured in the device model.
-   **Invariant**: `(∃k. k.endpoint.type ∈ {Publisher, Subscriber}) ⇒ (broker ≠ None)`

### 6.3. Unique Pin Numbers (WF-Unique-Pin-Numbers)

-   **Rule**: Within a single component (board or peripheral) definition, all physical pin numbers must be unique.

### 6.4. Unique Peripheral Names (WF-Unique-Peripheral-Names)

-   **Rule**: All peripheral instances defined in the `Components` section must have unique names. This prevents ambiguity when defining connections.