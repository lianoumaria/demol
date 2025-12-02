# Formal Semantics of DeMoL (Device Modeling Language)

## Table of Contents

1. [Introduction](#introduction)
2. [Abstract Syntax](#abstract-syntax)
3. [Formal Grammar](#formal-grammar)
4. [Static Semantics](#static-semantics)
5. [Operational Semantics](#operational-semantics)
6. [Axiomatic Semantics](#axiomatic-semantics)
7. [Type System](#type-system)
8. [Verification Conditions](#verification-conditions)

---

## 1. Introduction

DeMoL is a declarative domain-specific language for modeling IoT devices. This document provides the formal semantics covering:

- **Abstract Syntax**: The mathematical representation of DeMoL programs
- **Formal Grammar**: BNF/EBNF specification of concrete syntax
- **Static Semantics**: Type checking and well-formedness rules
- **Operational Semantics**: Runtime behavior and execution model
- **Axiomatic Semantics**: Logical properties and verification conditions

---

## 2. Abstract Syntax

### 2.1 Syntactic Domains

```
d ∈ DeviceModel
m ∈ Metadata
n ∈ Network
c ∈ Components
b ∈ Board
p ∈ Peripheral ::= Sensor | Actuator
k ∈ Connection
br ∈ Broker ::= MQTTBroker | AMQPBroker | RedisBroker
pin ∈ Pin ::= PowerPin | IOPin
conn ∈ IOConnection ::= GPIOConn | I2CConn | SPIConn | UARTConn
e ∈ Endpoint
s ∈ Setting
v ∈ Value ::= Int(ℤ) | Float(ℝ) | String(Σ*) | Bool(𝔹) | List([Value]) | Dict({String ↦ Value})
```

### 2.2 Abstract Syntax Trees

#### Device Model

```
DeviceModel ::= Device(
    imports: List[Import],
    meta: Metadata,
    network: Network,
    components: Components,
    broker: Option[Broker],
    connections: List[Connection]
)

Import ::= Imp(uri: FQN, alias: Option[ID])
```

#### Metadata

```
Metadata ::= Meta(
    name: String,
    description: String,
    author: String,
    os: OS
)

OS ::= Raspbian | RiotOS
```

#### Network

```
Network ::= Net(
    ssid: String,
    passwd: String,
    address: Option[IPAddr],
    channel: Option[String]
)

IPAddr ::= IPv4(String) | IPv6(String)
```

#### Components

```
Components ::= Comp(
    board: BoardRef,
    peripherals: List[PeripheralDef]
)

BoardRef ::= Ref(name: FQN, model: Board)

PeripheralDef ::= PDef(
    ref: PeripheralRef,
    instanceName: ID
)

PeripheralRef ::= Ref(name: FQN, model: Peripheral)
```

#### Board

```
Board ::= BoardDef(
    name: ID,
    vcc: PowerType,
    cpu: CPU,
    memory: Memory,
    pins: List[Pin],
    networking: List[NetworkInterface],
    bluetooth: BluetoothVersion,
    ioVcc: Option[PowerType]
)

CPU ::= CPUSpec(
    family: CPUFamily,
    maxFreq: Frequency,
    fpu: Bool
)

CPUFamily ::= ESP32 | ESP8266 | PiArmCortex

Memory ::= MemSpec(
    ram: Option[Size],
    rom: Option[Size],
    flash: Option[Size]
)

NetworkInterface ::= WiFi(name: ID, freq: Option[Frequency])
                   | Ethernet(name: ID)

BluetoothVersion ::= NA | BT3 | BT4 | BT5
```

#### Peripheral

```
Peripheral ::= Sensor(
                   name: ID,
                   vcc: PowerType,
                   msg: SensorMsgType,
                   pins: List[Pin],
                   attributes: List[Attribute],
                   constraints: List[Constraint],
                   powerConsumption: Option[Power],
                   piTpl: Option[String],
                   riotTpl: Option[String],
                   ioVcc: Option[PowerType]
               )
             | Actuator(
                   name: ID,
                   vcc: PowerType,
                   msg: ActuatorMsgType,
                   pins: List[Pin],
                   attributes: List[Attribute],
                   constraints: List[Constraint],
                   powerConsumption: Option[Power],
                   piTpl: Option[String],
                   riotTpl: Option[String],
                   ioVcc: Option[PowerType]
               )

SensorMsgType ::= Distance | Temperature | Humidity | Gas | Pressure 
                | Env | Acceleration | IMU | Tracker | ADC

ActuatorMsgType ::= MotorController | ServoController | LedArray
```

#### Pins

```
Pin ::= PowerPin(name: ID, number: ℕ, type: PowerType)
      | IOPin(name: ID, number: Option[ℕ], functions: List[PinFunction],
              vmin: Option[ℝ], vmax: Option[ℝ], signalLevel: Option[ℝ])

PowerType ::= GND | V3_3 | V5 | V12 | Custom(ℝ)

PinFunction ::= GPIO
              | I2C(type: I2CType, bus: ℕ)
              | SPI(type: SPIType, bus: ℕ)
              | UART(type: UARTType, bus: ℕ)
              | PWM(channel: ℕ)
              | ADC | DAC
              | PCM(type: PCMType)

I2CType ::= SDA | SCL
SPIType ::= MOSI | MISO | SCK | CS
UARTType ::= TX | RX
PCMType ::= FS | DIN | DOUT
```

#### Connection

```
Connection ::= Conn(
    peripheral: PeripheralDef,
    board: BoardRef,  // Implicit in grammar, explicit in resolved model
    powerConns: List[PowerConnection],
    ioConns: List[IOConnection],
    endpoint: Option[Endpoint],
    settings: List[Setting]
)

PowerConnection ::= PConn(boardPin: ID, peripheralPin: ID)

IOConnection ::= GPIOConn(name: Option[ID], pin: PinConn, mode: GPIOMode)
               | I2CConn(name: Option[ID], slaveAddr: ℕ, sda: PinConn, scl: PinConn)
               | SPIConn(name: Option[ID], mosi: PinConn, miso: PinConn, 
                        sck: PinConn, cs: PinConn)
               | UARTConn(name: Option[ID], tx: PinConn, rx: PinConn, baudrate: ℕ)

PinConn ::= PC(boardPin: ID, peripheralPin: ID)

GPIOMode ::= GPIOConfig(
    input: Option[Bool],
    output: Option[Bool],
    pullup: Option[Bool],
    pulldown: Option[Bool],
    openDrain: Option[Bool]
)
```

#### Endpoint

```
Endpoint ::= EP(
    topic: Option[String],
    type: Option[EndpointType]
)

EndpointType ::= Publisher | Subscriber | RPC | Action
```

#### Broker

```
Broker ::= MQTTBroker(
               name: ID,
               host: String,
               port: ℕ,
               ssl: Option[Bool],
               basePath: Option[String],
               webPath: Option[String],
               webPort: Option[ℕ],
               auth: Option[Auth]
           )
         | AMQPBroker(
               name: ID,
               host: String,
               port: ℕ,
               vhost: Option[String],
               topicExchange: Option[String],
               rpcExchange: Option[String],
               ssl: Option[Bool],
               auth: Option[Auth]
           )
         | RedisBroker(
               name: ID,
               host: String,
               port: ℕ,
               db: Option[ℕ],
               ssl: Option[Bool],
               auth: Option[Auth]
           )

Auth ::= AuthPlain(username: String, password: String)
       | AuthApiKey(key: String)
       | AuthCert(cert: String) | AuthCertPath(path: String)
```

#### Settings and Attributes

```
Setting ::= IntSetting(name: ID, default: Option[ℤ])
          | FloatSetting(name: ID, default: Option[ℝ])
          | StringSetting(name: ID, default: Option[String])
          | BoolSetting(name: ID, default: Option[Bool])
          | ListSetting(name: ID, default: Option[List[Value]])
          | DictSetting(name: ID, default: Option[Dict[String, Setting]])

Attribute ::= IntAttr(name: ID, default: Option[ℤ])
            | FloatAttr(name: ID, default: Option[ℝ])
            | StringAttr(name: ID, default: Option[String])
            | BoolAttr(name: ID, default: Option[Bool])
            | ListAttr(name: ID, default: Option[List[Value]])
            | DictAttr(name: ID, default: Option[Dict[String, Attribute]])

Constraint ::= MaxFrequency(value: ℝ, unit: FreqUnit)
             | MinDistance(value: ℝ, unit: DistUnit)
             | MaxDistance(value: ℝ, unit: DistUnit)
```

---

## 3. Formal Grammar

### 3.1 Context-Free Grammar (Extended BNF)

```ebnf
(* Device Model *)
DeviceModel ::= Import* Metadata Network Components Broker? Connection+

Import ::= 'import' FQN ('as' ID)?

FQN ::= ID ('.' ID)*

(* Metadata *)
Metadata ::= 'Metadata'
             'name:' STRING
             'description:' STRING
             'author:' STRING
             ('os:' OS)?
             'end'

OS ::= 'Raspbian' | 'RiotOS'

(* Network *)
Network ::= 'Network'
            'ssid:' STRING
            'passwd:' STRING
            ('address:' IPAddr)?
            ('channel:' STRING)?
            'end'

IPAddr ::= IPv4 | IPv6
IPv4 ::= Digit{1,3} '.' Digit{1,3} '.' Digit{1,3} '.' Digit{1,3}
IPv6 ::= (HexDigit{1,4} ':'){7} HexDigit{1,4}

(* Components *)
Components ::= 'Components'
               'board:' FQN
               'peripherals:' '-' PeripheralDef ('-' PeripheralDef)*
               'end'

PeripheralDef ::= FQN '(' ID ')'

(* Board *)
Board ::= 'Board' ID
          'cpu:' CPU
          'memory:' Memory
          'vcc:' PowerType
          'pins:' '-' Pin ('-' Pin)*
          ('networking:' '-' NetworkInterface ('-' NetworkInterface)*)?
          ('bluetooth:' BluetoothVersion)?
          ('ioVcc:' PowerType)?
          'end'

CPU ::= 'cpu_family:' CPUFamily
        'max_freq:' Number FreqUnit
        'fpu:' BOOL

CPUFamily ::= 'ESP32' | 'ESP8266' | 'PiArmCortex'

Memory ::= ('ram:' Number MemUnit)?
           ('rom:' Number MemUnit)?
           ('flash:' Number MemUnit)?

MemUnit ::= 'b' | 'kb' | 'mb' | 'gb'
FreqUnit ::= 'hz' | 'khz' | 'mhz' | 'ghz'

NetworkInterface ::= WiFiInterface | EthernetInterface

WiFiInterface ::= 'wifi:' 'name:' ID ('freq:' Number FreqUnit)?

EthernetInterface ::= 'ethernet:' 'name:' ID

BluetoothVersion ::= 'NA' | 'BT3' | 'BT4' | 'BT5'

(* Peripheral *)
Peripheral ::= Sensor | Actuator

Sensor ::= 'Sensor' ID
           'vcc:' PowerType
           'msg:' SensorMsgType
           'pins:' '-' Pin ('-' Pin)*
           ('attributes:' '-' Attribute ('-' Attribute)*)?
           ('constraints:' '-' Constraint ('-' Constraint)*)?
           ('powerConsumption:' Number PowerUnit)?
           ('riotTpl:' STRING)?
           ('piTpl:' STRING)?
           ('ioVcc:' PowerType)?
           'end'

Actuator ::= 'Actuator' ID
             'vcc:' PowerType
             'msg:' ActuatorMsgType
             'pins:' '-' Pin ('-' Pin)*
             ('attributes:' '-' Attribute ('-' Attribute)*)?
             ('constraints:' '-' Constraint ('-' Constraint)*)?
             ('powerConsumption:' Number PowerUnit)?
             ('riotTpl:' STRING)?
             ('piTpl:' STRING)?
             ('ioVcc:' PowerType)?
             'end'

SensorMsgType ::= 'Distance' | 'Temperature' | 'Humidity' | 'Gas' 
                | 'Pressure' | 'Env' | 'Acceleration' | 'IMU' 
                | 'Tracker' | 'ADC'

ActuatorMsgType ::= 'MotorController' | 'ServoController' | 'LedArray'

PowerUnit ::= 'W' | 'mW' | 'uW'

(* Pin *)
Pin ::= PowerPin | IOPin

PowerPin ::= 'power:'
             'name:' ID
             'number:' INT
             'type:' PowerType

PowerType ::= 'GND' | '3V3' | '5V' | '12V' | CustomVoltage

CustomVoltage ::= Number 'V'

IOPin ::= 'io_pin:'
          'functions:' PinFunction (',' PinFunction)*
          'name:' ID
          ('number:' INT)?
          ('vmin:' Number)?
          ('vmax:' Number)?
          ('signalLevel:' Number)?

PinFunction ::= 'gpio' 
              | I2CType '-' INT
              | SPIType '-' INT
              | UARTType '-' INT
              | 'pwm-' INT
              | 'adc' | 'dac'
              | PCMType

I2CType ::= 'sda' | 'scl'
SPIType ::= 'mosi' | 'miso' | 'sck' | 'cs'
UARTType ::= 'tx' | 'rx'
PCMType ::= 'fs' | 'din' | 'dout'

(* Connection *)
Connection ::= 'Connection'
               'peripheral:' FQN
               'powerConnections:' '-' PowerConnection ('-' PowerConnection)*
               'ioConnections:' '-' IOConnection ('-' IOConnection)*
               ('endpoint:' Endpoint)?
               ('settings:' '-' Setting ('-' Setting)*)?
               'end'

PowerConnection ::= ID '--' ID

IOConnection ::= GPIOConnection | I2CConnection | SPIConnection | UARTConnection

GPIOConnection ::= 'type:' 'gpio'
                   ('name:' ID)?
                   (GPIOMode)?
                   'pin:' ID '--' ID

GPIOMode ::= ('input:' BOOL)?
             ('output:' BOOL)?
             ('pullup:' BOOL)?
             ('pulldown:' BOOL)?
             ('open_drain:' BOOL)?

I2CConnection ::= 'type:' 'i2c'
                  ('name:' ID)?
                  'slave_address:' '0x' HexInt
                  'pins:'
                  'sda:' ID '--' ID
                  'scl:' ID '--' ID

SPIConnection ::= 'type:' 'spi'
                  ('name:' ID)?
                  'pins:'
                  'mosi:' ID '--' ID
                  'miso:' ID '--' ID
                  'sck:' ID '--' ID
                  'cs:' ID '--' ID

UARTConnection ::= 'type:' 'uart'
                   ('name:' ID)?
                   'pins:'
                   'tx:' ID '--' ID
                   'rx:' ID '--' ID
                   'baudrate:' INT

(* Endpoint *)
Endpoint ::= ('topic:' STRING)?
             ('type:' EndpointType)?

EndpointType ::= 'Publisher' | 'Subscriber' | 'RPC' | 'Action'

(* Message Broker *)
Broker ::= MQTTBroker | AMQPBroker | RedisBroker

MQTTBroker ::= 'Broker<MQTT>' ID
               'host:' STRING
               'port:' INT
               ('ssl:' BOOL)?
               ('basePath:' STRING)?
               ('webPath:' STRING)?
               ('webPort:' INT)?
               ('auth:' Auth)?
               'end'

AMQPBroker ::= 'Broker<AMQP>' ID
               'host:' STRING
               'port:' INT
               ('vhost:' STRING)?
               ('topicExchange:' STRING)?
               ('rpcExchange:' STRING)?
               ('ssl:' BOOL)?
               ('auth:' Auth)?
               'end'

RedisBroker ::= 'Broker<Redis>' ID
                'host:' STRING
                'port:' INT
                ('db:' INT)?
                ('ssl:' BOOL)?
                ('auth:' Auth)?
                'end'

Auth ::= AuthPlain | AuthApiKey | AuthCert

AuthPlain ::= 'username:' STRING 'password:' STRING

AuthApiKey ::= 'key:' STRING

AuthCert ::= ('cert:' STRING) | ('certPath:' STRING)

(* Settings and Attributes *)
Setting ::= ID ':' Type ('=' Value)?
Attribute ::= ID ':' Type ('=' Value)?

Type ::= 'int' | 'float' | 'str' | 'bool' | 'list' | 'dict'

Value ::= INT | FLOAT | STRING | BOOL | List | Dict

List ::= '[' Value (',' Value)* ']'

Dict ::= '{' (ID ':' Setting) (',' ID ':' Setting)* '}'

(* Constraint *)
Constraint ::= 'max_frequency:' Number FreqUnit
             | 'min_distance:' Number DistUnit
             | 'max_distance:' Number DistUnit

DistUnit ::= 'm' | 'cm' | 'mm'

(* Lexical Elements *)
ID ::= Letter (Letter | Digit | '_')*
STRING ::= '"' (Char)* '"'
INT ::= Digit+
FLOAT ::= Digit+ '.' Digit+
BOOL ::= 'True' | 'False'
Number ::= INT | FLOAT
Letter ::= 'a'..'z' | 'A'..'Z'
Digit ::= '0'..'9'
HexDigit ::= '0'..'9' | 'a'..'f' | 'A'..'F'
```

---

## 4. Static Semantics

### 4.1 Well-Formedness Rules

#### Judgment Forms

```
Γ ⊢ d : ok                    (Device model d is well-formed in environment Γ)
Γ ⊢ c : Components            (Components c are well-formed)
Γ ⊢ k : Connection            (Connection k is well-formed)
Γ ⊢ pin₁ ~ pin₂ : PowerConn   (Power connection is valid)
Γ ⊢ pin₁ ~ pin₂ : IOConn      (IO connection is valid)
```

#### Environment

```
Γ ::= ∅                       (empty environment)
    | Γ, b : Board            (board binding)
    | Γ, p : Peripheral       (peripheral binding)
    | Γ, pin : Pin            (pin binding)
```

#### Device Well-Formedness

```
────────────────────────────────────────────────────────────────────── [T-Device]
Γ ⊢ m : Metadata    Γ ⊢ n : Network    Γ ⊢ c : Components
Γ ⊢ br : Option[Broker]    Γ, c ⊢ k₁ : Connection ... Γ, c ⊢ kₙ : Connection
────────────────────────────────────────────────────────────────────────────────
Γ ⊢ Device(m, n, c, br, [k₁, ..., kₙ]) : ok
```

#### Component Well-Formedness

```
────────────────────────────────────────────────────────────────── [T-Components]
Γ ⊢ b : Board    Γ ⊢ p₁ : Peripheral ... Γ ⊢ pₙ : Peripheral
∀i,j. i≠j ⇒ pᵢ.instanceName ≠ pⱼ.instanceName    (unique peripheral names)
─────────────────────────────────────────────────────────────────────────────────
Γ ⊢ Comp(b, [p₁, ..., pₙ]) : Components
```

#### Connection Well-Formedness

```
────────────────────────────────────────────────────────────────── [T-Connection]
Γ(c.board) = b : Board    Γ(k.peripheral) = p : Peripheral
∀pc ∈ k.powerConns. Γ ⊢ b.pins(pc.boardPin) ~ p.pins(pc.peripheralPin) : PowerConn
∀ioc ∈ k.ioConns. Γ ⊢ validateIOConn(ioc, b, p) : IOConn
Γ ⊢ k.endpoint : Option[Endpoint]
∀s ∈ k.settings. Γ ⊢ s : Setting
─────────────────────────────────────────────────────────────────────────────────
Γ ⊢ k : Connection
```

#### Power Connection Validation

```
─────────────────────────────────────────────────────────── [T-PowerConn-GND]
pin₁ : PowerPin(_, _, GND)    pin₂ : PowerPin(_, _, GND)
───────────────────────────────────────────────────────────────────────────────
Γ ⊢ pin₁ ~ pin₂ : PowerConn
```

```
────────────────────────────────────────────────────────── [T-PowerConn-VCC]
pin₁ : PowerPin(_, _, v₁)    pin₂ : PowerPin(_, _, v₂)
v₁ ≠ GND ∧ v₂ ≠ GND ∧ compatible(v₁, v₂)
───────────────────────────────────────────────────────────────────────────
Γ ⊢ pin₁ ~ pin₂ : PowerConn

where compatible(v₁, v₂) ≡ 
    (v₁ = v₂) ∨ 
    (v₁ = Custom(x) ∧ v₂ = Custom(y) ∧ |x - y| ≤ 0.5)
```

#### GPIO Connection Validation

```
──────────────────────────────────────────────────────────── [T-GPIO-Conn]
pin₁ : IOPin(_, _, funcs₁, _, _, _)    GPIO ∈ funcs₁
pin₂ : IOPin(_, _, funcs₂, _, _, _)    GPIO ∈ funcs₂
────────────────────────────────────────────────────────────────────────
Γ ⊢ GPIOConn(_, PC(pin₁.name, pin₂.name), _) : IOConn
```

#### I2C Connection Validation

```
───────────────────────────────────────────────────────────── [T-I2C-Conn]
pin₁ : IOPin(_, _, funcs₁, _, _, _)    ∃bus. SDA(bus) ∈ funcs₁
pin₂ : IOPin(_, _, funcs₂, _, _, _)    SDA(_) ∈ funcs₂
pin₃ : IOPin(_, _, funcs₃, _, _, _)    ∃bus. SCL(bus) ∈ funcs₃
pin₄ : IOPin(_, _, funcs₄, _, _, _)    SCL(_) ∈ funcs₄
0x00 ≤ addr ≤ 0x7F
──────────────────────────────────────────────────────────────────────────
Γ ⊢ I2CConn(_, addr, PC(pin₁.name, pin₂.name), PC(pin₃.name, pin₄.name)) : IOConn
```

#### Constraint Validation

```
───────────────────────────────────────────────────── [T-Constraint-Freq]
p : Peripheral    MaxFrequency(f, unit) ∈ p.constraints
────────────────────────────────────────────────────────────────────────
∀k. k.peripheral = p ⇒ k.settings.poll_rate ≤ toHz(f, unit)
```

### 4.2 Type Rules

#### Setting Type Checking

```
────────────────────── [T-IntSetting]
v : ℤ
────────────────────────────────────
Γ ⊢ IntSetting(n, Some(v)) : ok
```

```
────────────────────── [T-ListSetting]
v₁ : τ ... vₙ : τ
────────────────────────────────────────────────
Γ ⊢ ListSetting(n, Some([v₁, ..., vₙ])) : ok
```

```
───────────────────────────────────────────── [T-DictSetting]
Γ ⊢ s₁ : Setting ... Γ ⊢ sₙ : Setting
────────────────────────────────────────────────────────────
Γ ⊢ DictSetting(n, Some({k₁ ↦ s₁, ..., kₙ ↦ sₙ})) : ok
```

---

## 5. Operational Semantics

### 5.1 Runtime State

#### State Configuration

```
σ ∈ State ::= ⟨D, B, C, M⟩

D : DeviceState        (device runtime state)
B : BrokerState        (broker connection state)
C : ConnectionState    (peripheral connection states)
M : MessageQueue       (message queue)
```

#### Device State

```
DeviceState ::= {
    status: DeviceStatus,
    board: BoardState,
    peripherals: Map[ID, PeripheralState],
    network: NetworkState
}

DeviceStatus ::= Initializing | Running | Error(String) | Stopped

BoardState ::= {
    pins: Map[ID, PinState]
}

PinState ::= {
    value: Option[Value],
    direction: Option[Direction],
    mode: Option[Mode]
}

Direction ::= Input | Output
Mode ::= PullUp | PullDown | OpenDrain | Default
```

#### Peripheral State

```
PeripheralState ::= {
    status: PeripheralStatus,
    config: Map[String, Value],
    lastRead: Option[Value],
    lastWrite: Option[Value],
    timestamp: Time
}

PeripheralStatus ::= Idle | Reading | Writing | Error(String)
```

#### Broker State

```
BrokerState ::= {
    connected: Bool,
    subscriptions: Set[Topic],
    publications: Set[Topic]
}
```

#### Message Queue

```
MessageQueue ::= List[Message]

Message ::= Msg(
    topic: Topic,
    payload: Value,
    timestamp: Time,
    qos: QoS
)

QoS ::= QoS0 | QoS1 | QoS2
```

### 5.2 Transition Rules

#### Judgment Form

```
⟨σ, d⟩ ⟶ ⟨σ', d'⟩        (State σ with device d transitions to σ' with d')
```

#### Device Initialization

```
─────────────────────────────────────────────────────────────── [E-Init-Start]
d.meta.os = os    σ.D.status = Initializing
initBoard(d.components.board) = b'
initPeripherals(d.components.peripherals) = ps'
initNetwork(d.network) = n'
σ' = σ[D ↦ {status = Running, board = b', peripherals = ps', network = n'}]
───────────────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### Broker Connection

```
────────────────────────────────────────────────────────── [E-Broker-Connect]
d.broker = Some(br)    σ.B.connected = false
connect(br) = success
σ' = σ[B ↦ {connected = true, subscriptions = ∅, publications = ∅}]
──────────────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### Connection Establishment

```
──────────────────────────────────────────────────────── [E-Conn-Establish]
k ∈ d.connections    σ.D.status = Running
validatePowerConnections(k, σ.D.board) = success
configureIOConnections(k, σ.D.board) = σ'
──────────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### GPIO Read Operation

```
───────────────────────────────────────────────────────── [E-GPIO-Read]
k : Connection    k.ioConns contains GPIOConn(_, pc, mode)
p = k.peripheral    σ.D.peripherals(p.instanceName).status = Idle
readGPIO(pc.boardPin) = v
σ' = σ[D.peripherals(p.instanceName).lastRead ↦ v,
       D.peripherals(p.instanceName).timestamp ↦ now()]
─────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### GPIO Write Operation

```
───────────────────────────────────────────────────────── [E-GPIO-Write]
k : Connection    k.ioConns contains GPIOConn(_, pc, mode)
p = k.peripheral    v : Value
writeGPIO(pc.boardPin, v) = success
σ' = σ[D.peripherals(p.instanceName).lastWrite ↦ v,
       D.peripherals(p.instanceName).timestamp ↦ now()]
──────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### I2C Read Operation

```
────────────────────────────────────────────────────────── [E-I2C-Read]
k : Connection    k.ioConns contains I2CConn(_, addr, sda, scl)
p = k.peripheral    σ.D.peripherals(p.instanceName).status = Idle
i2cRead(addr, sda.boardPin, scl.boardPin) = data
σ' = σ[D.peripherals(p.instanceName).lastRead ↦ data,
       D.peripherals(p.instanceName).timestamp ↦ now()]
──────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### Message Publication

```
─────────────────────────────────────────────────────── [E-Msg-Publish]
k : Connection    k.endpoint = Some(EP(Some(topic), Some(Publisher)))
p = k.peripheral    σ.D.peripherals(p.instanceName).lastRead = Some(v)
σ.B.connected = true
msg = Msg(topic, v, now(), QoS0)
σ' = σ[M ↦ σ.M ++ [msg]]
publish(σ.B, msg) = success
───────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### Message Subscription

```
──────────────────────────────────────────────────────── [E-Msg-Subscribe]
k : Connection    k.endpoint = Some(EP(Some(topic), Some(Subscriber)))
σ.B.connected = true    topic ∉ σ.B.subscriptions
subscribe(σ.B, topic) = success
σ' = σ[B.subscriptions ↦ σ.B.subscriptions ∪ {topic}]
─────────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### Message Reception

```
─────────────────────────────────────────────────────────── [E-Msg-Receive]
k : Connection    k.endpoint = Some(EP(Some(topic), Some(Subscriber)))
p = k.peripheral    topic ∈ σ.B.subscriptions
msg = Msg(topic, v, t, qos) ∈ σ.M
processMessage(k, p, v) = σ''
σ' = σ''[M ↦ σ.M \ {msg}]
───────────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

#### Periodic Sensor Reading

```
─────────────────────────────────────────────────────────── [E-Periodic-Read]
k : Connection    p : Sensor = k.peripheral
k.settings contains IntSetting("poll_rate", Some(rate))
now() - σ.D.peripherals(p.instanceName).timestamp ≥ 1/rate
⟨σ, d⟩ ⟶[E-GPIO-Read or E-I2C-Read] ⟨σ₁, d⟩
⟨σ₁, d⟩ ⟶[E-Msg-Publish] ⟨σ', d⟩
────────────────────────────────────────────────────────────────────────────
⟨σ, d⟩ ⟶ ⟨σ', d⟩
```

---

## 6. Axiomatic Semantics

### 6.1 Hoare Logic for Device Operations

#### Assertion Language

```
P, Q ∈ Assertion ::= true | false
                    | P ∧ Q | P ∨ Q | ¬P | P ⇒ Q
                    | ∀x. P | ∃x. P
                    | σ.D.status = s
                    | σ.B.connected = b
                    | σ.D.peripherals(p).lastRead = v
                    | compatible(pin₁, pin₂)
                    | validConnection(k)
                    | inRange(v, min, max)
```

### 6.2 Device Initialization Axioms

```
────────────────────────────────────────────────────── [Ax-Init]
{ σ.D.status = Initializing ∧ wellFormed(d) }
  initDevice(d)
{ σ.D.status = Running ∧ 
  ∀p ∈ d.components.peripherals. 
    σ.D.peripherals(p.instanceName).status = Idle }
```

### 6.3 Connection Establishment Axioms

```
─────────────────────────────────────────────────────────────── [Ax-Power-Conn]
{ validPowerConnection(k, pc) ∧ 
  compatible(boardPin(pc), peripheralPin(pc)) }
  establishPowerConnection(k, pc)
{ powerConnected(pc) ∧ 
  voltage(peripheralPin(pc)) = voltage(boardPin(pc)) }
```

```
──────────────────────────────────────────────────────────── [Ax-GPIO-Conn]
{ validGPIOConnection(k, gc) ∧ 
  hasFunction(boardPin(gc), GPIO) ∧ 
  hasFunction(peripheralPin(gc), GPIO) }
  establishGPIOConnection(k, gc)
{ gpioConnected(gc) ∧ 
  ∀v. write(boardPin(gc), v) ⇒ read(peripheralPin(gc)) = v }
```

```
───────────────────────────────────────────────────────────── [Ax-I2C-Conn]
{ validI2CConnection(k, ic) ∧ 
  hasFunction(ic.sda.boardPin, SDA) ∧ 
  hasFunction(ic.scl.boardPin, SCL) ∧ 
  0x00 ≤ ic.slaveAddr ≤ 0x7F }
  establishI2CConnection(k, ic)
{ i2cConnected(ic) ∧ 
  canCommunicate(ic.slaveAddr, ic.sda, ic.scl) }
```

### 6.4 Message Broker Axioms

```
──────────────────────────────────────────────────────── [Ax-Broker-Connect]
{ ¬σ.B.connected ∧ reachable(broker.host, broker.port) ∧
  validAuth(broker.auth) }
  connect(broker)
{ σ.B.connected ∧ authenticated(σ.B) }
```

```
─────────────────────────────────────────────────────── [Ax-Publish]
{ σ.B.connected ∧ k.endpoint.type = Publisher ∧
  k.endpoint.topic = topic ∧ validValue(v) }
  publish(topic, v)
{ ∃msg ∈ σ.M. msg.topic = topic ∧ msg.payload = v ∧
  topic ∈ σ.B.publications }
```

```
──────────────────────────────────────────────────────── [Ax-Subscribe]
{ σ.B.connected ∧ k.endpoint.type = Subscriber ∧
  k.endpoint.topic = topic }
  subscribe(topic)
{ topic ∈ σ.B.subscriptions ∧
  ∀msg. msg.topic = topic ⇒ willReceive(msg) }
```

### 6.5 Sensor Reading Axioms

```
───────────────────────────────────────────────────────── [Ax-Sensor-Read]
{ p : Sensor ∧ σ.D.peripherals(p.instanceName).status = Idle ∧
  validConnection(k, p) ∧ powerConnected(k) }
  readSensor(p)
{ ∃v. σ.D.peripherals(p.instanceName).lastRead = Some(v) ∧
  satisfiesConstraints(v, p.constraints) }
```

```
────────────────────────────────────────────────────────── [Ax-Range-Check]
{ p : Sensor ∧ 
  MinDistance(dₘᵢₙ, unit) ∈ p.constraints ∧
  MaxDistance(dₘₐₓ, unit) ∈ p.constraints ∧
  σ.D.peripherals(p.instanceName).lastRead = Some(v) }
  validateReading(v, p)
{ toUnit(dₘᵢₙ, unit) ≤ v ≤ toUnit(dₘₐₓ, unit) }
```

### 6.6 Actuator Control Axioms

```
───────────────────────────────────────────────────────────── [Ax-Actuator-Write]
{ a : Actuator ∧ σ.D.peripherals(a.instanceName).status = Idle ∧
  validConnection(k, a) ∧ powerConnected(k) ∧
  validValue(v) }
  writeActuator(a, v)
{ σ.D.peripherals(a.instanceName).lastWrite = Some(v) ∧
  actuatorState(a) = v }
```

### 6.7 Invariants

#### Global Invariants

```
Inv-Device-Status:
  σ.D.status = Running ⇒ 
    (∀p ∈ peripherals. σ.D.peripheral(p).status ∈ {Idle, Reading, Writing})

Inv-Power-Compatibility:
  ∀k ∈ connections, pc ∈ k.powerConns.
    powerConnected(pc) ⇒ compatible(boardPin(pc), peripheralPin(pc))

Inv-Unique-Pins:
  ∀k₁, k₂ ∈ connections, k₁ ≠ k₂.
    usedPins(k₁) ∩ usedPins(k₂) = ∅

Inv-Broker-Connection:
  (∃k. k.endpoint.type ∈ {Publisher, Subscriber}) ⇒ 
    (broker ≠ None ∧ σ.B.connected)

Inv-Message-Delivery:
  topic ∈ σ.B.subscriptions ∧ msg.topic = topic ∧ msg ∈ σ.M ⇒ 
    ◊(msg will be processed)

Inv-Constraint-Satisfaction:
  ∀p : Sensor, v = σ.D.peripherals(p).lastRead.
    satisfiesConstraints(v, p.constraints)
```

#### Connection-Specific Invariants

```
Inv-I2C-Address:
  ∀k : Connection, ic : I2CConn ∈ k.ioConns.
    0x00 ≤ ic.slaveAddr ≤ 0x7F

Inv-UART-Baudrate:
  ∀k : Connection, uc : UARTConn ∈ k.ioConns.
    uc.baudrate ∈ {9600, 19200, 38400, 57600, 115200, ...}

Inv-GPIO-Direction:
  ∀k : Connection, gc : GPIOConn ∈ k.ioConns.
    (gc.mode.output = true ⇒ gc.mode.input = false) ∨
    (gc.mode.input = true ⇒ gc.mode.output = false)
```

---

## 7. Type System

### 7.1 Type Judgments

```
Γ ⊢ e : τ        (Expression e has type τ in environment Γ)
```

### 7.2 Base Types

```
τ ∈ Type ::= Int | Float | String | Bool 
           | List[τ] | Dict[String, τ]
           | Board | Peripheral | Connection
           | Pin | Broker | Network
           | Unit
```

### 7.3 Typing Rules

```
───────────────── [T-Int]
Γ ⊢ n : Int
```

```
───────────────── [T-Float]
Γ ⊢ f : Float
```

```
───────────────── [T-String]
Γ ⊢ s : String
```

```
───────────────── [T-Bool]
Γ ⊢ b : Bool
```

```
───────────────────────────────── [T-List]
Γ ⊢ e₁ : τ ... Γ ⊢ eₙ : τ
─────────────────────────────────────────
Γ ⊢ [e₁, ..., eₙ] : List[τ]
```

```
──────────────────────────────────────────────── [T-Dict]
Γ ⊢ e₁ : τ ... Γ ⊢ eₙ : τ
────────────────────────────────────────────────────────
Γ ⊢ {k₁: e₁, ..., kₙ: eₙ} : Dict[String, τ]
```

```
──────────────────────────────── [T-Board-Ref]
Γ(b) = Board
─────────────────────────────────────────
Γ ⊢ b : Board
```

```
────────────────────────────────────── [T-Peripheral-Ref]
Γ(p) = Peripheral
─────────────────────────────────────────────────
Γ ⊢ p : Peripheral
```

### 7.4 Subtyping

```
τ <: τ        (Reflexivity)

τ₁ <: τ₂    τ₂ <: τ₃
────────────────────    (Transitivity)
τ₁ <: τ₃

Int <: Float    (Numeric widening)

Custom(v) <: V3_3    if |v - 3.3| ≤ 0.5
Custom(v) <: V5      if |v - 5.0| ≤ 0.5
```

---

## 8. Verification Conditions

### 8.1 Safety Properties

```
Safety-No-Short-Circuit:
  ∀k ∈ connections, pc₁, pc₂ ∈ k.powerConns.
    pc₁.boardPin ≠ pc₂.boardPin ∧ 
    ¬(powerType(pc₁) = GND ∧ powerType(pc₂) ≠ GND ∧ 
      connectedTo(pc₁.boardPin, pc₂.boardPin))

Safety-Voltage-Limits:
  ∀k ∈ connections, p = k.peripheral.
    voltage(p) ≤ p.vcc.toVolts() ∧
    (p.ioVcc ≠ None ⇒ ioVoltage(p) ≤ p.ioVcc.toVolts())

Safety-Pin-Capacity:
  ∀k ∈ connections, pin ∈ usedPins(k).
    currentDraw(pin) ≤ maxCurrent(pin)

Safety-I2C-Address-Unique:
  ∀k₁, k₂ ∈ connections, k₁ ≠ k₂,
   ic₁ : I2CConn ∈ k₁.ioConns, ic₂ : I2CConn ∈ k₂.ioConns.
    sameBus(ic₁, ic₂) ⇒ ic₁.slaveAddr ≠ ic₂.slaveAddr
```

### 8.2 Liveness Properties

```
Liveness-Message-Delivery:
  □◊(∀msg ∈ σ.M. msg.topic ∈ σ.B.subscriptions ⇒ 
     ◊(msg will be delivered))

Liveness-Sensor-Reading:
  □(∀p : Sensor, k : Connection.
    k.peripheral = p ∧ k.settings.poll_rate = r ⇒
      ◊≤1/r(readSensor(p)))

Liveness-Broker-Reconnect:
  □(σ.B.connected = false ∧ broker ≠ None ⇒ 
     ◊(attemptReconnect(broker)))
```

### 8.3 Correctness Conditions

```
Correctness-Topic-Generation:
  ∀k : Connection.
    k.endpoint.topic = None ⇒
      k.endpoint.topic = generateTopic(device.meta.name, 
                                       k.peripheral.type,
                                       k.peripheral.msg,
                                       k.peripheral.instanceName)

Correctness-Pin-Function:
  ∀k : Connection, ioc : IOConn ∈ k.ioConns.
    requiredFunctions(ioc) ⊆ availableFunctions(boardPins(ioc))

Correctness-Constraint-Satisfaction:
  ∀p : Peripheral, c ∈ p.constraints, k : Connection.
    k.peripheral = p ⇒ satisfies(k.settings, c)
```

### 8.4 Well-Formedness Conditions

```
WF-All-Peripherals-Connected:
  ∀p ∈ components.peripherals.
    ∃k ∈ connections. k.peripheral = p

WF-Board-Referenced:
  ∀k ∈ connections.
    k.board = components.board

WF-Pin-Exists:
  ∀k ∈ connections, pc ∈ k.powerConns ∪ ioConns.
    pc.boardPin ∈ board.pins.map(_.name) ∧
    pc.peripheralPin ∈ k.peripheral.pins.map(_.name)

WF-Settings-Match-Attributes:
  ∀k ∈ connections, s ∈ k.settings.
    s.name ∈ k.peripheral.attributes.map(_.name)
```

---

## Summary

This formal semantics provides:

1. **Abstract Syntax**: Mathematical representation of DeMoL constructs
2. **Formal Grammar**: EBNF specification of concrete syntax
3. **Static Semantics**: Well-formedness and type checking rules
4. **Operational Semantics**: Runtime behavior via transition systems
5. **Axiomatic Semantics**: Hoare logic specifications and invariants
6. **Type System**: Type judgments and subtyping relations
7. **Verification Conditions**: Safety, liveness, and correctness properties

This formalization enables:
- **Verification**: Proving correctness of device models
- **Code Generation**: Sound translation to target platforms
- **Validation**: Checking compliance with constraints
- **Reasoning**: Understanding device behavior formally
