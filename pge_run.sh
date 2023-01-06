#!/bin/bash

source activate sister

python generate_runconfig.py inputs.json

python l1_preprocess.py run_config.json
