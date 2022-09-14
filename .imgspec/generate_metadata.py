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

import sys
import os
import json
import hytools as ht

def main():

    img = ht.HyTools(sys.argv[1])
    output_dir = sys.argv[2]

    img = ht.HyTools()
    header = img.get_header()

    metadata = {}
    metadata['sensor'] = header['sensor type'].upper()
    metadata['start_time'] = header['start acquisition time'].upper()
    metadata['end_time'] = header['end acquisition time'].upper()
    metadata['spatial_bounds'] = {}
    metadata['spatial_bounds']['latitude_min'] = float(header['latitude min'])
    metadata['spatial_bounds']['latitude_max'] = float(header['latitude max'])
    metadata['spatial_bounds']['longitude_min'] = float(header['longitude min'])
    metadata['spatial_bounds']['longitude_max'] = float(header['longitude max'])
    metadata['product'] = img.base_name.split('_')[4]
    metadata['processing_level'] = img.base_name.split('_')[3]

    config_file = '%s/%s.met.json' % (output_dir,img.base_name)

    with open(config_file, 'w') as outfile:
        json.dump(metadata,outfile,indent=3)


if __name__=='__main__':

    main()
