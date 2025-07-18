import os
import sys
import argparse
import pydot
import shutil
import jinja2
import codecs

from demol.definitions import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

fsloader = jinja2.FileSystemLoader(TEMPLATES)
env = jinja2.Environment(loader=fsloader)

def gen_src_raspi(connection_model, device_models, out_dir):

    #Load the main function template
    template1 = env.get_template(
        'main.py.tmpl'
    )

    #THe following part was copied from riot_old i'll see if i acctually need it.
    peripheral_name_tmp = {}
    peripheral_type_tmp = {}
    id_tmp = {}
    frequency_tmp = {}
    module_tmp = {}
    args_tmp = {}
    topic_tmp = {}
    num_of_peripherals_tmp = len(connection_model.connections)

    # Transform the name in a convinient form with out '_'
    board_name_tmp = connection_model.connections[0].board.device
    if board_name_tmp == 'RaspberryPi_5':
        board_name_tmp = 'RaspberryPi-5'
    
    # Wifi credentials
    wifi_ssid_tmp = connection_model.connections[0].com_endpoint.wifi_ssid[:-1]
    wifi_passwd_tmp = connection_model.connections[0].com_endpoint.wifi_passwd[:-1]

    
