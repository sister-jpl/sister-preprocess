# Need to do custom install to prevent dependency errors
conda create -y --name sister python=3.8
source activate sister
conda install -y gdal

git clone -b 1.3.1 https://github.com/EnSpec/sister.git
cd sister
pip install .

git clone -b 1.5.0 https://github.com/EnSpec/hytools.git
cd hytools
pip install .
