# Disclaimer

* All study area boxes should be oriented to the North when choosing lower right and upper left bounding coordinates.

* Currently this script is not supported in Windows due to pynco only supporting Mac OS or Unix

* Requires python 3.6 and Anaconda 3

# Setup:

## 1. Setup Earthdata Login
Create an Earthdata account to be able to download data: https://urs.earthdata.nasa.gov/

## Optional (.netrc file vs passing Username and Password):
Setup your username and password in a .netrc file
Run this command in the directory you will be working in

	echo "machine urs.earthdata.nasa.gov login <uid> password <password>" >> ~/.netrc
	chmod 0600 ~/.netrc
uid is your Earthdata username. Do not include the brackets <>.

https://nsidc.org/support/faq/what-options-are-available-bulk-downloading-data-https-earthdata-login-enabled

## 2. Install SWEpy Using Conda (Recommended):
SWEpy is available from anaconda, and will install all dependencies when installed.

```{python}
conda install -c wino6687 swepy
```

### Alternative: Setup conda environment from yaml
The libraries used in this analysis, namely pynco, can be finicky with the channels that dependencies are installed with. Thus, using the provided yaml file to build an environment for this project will make your life simpler. You can add more packages on top of the provided environment as long as you install with the conda-forge channel.

Using the yaml file (.yml) create a new conda environment
```{python}
conda env create -f swepy_env.yml
```

## 3. Install ipykernel (if using jupyter and conda environments)

```{python}
source activate swepy_env
python -m ipykernel install --user --name <env name> --display-name "<display name>"
```
**Do not include the brackets <>**

# Using SWEpy for analyzing SWE:

1. Import the Library:
```{python}
from swepy.swepy import swepy
```

2. Instantiate the class with working directory, date range, bounding coordinates, and earthdata username and password

* Reminder: Don't forget to orient your upper-left and lower-right bounding coordinates to the North.

* By default, the high_res parameter is set to True, meaning it will scrape high resolution images. If it is passed as 'False' then it will scrape 25km images instead of the 6.25km high resolution images.

```{python}
upper_left = [lat_upleft, lon_upleft]
lower_right = [lat_lowright, lon_lowright]

start = datetime.date(startY, startM, startD)
end = datetime.date(endY, endM, endD)

path = os.getcwd()

username = <username>
password = <password>

swepy = swepy(path, start, end, upper_left, lower_right, username, password, high_res = True)
```
3. Use desired functionality, either separate or individually:

```{python}
swepy.scrape()
swepy.subset()
swepy.concatenate()

swepy.concatenate(swepy.subset(swepy.scrape()))
```

4. Or, use scrape_all to avoid massive file sizes:
```{python}
swepy.scrape_all()
```
This limits the number of full-size images on your disk at one time.

## If you would like a full grid file, with no subsetting, simply pass the grid id as your upper left and lower right bounding coordinates.

* North = "N"
* South = "S"
* Equator = "T"

```{python}
upper_left = "N"
lower_right = "N"
```

## Using SWEpy's Web Scraper Alone:

* Note: Web scraper is enabled automatically in the scrape_all workflow, however it can also be used as a standalone function!

```{python}
from swepy.nsidcDownloader import nsidcDownloader

## Ways to instantiate nsidcDownloader
nD = nsidcDownloader.nsidcDownloader(username="user", password="pass", folder=".") ## user/pass combo and folder

nD = nsidcDownloader(sensor="SSMIS") ## user/pass combo from .netrc and default folder, setting the default key of sensor

## Download a file:

file = {
    "resolution": "3.125km",
    "platform": "F17",
    "sensor": "SSMIS",
    "date": datetime(2015,10,10),
    "channel": "37H"
}

nD.download_file(**file)

nD.download_range(sensor="SSMIS", date=[datetime(2014,01,01), datetime(2015,01,01)])
```

* Authentication will work if the user/pass combo is saved in `~/.netrc`, or if it is passed in the nsidcDownloader instance


