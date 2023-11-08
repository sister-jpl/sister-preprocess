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
    parser.add_argument('--raw_dataset', help='Path to raw dataset')
    parser.add_argument('--crid', help='CRID value')
    args = parser.parse_args()

    run_config = {
        "inputs": {
            "raw_dataset": args.raw_dataset,
            "crid": args.crid
        }
    }
    run_config["inputs"]["experimental"] = True if args.experimental == "True" else False

    config_file = 'runconfig.json'

    with open(config_file, 'w') as outfile:
        json.dump(run_config, outfile, indent=4)


if __name__=='__main__':
    main()
