from demol.mm_classes.utils import SClass

class CPU(SClass):
    def __init__(self, parent, cpu_family, max_freq, unit, fpu):
        self.parent = parent
        self.cpu_family = cpu_family
        self.max_freq = max_freq
        self.unit = unit
        self.fpu = fpu


class Memory(SClass):
    def __init__(self, parent, ram, rom, flash):
        self.parent = parent
        self.ram = ram
        self.rom = rom
        self.flash = flash


class PowerPin(SClass):
    def __init__(self, parent, name, number, ptype):
        self.parent = parent
        self.name = name
        self.number = number
        self.ptype = ptype


class IOPin(SClass):
    def __init__(self, parent, funcs, name, number, vmin, vmax, signalLevel):
        self.parent = parent
        self.funcs = funcs
        self.name = name
        self.number = number
        self.vmin = vmin
        self.vmax = vmax
        self.signalLevel = signalLevel


class GPIO(SClass):
    def __init__(self, parent, ptype):
        self.parent = parent
        self.ptype = ptype


class I2C(SClass):
    def __init__(self, parent, ptype, bus):
        self.parent = parent
        self.ptype = ptype
        self.bus = bus


class SPI(SClass):
    def __init__(self, parent, ptype, bus):
        self.parent = parent
        self.ptype = ptype
        self.bus = bus


class UART(SClass):
    def __init__(self, parent, ptype, bus):
        self.parent = parent
        self.ptype = ptype
        self.bus = bus


class PWM(SClass):
    def __init__(self, parent, ptype, channel):
        self.parent = parent
        self.ptype = ptype
        self.channel = channel


class ADC(SClass):
    def __init__(self, parent, ptype):
        self.parent = parent
        self.ptype = ptype

class DAC(SClass):
    def __init__(self, parent, ptype):
        self.parent = parent
        self.ptype = ptype
