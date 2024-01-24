#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTER
Space-based Imaging Spectroscopy and Thermal PathfindER
Author: Adam Chlus

"""

import datetime as dt
import glob
import os
import shutil
import sys
import tarfile
import json
import hytools as ht
from hytools.io import parse_envi_header, write_envi_header
import numpy as np
from PIL import Image
import pystac

import spectral.io.envi as envi

from sister.sensors import prisma,aviris,desis,emit
from sister.utils import download_file


def main():

    pge_path = os.path.dirname(os.path.realpath(__file__))

    run_config_json = sys.argv[1]

    with open(run_config_json, 'r') as in_file:
        run_config = json.load(in_file)

    base_name = os.path.basename(run_config['inputs']['raw_dataset'])

    experimental = run_config['inputs']['experimental']

    os.mkdir('output')
    os.mkdir('temp')

    aws_cop_url='https://copernicus-dem-30m.s3.amazonaws.com/'

    if base_name.startswith('PRS'):

        smile = f'{pge_path}/data/prisma/PRISMA_Mali1_wavelength_shift_surface_smooth.npz'
        rad_coeff = f'{pge_path}/data/prisma/PRS_Mali1_radcoeff_surface.npz'

        landsat_directory = os.path.dirname(run_config['inputs']['raw_dataset']).replace('raw', 'landsat_reference')
        landsat_url=f'{landsat_directory}/PRS_{base_name[16:50]}_landsat.tar.gz'
        os.mkdir('input')
        landsat_tar = 'input/%s' % os.path.basename(landsat_url)

        download_file(landsat_tar,
                      landsat_url)

        with tarfile.open(landsat_tar, 'r') as tar_ref:
            tar_ref.extractall('input')

        landsat = landsat_tar[:-7]

        prisma.he5_to_envi(run_config['inputs']['raw_dataset'],
                            'output/',
                            'temp/',
                            aws_cop_url,
                            shift = smile,
                            rad_coeff =rad_coeff,
                            proj = True,
                            match=landsat)

        l1p_dir = glob.glob('output/PRS*')[0]
        datetime = '%sT%s' %  (base_name[16:24],base_name[24:30])
        sensor = 'PRISMA'

    elif base_name.startswith('ang') or base_name.startswith('f'):
        aviris.preprocess(run_config['inputs']['raw_dataset'],
                            'output/',
                            'temp/',
                            res = 30)
        l1p_dir = glob.glob('output/S*')[0]
        sensor = os.path.basename(l1p_dir).split('_')[1]

    elif base_name.startswith('DESIS'):
        desis.l1c_process(run_config['inputs']['raw_dataset'],
                            'output/',
                            'temp/',
                            aws_cop_url)

        l1p_dir = glob.glob('output/DESIS*')[0]

        # Get starting time of image acquisition
        header_file = glob.glob(l1p_dir + '/*rdn_prj.hdr')[0]
        header = parse_envi_header(header_file)
        datetime =(header['start acquisition time'].replace('-','').replace(':','')[:-1]).upper()
        sensor = 'DESIS'

    elif base_name.startswith('EMIT'):

        emit_directory = os.path.dirname(run_config['inputs']['raw_dataset'])
        obs_base_name = base_name.replace('RAD','OBS')
        obs_url = f'{emit_directory}/{obs_base_name}'
        os.mkdir('input')
        obs_nc = f'input/{obs_base_name}'

        download_file(obs_nc,
                      obs_url)

        emit.nc_to_envi(run_config['inputs']['raw_dataset'],
                            'output/',
                            'temp/',
                            obs_file = obs_nc,
                            export_loc = True,
                            crid = str(run_config['inputs']['crid']))
        sensor = 'EMIT'
    else:
        print("Unrecognized input sensor")

    #Rename DESIS and PRISMA output files
    if sensor in ['PRISMA','DESIS']:
        for file in glob.glob('%s/*' % l1p_dir):
            if ('loc' in file) & ('.csv' not in file):
                product = '_LOC'
            elif 'obs' in file:
                product = '_OBS'
            elif'rdn' in file:
                product = ''
            else:
                continue
            ext = os.path.splitext(file)[-1]
            if ext == '':
                ext = '.bin'

            old_file = os.path.basename(file)
            new_file = f'SISTER_{sensor}_L1B_RDN_{datetime}_CRID{product}{ext}'

            os.rename('%s/%s' % (l1p_dir,old_file),
                      'output/%s' % (new_file))
        shutil.rmtree(l1p_dir)

    #Update crid
    for file in glob.glob("output/SISTER*"):
        os.rename(file,file.replace('CRID',
                                        str(run_config['inputs']['crid'])))

    # If experimental, prefix filenames with "EXPERIMENTAL-" and update ENVI .hdr descriptions
    disclaimer = ""
    if experimental:
        disclaimer = "(DISCLAIMER: THIS DATA IS EXPERIMENTAL AND NOT INTENDED FOR SCIENTIFIC USE) "
        for file in glob.glob(f"output/SISTER*"):
            shutil.move(file, f"output/EXPERIMENTAL-{os.path.basename(file)}")
        for hdr_file in glob.glob(f"output/*SISTER*hdr"):
            update_experimental_hdr_files(hdr_file)

    rdn_file = glob.glob("output/*%s.bin" % run_config['inputs']['crid'])[0]
    generate_quicklook(rdn_file, 'output/')
    rdn_basename = os.path.basename(rdn_file)[:-4]

    output_runconfig_path = f'output/{rdn_basename}.runconfig.json'
    shutil.copyfile(run_config_json, output_runconfig_path)

    output_log_path = f'output/{rdn_basename}.log'
    if os.path.exists("pge_run.log"):
        shutil.copyfile('pge_run.log', output_log_path)

    # Generate STAC
    catalog = pystac.Catalog(id=rdn_basename,
                             description=f'{disclaimer}This catalog contains the output data products of the SISTER '
                                         f'preprocessing PGE, including radiance, location data, and observation '
                                         f'parameters. Execution artifacts including the runconfig file and execution '
                                         f'log file are included with the radiance data.')

    # Add items for data products
    hdr_files = glob.glob("output/*SISTER*.hdr")
    hdr_files.sort()
    for hdr_file in hdr_files:
        metadata = generate_stac_metadata(hdr_file)
        assets = {
            "envi_binary": f"./{os.path.basename(hdr_file.replace('.hdr', '.bin'))}",
            "envi_header": f"./{os.path.basename(hdr_file)}"
        }
        # If it's the radiance product, then add png, runconfig, and log
        if os.path.basename(hdr_file) == f"{rdn_basename}.hdr":
            png_file = hdr_file.replace(".hdr", ".png")
            assets["browse"] = f"./{os.path.basename(png_file)}"
            assets["runconfig"] = f"./{os.path.basename(output_runconfig_path)}"
            if os.path.exists(output_log_path):
                assets["log"] = f"./{os.path.basename(output_log_path)}"
        item = create_item(metadata, assets)
        catalog.add_item(item)

    # set catalog hrefs
    catalog.normalize_hrefs(f"./output/{rdn_basename}")

    # save the catalog
    catalog.describe()
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print("Catalog HREF: ", catalog.get_self_href())
    # print("Item HREF: ", item.get_self_href())

    # Move the assets from the output directory to the stac item directories and create empty .met.json files
    for item in catalog.get_items():
        for asset in item.assets.values():
            fname = os.path.basename(asset.href)
            shutil.move(f"output/{fname}", f"output/{rdn_basename}/{item.id}/{fname}")
        with open(f"output/{rdn_basename}/{item.id}/{item.id}.met.json", mode="w"):
            pass


def generate_quicklook(input_file,output_dir):

    img = ht.HyTools()
    img.read_file(input_file)
    image_file =f"{output_dir}/{img.base_name}.png"

    if 'DESIS' in img.base_name:
        band3 = img.get_wave(560)
        band2 = img.get_wave(850)
        band1 = img.get_wave(660)
    else:
        band3 = img.get_wave(560)
        band2 = img.get_wave(850)
        band1 = img.get_wave(1660)

    rgb=  np.stack([band1,band2,band3])
    rgb[rgb == img.no_data] = np.nan

    rgb = np.moveaxis(rgb,0,-1).astype(float)
    bottom = np.nanpercentile(rgb,5,axis = (0,1))
    top = np.nanpercentile(rgb,95,axis = (0,1))
    rgb = np.clip(rgb,bottom,top)
    rgb = (rgb-np.nanmin(rgb,axis=(0,1)))/(np.nanmax(rgb,axis= (0,1))-np.nanmin(rgb,axis= (0,1)))
    rgb = (rgb*255).astype(np.uint8)

    im = Image.fromarray(rgb)
    im.save(image_file)


def update_experimental_hdr_files(header_file):

    header = parse_envi_header(header_file)
    header['description'] = "(DISCLAIMER: THIS DATA IS EXPERIMENTAL AND NOT INTENDED FOR SCIENTIFIC USE) " + \
                                header['description'].capitalize()
    write_envi_header(header_file, header)


def generate_stac_metadata(header_file):

    header = envi.read_envi_header(header_file)
    base_name = os.path.basename(header_file)[:-4]

    metadata = {}
    metadata['id'] = base_name
    metadata['start_datetime'] = dt.datetime.strptime(header['start acquisition time'], "%Y-%m-%dt%H:%M:%Sz")
    metadata['end_datetime'] = dt.datetime.strptime(header['end acquisition time'], "%Y-%m-%dt%H:%M:%Sz")
    # Split corner coordinates string into list
    coords = [float(x) for x in header['bounding box'].replace(']', '').replace('[', '').split(',')]
    geometry = [list(x) for x in zip(coords[::2], coords[1::2])]
    # Add first coord to the end of the list to close the polygon
    geometry.append(geometry[0])
    metadata['geometry'] = {
        "type": "Polygon",
        "coordinates": geometry
    }
    base_tokens = base_name.split('_')
    metadata['collection'] = f"SISTER_{base_tokens[1]}_{base_tokens[2]}_{base_tokens[3]}_{base_tokens[5]}"
    product = base_tokens[3]
    if "LOC" in base_name:
        product += "_LOC"
    if "OBS" in base_name:
        product += "_OBS"
    metadata['properties'] = {
        'sensor': base_tokens[1],
        'description': header['description'],
        'product': product,
        'processing_level': base_tokens[2]
    }
    return metadata


def create_item(metadata, assets):
    item = pystac.Item(
        id=metadata['id'],
        datetime=metadata['start_datetime'],
        start_datetime=metadata['start_datetime'],
        end_datetime=metadata['end_datetime'],
        geometry=metadata['geometry'],
        collection=metadata['collection'],
        bbox=None,
        properties=metadata['properties']
    )
    # Add assets
    for key, href in assets.items():
        item.add_asset(key=key, asset=pystac.Asset(href=href))
    return item


if __name__=='__main__':

    main()
