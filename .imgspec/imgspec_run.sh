#!/bin/bash

imgspec_dir=$(cd "$(dirname "$0")" ; pwd -P)
pge_dir=$(dirname ${imgspec_dir})

source activate sister
mkdir output temp

input_file=input/*.*
input_file=$(ls input/*.* | tail -n 1)

echo $input_file
base=$(basename $input_file)

if [[ $base == PRS* ]]; then
    echo $1
    wget $1 -P ./input
    lst_archive=$(ls input/*landsat.tar.gz)
    tar -xzvf $lst_archive -C input/
    landsat=$(ls input/*landsat)
    rdn_coeffs=${pge_dir}/data/prisma/*_radcoeff_surface.npz
    smile=${pge_dir}/data/prisma/*_wavelength_shift_surface_smooth.npz
    prisma_zip=input/*.zip
    python ${pge_dir}/l1_preprocess.py $prisma_zip output/ temp/ 30 $smile $rdn_coeffs $landsat
    rm output/*/*.log
    rm output/*/*.csv

else
    python ${pge_dir}/l1_preprocess.py $input_file output/ temp/ 30
fi

cd output
out_dir=$(ls ./)
tar -czvf ${out_dir}.tar.gz ${out_dir}

# Create metadata
python ${imgspec_dir}/generate_metadata.py */*RDN*.hdr .
# Create quicklook
python ${imgspec_dir}/generate_quicklook.py $(ls */*RDN* | grep -v '.hdr') .

rm -r ${out_dir}

cp ../run.log ${out_dir}.log
