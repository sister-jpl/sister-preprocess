run_dir=$('pwd')
imgspec_dir=$(cd "$(dirname "$0")" ; pwd -P)
pge_dir=$(dirname ${imgspec_dir})

# Need to do custom install to prevent dependency errors
conda create -y --name sister python=3.8
source activate sister
conda install -y gdal

pip install -r ${pge_dir}/requirements.txt
