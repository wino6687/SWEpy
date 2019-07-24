[![PyPI version](https://badge.fury.io/py/swepy.svg)](https://badge.fury.io/py/swepy)      [![Build Status](https://travis-ci.org/wino6687/SWEpy.svg?branch=master)](https://travis-ci.org/wino6687/SWEpy)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
![OS](https://img.shields.io/badge/OS-Linux64%2C%20MacOS-green.svg)
[![DOI](https://zenodo.org/badge/132654953.svg)](https://zenodo.org/badge/latestdoi/132654953)
![Python Version](https://img.shields.io/pypi/pyversions/Django.svg)[![codecov](https://codecov.io/gh/wino6687/SWEpy/branch/master/graph/badge.svg)](https://codecov.io/gh/wino6687/SWEpy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## Important Notes

* Anaconda 3 recommended

# SWEpy Quick Start Guide
### For Full Documentation, Please see the [Wiki](https://github.com/wino6687/SWEpy/wiki)!

SWEpy is a Python library designed to simplify access to a [passive microwave brightness temperature dataset](https://doi.org/10.5067/MEASURES/CRYOSPHERE/NSIDC-0630.001) available at the National Snow and Ice Data Center (NSIDC). This dataset contains Northern and Southern hemisphere imagery along with Equatorial imagery, and can be quite useful in analyzing snow water equivalent (SWE) over large spatial extents. SWEpy contains tools to web scrape, geographically subset, and concatenate files into time cubes. There is an automated workflow to scrape long time series while periodically stopping to geographically subset and concatenate files in order to reduce disk impact.

## Setup:

### 1. Setup Earthdata Login
Create an Earthdata account to be able to download data: https://urs.earthdata.nasa.gov/


### 2. Setup conda environment from yaml (Recommended)

The libraries used in this analysis, namely pynco, can be finicky with the channels that dependencies are installed with. Thus, using the provided yaml file to build an environment for this project will make your life simpler. You can add more packages on top of the provided environment as long as you install with the conda-forge channel.

Using the yaml file (.yml) create a new conda environment
```{python}
conda env create -f swepy_env.yml
```

### Alternative: Install SWEpy Using Conda or pip:

SWEpy is available from anaconda, and will install all dependencies when installed. It is also available from pip (Pypi), but will not install all the dependencies automatically.

** Important ** ```conda-forge``` must be the first channel in your .condarc file.

```
channels:
  - conda-forge
  - defaults
```

```{python}
conda install swepy
```


### 3. Install ipykernel (if using jupyter and conda environments)

```{python}
source activate swepy_env
python -m ipykernel install --user --name <env name> --display-name "<display name>"
```
**Do not include the brackets <>**

## Using SWEpy for analyzing SWE:

1. Import the Library:
```{python}
from swepy.swepy import swepy
```

2. Instantiate the class with working directory, date range, bounding coordinates, and earthdata username and password

	```{python}
	upper_left = [lon_upleft, lat_upleft]
	lower_right = [lon_lowright, lat_lowright]

	start = datetime.date(startY, startM, startD)
	end = datetime.date(endY, endM, endD)

	path = os.getcwd()

	username = "username"
	password = "password"

	swe = swepy(path, start, end, upper_left, lower_right, username, password, high_res = True)
	```

3. Don't forget to orient your upper-left and lower-right bounding coordinates with the EASE Grid 2.0 Orientation:

 ![Example Study Area](https://nsidc.org/sites/nsidc.org/files/images/data/ease/all_maps.gif)

* By default, the high_res parameter is set to True, meaning it will scrape high resolution images. If it is passed as 'False' then it will scrape 25km images instead of the 6.25km high resolution images.

5. Get Files

	a. Use desired functionality, either separate or individually:

	```{python}
	swe.scrape()
	swe.subset()
	swe.concatenate()

	swe.concatenate(swepy.subset(swepy.scrape()))
	```
 	b. Or, use ```scrape_all``` to avoid massive file sizes:
	```{python}
	swepy.scrape_all()
	```
	This limits the number of full-size images on your disk at one time.


6. If you need to give the class more information, or change information it already has, use the ```set_params``` function:
	```{python}
	swe.set_params(ul = [-145,66], lr = [-166, -16])
	```

## Using SWEpy's Web Scraper Alone:

* The web scraper is enabled automatically in the scrape_all workflow, however it can also be used as a standalone function!

```{python}
from swepy.nsidcDownloader import nsidcDownloader

## Ways to instantiate nsidcDownloader
nD = nsidcDownloader.nsidcDownloader(username="user", password="pass", folder=os.getcwd())


## Download a file:

file = {
    "resolution": "3.125km",
    "platform": "F17",
    "sensor": "SSMIS",
    "date": datetime(2015,10,10),
    "channel": "37H"
}

nD.download_file(**file)
```


# Main Dependencies:
- gdal
- affine
- requests
- scikit-image
- pynco
- netCDF4
- datetime
- tqdm
- pandas


# Troubleshooting:
1. Missing image error when loading in swepy or when calling swepy functions
	- These are channel dependency errors and likely arise due to some of your packages being on conda-forge and others being on other channels. Namely, ```pynco``` struggles with this.
	- Make sure ```conda-forge``` is at the top of your ```.condarc``` file and then run a ```conda update --all```.
	- https://conda-forge.org/docs/conda-forge_gotchas.html#using-multiple-channels

2. Importing SWEpy fails, or pandas fails to find numpy.
	- This seems to be an issue caused by numpy v1.15.0. I reverted back to 1.14.5 and reinstalled everything and it worked again.

If you experience any other issues, do not hesitate to open an issue in this repo!



### Citations:

This library is designed to work with the MEaSUREs CETB dataset:

Brodzik, M. J., D. G. Long, M. A. Hardman, A. Paget, and R. Armstrong. 2016. MEaSUREs Calibrated Enhanced-Resolution Passive Microwave Daily EASE-Grid 2.0 Brightness Temperature ESDR, Version 1. [Indicate subset used]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. doi: https://doi.org/10.5067/MEASURES/CRYOSPHERE/NSIDC-0630.001. [June 2018].


### Acknowledgements:
I want to thank Davey Lovin and David Nyberg for their help in conceiving the original project and developing the original prototype!

I also want to thank Carson Farmer and Earth Lab, CU Boulder for their support throughout the development of this project. 
