#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTER
Space-based Imaging Spectroscopy and Thermal PathfindER
Author: Adam Chlus
"""

import argparse
import json


def main():
    """
        This function takes as input the path to an inputs.json file and exports a run config json
        containing the arguments needed to run the L1 preprocess PGE.

    """

    parser = argparse.ArgumentParser(description='Parse inputs to create runconfig.json')
    parser.add_argument('--radiance_data', help='Path to radiance data file')
    parser.add_argument('--radiance_header', help='Path to radiance header file')
    parser.add_argument('--observation_data', help='Path to observation data file')
    parser.add_argument('--observation_header', help='Path to observation header file')
    parser.add_argument('--location_data', help='Path to location data file')
    parser.add_argument('--location_header', help='Path to location header file')
    parser.add_argument('--glt_data', help='Path to GLT data file')
    parser.add_argument('--glt_header', help='Path to GLT header file')
    parser.add_argument('--crid', help='CRID value', default="000")
    parser.add_argument('--experimental', help='If true then designates data as experiemntal', default="True")
    args = parser.parse_args()

    run_config = {
        "inputs": {
            "radiance_data": args.radiance_data,
            "radiance_header": args.radiance_header,
            "observation_data": args.observation_data,
            "observation_header": args.observation_header,
            "location_data": args.location_data,
            "location_header": args.location_header,
            "glt_data": args.glt_data,
            "glt_header": args.glt_header,
            "crid": args.crid
        }
    }
    run_config["inputs"]["experimental"] = True if args.experimental.lower() == "true" else False

    config_file = 'runconfig.json'

    with open(config_file, 'w') as outfile:
        json.dump(run_config, outfile, indent=4)


if __name__=='__main__':
    main()
