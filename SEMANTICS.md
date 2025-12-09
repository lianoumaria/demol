# Formal Semantics of DeMoL (Device Modeling Language)

This document outlines the formal semantics and validation rules implemented in the DeMoL language, as defined in `demol/lang/semantics.py`. The validation process ensures that device models are well-formed, safe, and logically consistent before code generation or deployment.

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Power Connection Validation](#2-power-connection-validation)
3.  [Data Connection Validation](#3-data-connection-validation)
    - [GPIO Connections](#31-gpio-connections)
    - [I2C Connections](#32-i2c-connections)
    - [SPI Connections](#33-spi-connections)
    - [UART Connections](#34-uart-connections)
4.  [Safety Properties](#4-safety-properties)
    - [Pin Conflicts (Inv-Unique-Pins)](#41-pin-conflicts-inv-unique-pins)
    - [I2C Address Uniqueness (Safety-I2C-Address-Unique)](#42-i2c-address-uniqueness-safety-i2c-address-unique)
    - [Voltage Limits (Safety-Voltage-Limits)](#43-voltage-limits-safety-voltage-limits)
    - [IO Voltage Compatibility](#44-io-voltage-compatibility)
    - [Common Ground](#45-common-ground)
5.  [Well-Formedness Rules](#5-well-formedness-rules)
    - [All Peripherals Connected (WF-All-Peripherals-Connected)](#51-all-peripherals-connected-wf-all-peripherals-connected)
    - [Broker Requirements (Inv-Broker-Connection)](#52-broker-requirements-inv-broker-connection)
    - [Unique Pin Numbers (WF-Unique-Pin-Numbers)](#53-unique-pin-numbers-wf-unique-pin-numbers)
    - [Unique Peripheral Names (WF-Unique-Peripheral-Names)](#54-unique-peripheral-names-wf-unique-peripheral-names)

---

## 1. Introduction

The semantic validation in DeMoL is a critical step that checks the correctness of a device model against a set of predefined rules. These rules are derived from electrical engineering principles and software design best practices. The validator, implemented in `demol/lang/semantics.py`, analyzes the abstract syntax tree (AST) of a DeMoL model and raises errors or warnings if any rules are violated.

The primary goals of semantic validation are:

-   **Preventing Hardware Damage**: Ensuring that electrical connections are compatible and do not exceed component ratings.
-   **Ensuring Correct Functionality**: Verifying that communication protocols are correctly configured and that all components are properly connected.
-   **Enforcing Best Practices**: Promoting robust and maintainable device designs.

---

## 2. Power Connection Validation

Power connections are fundamental to the operation of any electronic device. The validator enforces strict rules to ensure that power is supplied correctly and safely.

### Voltage Compatibility

The core principle of power connection validation is voltage compatibility. Voltages are parsed from pin types (e.g., `5V`, `3V3`, `GND`).

-   **Rule `[T-PowerConn-GND]`**: A `GND` pin can only be connected to another `GND` pin.
-   **Rule `[T-PowerConn-VCC]`**: A voltage-supplying pin (e.g., `5V`) can only be connected to another voltage-supplying pin if their voltages are compatible.

**Compatibility Definition**: Two voltages, `v₁` and `v₂`, are considered compatible if the absolute difference between them is within a tolerance of `0.5V`.
`compatible(v₁, v₂) ≡ |v₁ - v₂| ≤ 0.5`

This tolerance allows for slight variations in voltage levels between different components.

---

## 3. Data Connection Validation

Data connections enable communication between the main board and its peripherals. The validator checks that the pins used for data connections have the required functionality and that the protocol-specific properties are correctly defined.

### 3.1. GPIO Connections

-   **Rule `[T-GPIO-Conn]`**: Both the board pin and the peripheral pin involved in a GPIO connection must have `GPIO` functionality.
-   **Properties**:
    -   `mode`: Must be either `'input'` or `'output'`.
    -   `pullup`/`pulldown`: Must be a boolean value.
    -   `name` is a **deprecated** property.

### 3.2. I2C Connections

-   **Rule `[T-I2C-Conn]`**:
    -   The board and peripheral pins must have the appropriate `SDA` (Serial Data) and `SCL` (Serial Clock) functions.
    -   The `slave_address` must be within the valid I2C address range of `0x00` to `0x7F`.
-   **Properties**:
    -   `bus_speed`: Must be a positive integer (e.g., `100000` for 100kHz).
    -   `name` is a **deprecated** property.

### 3.3. SPI Connections

-   **Functionality**: The validator checks that all four SPI pins (`MOSI`, `MISO`, `SCK`, `CS`) on both the board and the peripheral have the corresponding SPI functionality.
-   **Properties**:
    -   `bus_speed`: Must be a positive integer.
    -   `mode`: Must be an integer from `0` to `3`.
    -   `name` is a **deprecated** property.

### 3.4. UART Connections

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

## 4. Safety Properties

Safety properties are invariants that must hold to prevent hardware damage and ensure stable operation.

### 4.1. Pin Conflicts (Inv-Unique-Pins)

-   **Rule**: A single board pin cannot be used for multiple conflicting purposes simultaneously.
-   **Invariant**: `∀k₁, k₂ ∈ connections, k₁ ≠ k₂. usedPins(k₁) ∩ usedPins(k₂) = ∅`
-   **Exceptions**:
    -   **Power Pins (`GND`, `VCC`)**: Multiple peripherals can connect to the same power pins.
    -   **I2C Pins (`SDA`, `SCL`)**: I2C is a bus protocol, so multiple devices can share the same `SDA` and `SCL` pins.

### 4.2. I2C Address Uniqueness (Safety-I2C-Address-Unique)

-   **Rule**: On a shared I2C bus, every peripheral must have a unique `slave_address`.
-   **Invariant**: `∀k₁, k₂. sameBus(k₁, k₂) ⇒ k₁.slaveAddr ≠ k₂.slaveAddr`

### 4.3. Voltage Limits (Safety-Voltage-Limits)

-   **Rule**: The voltage supplied to a peripheral must not exceed its maximum rated voltage (`vcc`).
-   **Invariant**: `∀k ∈ connections, p = k.peripheral. voltage(p) ≤ p.vcc.toVolts()`
-   A tolerance of `0.5V` is allowed.

### 4.4. IO Voltage Compatibility

-   **Rule**: The I/O voltage level of the board (`ioVcc`) must be compatible with the I/O voltage level of the connected peripheral.
-   **Warning**: If the I/O voltages are not compatible (i.e., differ by more than `0.5V`), a warning is issued. This may lead to communication errors or, in worst-case scenarios, damage the hardware.

### 4.5. Common Ground

-   **Rule**: Every peripheral must share a common ground (`GND`) connection with the board.
-   **Warning**: If a peripheral has no defined power connections or lacks a `GND` connection, a warning is issued. A common ground is essential for creating a complete electrical circuit and ensuring signal integrity.

---

## 5. Well-Formedness Rules

Well-formedness rules ensure that the device model is complete and logically sound.

### 5.1. All Peripherals Connected (WF-All-Peripherals-Connected)

-   **Rule**: Every peripheral declared in the `Components` section must be used in at least one `Connection`.
-   **Invariant**: `∀p ∈ components.peripherals. ∃k ∈ connections. k.peripheral = p`

### 5.2. Broker Requirements (Inv-Broker-Connection)

-   **Rule**: If any connection defines a remote endpoint (e.g., for MQTT `Publisher` or `Subscriber`), a `Broker` must be configured in the device model.
-   **Invariant**: `(∃k. k.endpoint.type ∈ {Publisher, Subscriber}) ⇒ (broker ≠ None)`

### 5.3. Unique Pin Numbers (WF-Unique-Pin-Numbers)

-   **Rule**: Within a single component (board or peripheral) definition, all physical pin numbers must be unique.

### 5.4. Unique Peripheral Names (WF-Unique-Peripheral-Names)

-   **Rule**: All peripheral instances defined in the `Components` section must have unique names. This prevents ambiguity when defining connections.