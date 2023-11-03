#!/bin/bash

source activate sister

pge_dir=$(cd "$(dirname "$0")" ; pwd -P)

cat inputs.json

echo "Creating runconfig"
python ${pge_dir}/generate_runconfig.py "${@:1}"

echo "Running L1 Preprocess PGE"
python ${pge_dir}/preprocess.py runconfig.json
