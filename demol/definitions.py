"""paths"""

import os

THIS_DIR_PATH = os.path.dirname(__file__)

#CURRENT_PATH = os.path.abspath(os.getcwd())
REPO_PATH = os.path.dirname(THIS_DIR_PATH)
CODE_PATH = os.path.join(REPO_PATH, "demol") #+ "/demol"
META_MODELS = os.path.join(CODE_PATH + "grammar")
CLASS_TEMPLATES = os.path.join(CODE_PATH , "templates", "sensor_classes")
TEMPLATES = os.path.join(CODE_PATH , "templates", "riot_old")
TEMPLATES_RASPI = os.path.join(CODE_PATH , "templates", "raspi_new")
RIOT_SOURCE_DIRNAME = "src"
DIAGRAMS_DIRNAME = 'diagrams'
METAMODEL_REPO_PATH=os.path.join(THIS_DIR_PATH, 'grammar')

DEVICES_MODEL_REPO_PATH=os.getenv(
    "DEVICES_MODEL_REPO_PATH",
    os.path.join(THIS_DIR_PATH, 'builtin_models')
)

BOARD_MODEL_REPO_PATH=os.getenv(
    "BOARD_MODEL_REPO_PATH",
    os.path.join(DEVICES_MODEL_REPO_PATH, 'boards')
)

PERIPHERAL_MODEL_REPO_PATH=os.getenv(
    "PERIPHERAL_MODEL_REPO_PATH",
    os.path.join(DEVICES_MODEL_REPO_PATH, 'peripherals')
)
