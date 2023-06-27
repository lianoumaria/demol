import os
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers
from .definitions import *


def create_output_dirs(out_dir: str):
    diagrams_dir = os.path.join(out_dir, DIAGRAMS_DIRNAME)
    if not os.path.exists(diagrams_dir):
        # If it doesn't exist, create it
        os.makedirs(diagrams_dir)
    riot_src_dir = os.path.join(out_dir, RIOT_SOURCE_DIRNAME)
    if not os.path.exists(riot_src_dir):
        # If it doesn't exist, create it
        os.makedirs(riot_src_dir)


def get_device_metamodel():
    # Get meta-model from language description
    mm= metamodel_from_file(
        os.path.join(METAMODEL_REPO_PATH, 'devices.tx'),
        global_repository=True,
        debug=False
    )

    mm.register_scope_providers(
        {
            "*.*": scoping_providers.FQNImportURI(
                importAs=True,
            )
        }
    )
    mm.register_obj_processors({
        # EMPTY
    })

    return mm


def get_synthesis_metamodel():
    mm= metamodel_from_file(
        os.path.join(METAMODEL_REPO_PATH, 'synthesis.tx'),
        global_repository=True,
        debug=False
    )

    mm.register_scope_providers(
        {
            # "*.*": scoping_providers.FQNImportURI(
            #     importAs=True,
            # ),
            "Connection.board": scoping_providers.FQNGlobalRepo(
                os.path.join(BOARD_MODEL_REPO_PATH, '*.hwd')
            ),
            "Connection.peripheral": scoping_providers.FQNGlobalRepo(
                os.path.join(PERIPHERAL_MODEL_REPO_PATH, '*.hwd')
            ),
        }
    )
    mm.register_obj_processors({
        # EMPTY
    })

    return mm


def get_device_model(model_path):
    return get_device_metamodel().model_from_file(model_path)


def get_synthesis_model(model_path):
    return get_connection_metamodel().model_from_file(model_path)

def build_device_model(moel_path):
    return get_device_model(model_path)

def build_synthesis_model(moel_path):
    return get_device_model(model_path)
