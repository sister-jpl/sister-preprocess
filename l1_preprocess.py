#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTER
Space-based Imaging Spectroscopy and Thermal PathfindER
Author: Adam Chlus

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import glob
import os
from sister.sensors import prisma,aviris,desis
from hytools.io import parse_envi_header


def main():
    parser = argparse.ArgumentParser(description = "Convert PRISMA HDF to ENVI format")
    parser.add_argument('l1_file',help="Path to compressed input file", type = str)
    parser.add_argument('out_dir',help="Output directory", type = str)
    parser.add_argument('temp_dir',help="Temporary directory", type = str)
    parser.add_argument('resolution',help="Output resample resolution",type=int, default = 30)
    parser.add_argument('smile', nargs='?',help="Path to smile wavelengths", default = False)
    parser.add_argument('rad_coeff', nargs='?',help="Path to radiometric coeffs",default = False)
    parser.add_argument('landsat', nargs='?',help="Landsat reference file",default = False)

    args = parser.parse_args()
    base_name = os.path.basename(args.l1_file)

    aws_cop_url='https://copernicus-dem-30m.s3.amazonaws.com/'

    if base_name.startswith('PRS'):
        prisma.he5_to_envi(args.l1_file,args.out_dir,args.temp_dir,
                           aws_cop_url,
                           shift = args.smile,
                           rad_coeff =args.rad_coeff,
                           proj = True,
                           match=args.landsat)


        l1p_dir = glob.glob("%s/PRS*" % args.out_dir)[0]
        datetime =  "%sT%s" %  (base_name[31:39],base_name[39:45])
        sensor = 'PRISMA'

    elif base_name.startswith('ang') or base_name.startswith('f'):
        aviris.preprocess(args.l1_file,args.out_dir,args.temp_dir,
                          res = args.resolution)
        sensor = 'AVIRIS'

    elif base_name.startswith('DESIS'):
        desis.l1c_process(args.l1_file,args.out_dir,args.temp_dir,
                           aws_cop_url)

        l1p_dir = glob.glob("%s/DESIS*" % args.out_dir)[0]
        date = base_name[31:39]

        # Get starting time of image acquisition
        header_file = glob.glob(l1p_dir + "/*rdn_prj.hdr")[0]
        header = parse_envi_header(header_file)
        datetime =header['start acquisition time'].replace('-','').replace(':','')[:-1]
        sensor = 'DESIS'

    else:
        print('Unrecognized input sensor')


    #Rename DESIS and PRISMA output files
    if sensor in ['PRISMA','DESIS']:
        for file in glob.glob("%s/*" % l1p_dir):
            if 'loc' in file:
                product = 'LOC'
            elif 'obs' in file:
                product = 'OBS'
            else:
                product = 'RDN'

            ext = os.path.splitext(file)[-1]
            old_file = os.path.basename(file)
            new_file = "SISTER_%s_%s_L1B_%s_000%s" % (sensor,datetime,product,ext)
            os.rename("%s/%s" % (l1p_dir,old_file),
                      "%s/%s" % (l1p_dir,new_file))
        os.rename(l1p_dir,
                  "%s/SISTER_%s_%s_L1B_RDN_000" %  (os.path.dirname(l1p_dir),sensor,datetime))





if __name__=='__main__':

    main()
