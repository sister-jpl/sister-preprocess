#!/bin/bash

source activate sister

ls -l

pwd

echo "Creating runconfig"
python generate_runconfig.py inputs.json

echo "Running L1 Preprocess PGE"
python l1_preprocess.py runconfig.json
