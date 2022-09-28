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
    echo $2
    aws s3 cp $2 ./input
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

# Future....replace placeholder with CRID, bad practice runs twice first the foldername is changed then the files...
# should only be needed for AVIRIS data, CRID can be used when renaming DESIS and PRISMA imagery
# maybe not needed can pass CRID pge script and use for AVIRIS renaming
#find . -iname "*_000*" | rename 's/\_000/\_CRID/g';
#find . -iname "*_000*" | rename 's/\_000/\_CRID/g';

cd output
out_dir=$(ls ./)
tar -czvf ${out_dir}.tar.gz ${out_dir}

# Create metadata
python ${imgspec_dir}/generate_metadata.py */*RDN*.hdr .

# Create quicklook
python ${imgspec_dir}/generate_quicklook.py $(ls input/*/*RDN* | grep -v '.hdr') .


rm -r ${out_dir}
