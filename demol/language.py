from textx import language

from .utils import (
    get_device_metamodel, get_device_model,
    get_synthesis_metamodel, get_synthesis_model
)



@language('devices', '*.hwd')
def devices_language():
    return get_device_metamodel()


@language('device-synthesis', '*.synth')
def device_synthesis_language():
    return get_synthesis_metamodel()
