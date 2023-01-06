#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTER
Space-based Imaging Spectroscopy and Thermal PathfindER
Author: Adam Chlus
"""

import sys
import json


def main():

    inputs_json  = sys.argv[1]

    with open(inputs_json, 'r') as in_file:
        inputs =json.load(in_file)

    run_config = {"inputs":{}}

    for file_dict in inputs["file"]:
        for key,value in file.items():
            run_config["inputs"][key] = value

    for key,value in inputs['config'].items():
        run_config["inputs"][key] = value


if __name__=='__main__':
    main()
