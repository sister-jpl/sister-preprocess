# SISTER Preprocess PGE Documentation

## Description

The L1B preprocess PGE takes as input imaging spectroscopy datasets in their native formats and converts them to a common set of file types for downstream processing. Currently, preprocessing is supported for four sensors:

- AVIRIS Classic
- AVIRIS Next Generation
- DESIS
- PRISMA

Processing steps vary by sensor and are descibed below.

### AVIRIS Classic (AVCL)

---

Input data for AVCL is a tar'ed and gzipped archived containing multiple ENVI formated datasets, including radiance, geolocation and geometry data.

File example:

	f080709t01p00r15.tar.gz

Preprocessing of AVCL data includes application of radiance gains to generate radiance data in the units of microwatts per centimeter squared per steradian (μW/cm<sup>2</sup>/sr). Preprocessing of AVCL also includes optional spatial resampling. Spatial resampling is performed by aggregationg and averaging pixels to the closest resolution to the target resolution. For example, for a target pixel size of 30m and source pixel size of 16m, pixels will be averaged in 2x2 blocks of pixels for an output resolution of 30m.

![AVCL preprocess workflow](./figures/avcl_workflow.svg)

### AVIRIS Next Generation (AVNG)

---

Input data for AVNG is a tar'ed and gzipped archived containing multiple ENVI formated datasets, including radiance, geolocation and geometry data.

File example:

		ang20191027t204454.tar.gz

Preprocessing of AVNG also includes optional spatial resampling. Spatial resampling is performed by aggregationg and averaging pixels to the closest resolution to the target resolution. For example, for a target pixel size of 30m and source pixel size of 5.6m, pixel will be averaged in 5x5 blocks of pixels for an output resolution of 28m.

![AVng preprocess workflow](./figures/avng_workflow.svg)


### DESIS (DESIS)

---

DESIS L1C radiance data are provided by the German Space Agency (DLR) and Teledyne as a zipped archive containing radiance data in a GeoTIFF file along with metadata in an XML file.

Example file:

		DESIS-HSI-L1C-DT0700655132_004-20220317T070333-V0215.zip

Provided band gains and offsets are using to convert radiance data to physical units of μW/cm<sup>2</sup>/sr. Per-pixel sensor geometry data is not provided, instead a scene mean value is included in the metadata, this value is assigned to all pixels in the image. Per-pixel solar geometry is calculated at the start time of image collection. An elevation dataset is not provided with DESIS imagery and is generated during runtime. Copernicus DEM tiles that overlap the DESIS image extent are downloaded from AWS servers (['https://copernicus-dem-30m.s3.amazonaws.com/']('https://copernicus-dem-30m.s3.amazonaws.com/')), mosiacked and clipped to the geographic extent of the input dataset.

![DESIS preprocess workflow](./figures/desis_workflow.svg)

### PRISMA (PRISMA)

---

PRISMA L1 radiance data are provided by the Italian Space Agency (ASI) as a zipped HDF file containing unprojected radiance, pixel geolocation data and sensor and solar geometry data.

Example file:

		PRS_L1_STD_OFFL_20210204092812_20210204092816_0001.zip

Prior to data export a series of correction routines are applied to the dataset to improve geometric registration and radiometry. First a smile correction is applied by resampling the radiance data using a precalculated wavelength center array, next a pseudo flat field correction is applied to the radiance data using a precalculated array of radiometric adjustment coefficients. Using the input Landsat image as a reference image pixel coordinates are then adjusted using an image matching algorithm. An elevation dataset is not provided with PRISMA imagery and is generated during runtime. Copernicus DEM tiles that overlap the PRISMA image extent are downloaded from AWS servers (['https://copernicus-dem-30m.s3.amazonaws.com/']('https://copernicus-dem-30m.s3.amazonaws.com/')), mosiacked and clipped to the geographic extent of the input dataset. Finally all datasets are projected in the appropriate WGS84 UTM zone at a spatial resolution of 30m.

![PRISMA preprocess workflow](./figures/prisma_workflow.svg)

## PGE Arguments

In addition to required MAAP job submission arguments the L1 preprocess PGE also takes the following arguments:


