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
import sister
from sister.sensors import prisma,aviris,desis


args.l1_file = '/Users/achlus/data1/desis/raw/DESIS-HSI-L1C-DT0696263016_002-20220307T001904-V0215.zip'
args.out_dir = '/Users/achlus/data1/desis/rdn/'
args.temp_dir = '/Users/achlus/data1/temp/'

args.l1_file = '/Users/achlus/data1/prisma/raw/PRS_L1_STD_OFFL_20211003070847_20211003070852_0001.zip'
args.out_dir = '/Users/achlus/data1/prisma/rdn/'
args.temp_dir = '/Users/achlus/data1/temp/'



args.l1_file = '/Users/achlus/data1/ang/raw/ang20191027t204454.tar.gz'
args.out_dir = '/Users/achlus/data1/ang/rdn/'
args.temp_dir = '/Users/achlus/data1/temp/'
args.resolution = 30



def main():
    parser = argparse.ArgumentParser(description = "Convert PRISMA HDF to ENVI format")
    parser.add_argument('l1_file',help="Path to compressed input file", type = str)
    parser.add_argument('out_dir',help="Output directory", type = str)
    parser.add_argument('temp_dir',help="Temporary directory", type = str)
    parser.add_argument('resolution',help="Output resample resolution",type=int, default = 0)
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
        datetime = base_name[16:30]
        for file in glob.glob("%s/*" % l1p_dir):
            old_file = os.path.basename(file)
            new_file = ("prs%s_%s" % (datetime,old_file[39:])).replace('_prj','')
            os.rename("%s/%s" % (l1p_dir,old_file),
                      "%s/%s" % (l1p_dir,new_file))
        os.rename(l1p_dir,
                  "%s/prs%s_l1p/" %  (os.path.dirname(l1p_dir),datetime))


   elif base_name.startswith('ang') or base_name.startswith('f'):
        aviris.preprocess(args.l1_file,args.out_dir,args.temp_dir,
                          res = args.resolution)

    elif base_name.startswith('DESIS'):
        desis.l1c_process(args.l1_file,args.out_dir,args.temp_dir,
                           aws_cop_url)

        l1p_dir = glob.glob("%s/DESIS*" % args.out_dir)[0]
        datetime = base_name[31:46].replace('t','')
        for file in glob.glob("%s/*" % l1p_dir):
            old_file = os.path.basename(file)
            new_file = ("des%s_%s" % (datetime,old_file[45:])).replace('_prj','')
            os.rename("%s/%s" % (l1p_dir,old_file),
                      "%s/%s" % (l1p_dir,new_file))
        os.rename(l1p_dir,
                  "%s/des%s_l1p" %  (os.path.dirname(l1p_dir),datetime))



    else:
        print('Unrecognized input sensor')


if __name__=='__main__':

    main()
