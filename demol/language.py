from textx import language

from .utils import (
    get_device_metamodel,
    get_synthesis_metamodel
)



@language('demol-component', '*.hwd')
def devices_language():
    return get_device_metamodel()


@language('demol-device', '*.dev')
def device_synthesis_language():
    return get_synthesis_metamodel()
