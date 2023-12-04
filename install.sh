# Need to do custom install to prevent dependency errors
conda create -y --name sister python=3.8
source activate sister
conda install -y gdal
pip install pystac==1.8.4

git clone -b 1.3.1 https://github.com/EnSpec/sister.git
pushd sister
pip install .
popd

git clone -b 1.5.0 https://github.com/EnSpec/hytools.git
pushd hytools
pip install .
popd