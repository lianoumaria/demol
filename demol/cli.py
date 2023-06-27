#!/usr/bin/env python

"""parser.py"""

# textX imports
from textx.export import metamodel_export, model_export, PlantUmlRenderer

from demol.generator import (
    gen_src_riot,
    generate_diagrams
)

from demol.utils import (
    get_device_model,
    get_connection_model,
    create_output_dirs
)

from os.path import join, dirname
from pathlib import Path
import os
import sys
import argparse
import pydot
import shutil

from demol.definitions import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)


def log(msg: str):
    print(f'[*] {msg}')


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("command", type=str)
    parser.add_argument("--model",
                        help="Model file path")

    parser.add_argument("--output",
                        default=os.path.join(os.getcwd(), 'gen'),
                        help="Output directory")

    return parser.parse_args()


def get_supported_boards():
    # Create a list of supported boards
    supported_boards = []
    directory = os.fsencode(SUPPORTED_DEVICES + 'boards')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".hwd"):
            supported_boards.append(filename[:-4])
            continue
        else:
            continue
    log(f'Supported boards: {supported_boards}')
    return supported_boards


def get_supported_peripherals():
    # Create a list of supported peripherals
    supported_peripherals = []
    directory = os.fsencode(SUPPORTED_DEVICES + 'peripherals')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".hwd"):
            supported_peripherals.append(filename[:-4])
            continue
        else:
            continue
    log(f'Supported peripherals: {supported_peripherals}')
    return supported_peripherals


def check_dependency_models(model, boards, peripherals):
    # Check if a hardware configuration file exists for each given board/peripheral
    all_hwd_exist = True
    for device in model.includes:
        # Construct device model from a specific file
        if device.name in boards:
            continue
        elif device.name in peripherals:
            continue
        else:
            print("No configuration file for device " + device.name + " found!")
            all_hwd_exist = False
    return all_hwd_exist


def main():
    cl_args = parse_args()
    conn_model_file = cl_args.model
    output_dir = cl_args.output

    if conn_model_file.endswith(".con"):
        connection_conf = conn_model_file.removesuffix('.con')
    else:
        sys.exit("Connection file should end with '.con'")

    supported_boards = get_supported_boards()
    supported_peripherals = get_supported_peripherals()

    # Construct connection model from a specific file
    connection_model = get_connection_model(
        'models/device/' + conn_model_file)

    create_output_dirs(output_dir)
    generate_diagrams(output_dir, connection_model)

    ret = check_dependency_models(connection_model, supported_boards,
                                  supported_peripherals)
    if ret == False:
        sys.exit("You need to create configuration (.hwd) file(s) "
                 "for the devices(s) mentioned above ...")

    device_models = {}

    # Create a model for each device used (board/peripheral)
    for device in connection_model.includes:

        # Construct device model from a specific file
        if device.name in supported_boards:
            device_models[device.name] = get_device_model(
                SUPPORTED_DEVICES + '/boards/' + device.name + '.hwd')
        elif device.name in supported_peripherals:
            device_models[device.name] = get_device_model(
                SUPPORTED_DEVICES + '/peripherals/' + device.name + '.hwd')

    gen_src_riot(connection_model, device_models, output_dir)


if __name__ == '__main__':
    main()