# Function Summaries
Descriptions of included functions
```{python}
swepy = swepy(working_dir, start, end, ll_ul, ll_lr, username, password)
```
* Instantiate the class with the working directory path, the start date, the end date, the bounding coordinates, and your Earthdata username and password.
* Once the class is instantiated, either call scrape_all or call scrape, then subset, then concatenate as desired.
```{python}
swepy.get_xy(latlon_ul, latlon_lr)
```
* Parameters: lists of latitude/longitude upper left, latitude/longitude lower right
* Uses NSIDC scripts to convert user inputted lat/lon into Ease grid 2.0 coordinates
* Returns: Ease grid 2.0 coordinates of inputted lat/longs
```{python}
swepy.subset()
```
* Parameters: none, list of downloaded files stored in class from scrape() function
* Subset will subset the files downloaded geographically to match study area inputed
* Returns: subsetted file
```{python}
swepy.concatenate()
```
* Parameters: current working directory, output file for 19Ghz, output file for 37Ghz
* The concatenate function merges all netCDF files into one large file
* Returns: concatenated netCDF file
```{python}
swepy.scrape_all()
```
* Parameters: none, everything needed comes from class instantiation
* Complete function that downloads, subsets, and concatenates the data
* Returns: file names of concatenated 19/37 time cubes
```{python}
swepy.plot_a_day(token)
```
* Parameters: mapbox token, everything else comes from the stored concatenated file list
* Plots a day of data using Mapbox Jupyter
* Returns: interactive map of inputted data
```{python}
swepy.get_file(path, date, channel)
```
* Parameters: date of file path to get, and the channel (19GHz vs 37GHz)
* get file path of file to download for specific day of SWE
* Returns: framework for file to be downloaded based on date and channel for analyzing SWE

# Main Dependencies:
- gdal
- affine
- requests
- scikit-image
- pynco
- netCDF4
- datetime
- tqdm
- mapboxgl
- pandas

# Troubleshooting

1. ‘image not found’ errors
If encountering ‘image not found’ errors then one possible fix is to add theconda-forge channel on top of the defaults in your .condarc file. This is a hidden file, show hidden files and then edit the .condarc file and make your file look like this:

    $ cat .condarc
    channels:
    - conda-forge
    - defaults

After saving this file, update conda:

    conda update all

https://conda-forge.org/docs/conda-forge_gotchas.html#using-multiple-channels

2. HDF5 errors:
If getting HDF5 errors, try deleting all the netCDF files in your directories and starting over. This usually occurs when there are already some files in the data directories before calling scrape_all and ncks gets confused on the subset step.

# Known Bugs:
1. Missing data can cause plotting to error out.
	- missing data is common in the mid-latitudes, so if your midlat study area errors out when plotting, this is likely the issue

2. There are some weird dates in the file paths of 25km data from 2003-2017 causing web scraper to error out.
	- According to the NSIDC, this is because N and S grid images contain data from more than one single day, and thus the dating of certain data is slightly off. I am going to dig into the pattern more to find a fix on SWEpy's end.
	- There are still some issue days. April 9th, 2004 is missing all N25km-F15 files, while the day prior and next day have these files. This will cause the automated scraping to stall and not finish.

3. 25km data will not plot properly in mapbox.
	- For some reason, there is an issue converting dataframes to geojson only when scraping the 25km data. I am looking into why this is, but for now visualization only works on high resolution data.

4. Conda-forge dependency issues:
	- My goal is to get the installation of SWEpy onto the conda-forge channel, but currently I cannot do that while I need to use different channels to install cetbtools and mapboxgl.


Citations:

This library is designed to work with the MEaSUREs CETB dataset:

Brodzik, M. J., D. G. Long, M. A. Hardman, A. Paget, and R. Armstrong. 2016. MEaSUREs Calibrated Enhanced-Resolution Passive Microwave Daily EASE-Grid 2.0 Brightness Temperature ESDR, Version 1. [Indicate subset used]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. doi: https://doi.org/10.5067/MEASURES/CRYOSPHERE/NSIDC-0630.001. [June 2018].