|Argument| Type |  Description | Default|
|---|---|---|---|
| raw_dataset| file |URL to input raw dataset granule| -|
| landsat_dataset | config |URL to composite Landsat reference image, required only for PRISMA datasets| 'none'|
| crid| config | Composite release identifier| 000|

## Outputs

The L1B preprocess PGE exports 3 ENVI formatted datacubes along with their associated header files. The outputs of the PGE use the following naming convention:

		SISTER_<SENSOR>_L1B_RDN_<YYYYMMDDTHHMMSS>_CRID.bin
		SISTER_<SENSOR>_L1B_RDN_<YYYYMMDDTHHMMSS>_CRID_LOC.bin
		SISTER_<SENSOR>_L1B_RDN_<YYYYMMDDTHHMMSS>_CRID_OBS.bin

Additionally, a false color quicklook PNG image is produced of the radiance image using wavelengths 560, 850 and 660 nm for DESIS and 560, 850, 1660 nm for all other sensors.

|Product Description |  Units | Example filename
|---|---|---|
| ENVI Radiance datacube |μW/cm<sup>2</sup>/sr|   SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001 |
| ENVI Radiance header file  | - |  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001.hdr|
| ENVI Radiance metadata  | - |  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001.hdr|
| Radiance PNG quicklook  | - |  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001.png |
| ENVI Location datacube |-|  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001_LOC.bin |
| 1. WGS-84 longitude |decimal degrees|
| 2. WGS-84 latitude |decimal degrees|
| 3. Ground elevation |meters|
| ENVI Location header file  | - | SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001_LOC.hdr |
| ENVI Location metadata  | - | SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001_LOC.met.json |
| ENVI Observation datacube |-|  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001_OBS.bin |
| 1. path length |meters|
| 2. to-sensor-azimuth |0 to 360 degrees clockwise N|
| 3. to-sensor-zenith |0 to 90 degrees from zenith|
| 4. to-sun-azimuth |0 to 360 degrees clockwise N|
| 5. to-sun-zenith |0 to 90 degrees from zenith|
| 6. solar phase |degrees|
| 7. slope |decimal degrees|
| 8. aspect |0 to 360 degrees clockwise from N|
| 9. cosine i |unitless|
| 10. UTC time |decimal hours|
| 11. Earth-sun distance |astronomical unit|
| ENVI Observation header file  | - |  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001_OBS.hdr |
| Observation metadata |-|  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001_OBS.met.json |
| PGE runconfig| - |  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001.runconfig.json |
| PGE log| - |  SISTER\_AVNG\_L1B\_RDN\_20220502T180901\_001.log |


File and band descriptions taken directly from [AVIRIS NG Data Product Readme]
(https://avirisng.jpl.nasa.gov/dataportal/ANG_L1B_L2_Data_Product_Readme_v02.txt)


## Algorithm registration

This algorithm can be registered using the algorirthm_config.yml file found in this repository:

	from maap.maap import MAAP
	import IPython
	
	maap = MAAP(maap_host="sister-api.imgspec.org")

	preprocess_alg_yaml = './sister-preprocess/algorithm_config.yaml'
	maap.register_algorithm_from_yaml_file(file_path=preprocess_alg_yaml)

## Examples

### PRISMA
	l1p_job_response = maap.submitJob(algo_id="sister-l1_preprocess",
							    version="2.0.0",
							    raw_dataset= 'PRS_L1_STD_OFFL_20200917091806_20200917091810_0001.zip',
							    landsat_dataset='PRS_20200917091806_20200917091810_0001_landsat.tar.gz',
							    crid='001',
							    publish_to_cmr=False,
							    cmr_metadata={},
							    queue="sister-job_worker-16gb",
							    identifier="SISTER_PRISMA_L1B_RDN_20170827T175432_001")

### AVCL, AVNG, DESIS

Landsat argument not required, will default to 'None'.

 	l1p_job_response = maap.submitJob(algo_id="sister-l1_preprocess",
								    version="2.0.0",
								    raw_dataset= 'ang20170827t175432.tar',
								    crid='001',
								    publish_to_cmr=False,
								    cmr_metadata={},
								    queue="sister-job_worker-16gb",
								    identifier="SISTER_AVNG_L1B_RDN_20170827T175432_001")
