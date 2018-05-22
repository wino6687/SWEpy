# Disclaimer

* Currently this script is not supported in Windows due to pynco only supporting Mac OS or Unix   

* Web scrapping currently only working on the northern hemisphere, fix coming soon

* Requires python 3.6 and Anaconda 3

# Setup:

## Setup Earthdata Login
Create an Earthdata account to be able to download data: https://urs.earthdata.nasa.gov/  

## Optional (.netrc file vs passing Username and Password):
Setup your username and password in a .netrc file  
Run this command in the directory you will be working in

	echo "machine urs.earthdata.nasa.gov login <uid> password <password>" >> ~/.netrc
	chmod 0600 ~/.netrc
uid is your Earthdata username. Do not include the brackets <>.

https://nsidc.org/support/faq/what-options-are-available-bulk-downloading-data-https-earthdata-login-enabled

## 2. Setup conda environment from yaml (Optional):
Using the yaml file (.yml) create a new conda environment
```{python}
conda env create -f swepy_env.yml
```

## 3. Install ipykernel (if using jupyter)

```{python}
source activate swepy_env
python -m ipykernel install --user --name swepy_env --display-name "Python (swepy_env)"
```

# Main Dependencies:
- gdal
- affine
- requests
- scikit-image
- nco (pynco)
- netCDF4
- datetime
- tqdm
- mapboxgl
- pandas


# Using SWEpy for analyzing SWE:

1. Import the Library:
```{python}
from swepy.swepy import swepy
```

2. Instantiate the class with working directory, date range, bounding coordinates, and earthdata username and password

```{python}
upper_left = [lat_upleft, lon_upleft]
lower_right = [lat_lowright, lon_lowright]

start = datetime.date(startY, startM, startD)
end = datetime.date(endY, endM, endD)

path = os.getcwd()

swepy = swepy(path, start, end, upper_left, lower_right, username, password)
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

## Using SWEpy's Web Scraper Alone:

* Note: Web scraper is enabled automatically in the scrape_all workflow, however it can also be used as a stanalone function!

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

* The class formats the following string:

```
 "{protocol}://{server}/{datapool}/{dataset}.{version}/{date:%Y.%m.%d}" \
                    "/{dataset}-{projection}_{grid}{resolution}-{platform}_{sensor}" \
                    "-{date:%Y%j}-{channel}-{pass}-{algorithm}-{input}-{dataversion}.nc"
```

# Function Summaries
Descriptions of included functions
```{python}
get_xy(ll_ul, ll_lr)
```
* Parameters: lists of latitude/longitude upper left, latitude/longitude lower right  
* Uses NSIDC scripts to convert user inputted lat/lon into Ease grid 2.0 coordinates  
* Returns: Ease grid 2.0 coordinates of inputted lat/longs
```{python}
subset(list6, path)
```
* Parameters: coordinates of area of interest, current working directory  
* Subset will get the files from wget directory and subset them geographically  
* Returns: subsetted file
```{python}
concatenate(path, outfile_19, outfile_37, final=False)
```
* Parameters: current working directory, output file for 19Ghz, output file for 37Ghz
* The concatenate function merges all netCDF files into one large file  
* Returns: concatenated netCDF file
```{python}
file_setup(path)
```
* Parameters: current working directory  
* setup files needed for other functions  
* Returns: create correct folders for use by other functions
```{python}
scrape_all(start, end, list3, path=None)
```
* Parameters: start date, end date, list, current working directory(optional)  
* Complete function that downloads, concatenates, and subsets data  
* Returns: file names of concatenated 19/37 time cubes
```{python}
plot_a_day(file1, file2, path, token)
```
* Parameters: 19Ghz files, 37Ghz files, current working directory, mapbox token  
* Plots a day of data using Mapbox Jupyter  
* Returns: interactive map of inputted data


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
If getting HDF5 errors, try deleting all the netCDF files in your directories.
