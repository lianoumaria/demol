from os.path import basename

from demol.lang import (
    get_device_mm,
    get_component_mm
)


def build_model(model_fpath):
    model_filename = basename(model_fpath)
    if model_filename.endswith('.hwd'):
        mm = get_component_mm()
    elif model_filename.endswith('.dev'):
        mm = get_device_mm()
    else:
        raise ValueError('Not a valid model extension.')
    model = mm.model_from_file(model_fpath)
    return model
