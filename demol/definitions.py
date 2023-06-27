"""paths"""

import os

THIS_DIR_PATH = os.path.dirname(__file__)

REPO_PATH = os.path.abspath(os.getcwd())
CODE_PATH = REPO_PATH + "/demol"
SUPPORTED_DEVICES = CODE_PATH + "/supported_devices/"
META_MODELS = CODE_PATH + "/meta-models/"
TEMPLATES = CODE_PATH + "/templates/"
RIOT_SOURCE_DIRNAME = "src"
DIAGRAMS_DIRNAME = 'diagrams'
METAMODEL_REPO_PATH=os.path.join(THIS_DIR_PATH, 'meta-models')
DEVICES_MODEL_REPO_PATH=os.getenv("DEVICES_MODEL_REPO_PATH",
                                  os.path.join(THIS_DIR_PATH, 'supported_devices'))
BOARD_MODEL_REPO_PATH=os.getenv("BOARD_MODEL_REPO_PATH",
                                  os.path.join(THIS_DIR_PATH,
                                               'supported_devices',
                                               'boards')
                                )
PERIPHERAL_MODEL_REPO_PATH=os.getenv("PERIPHERAL_MODEL_REPO_PATH",
                                      os.path.join(THIS_DIR_PATH,
                                                   'supported_devices',
                                                   'peripherals')
                                    )
