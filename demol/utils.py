import os
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers
from textx import get_location, TextXSemanticError
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
