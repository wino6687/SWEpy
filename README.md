# Disclaimer
Currently this script is not supported in Windows due to pynco only supporting Mac OS or Unix  
Requires python 3.6 and Anaconda 3

# 1. Setup Earthdata Login
Create an Earthdata account to be able to download data: https://urs.earthdata.nasa.gov/  
Setup your username and password in a .netrc file  
Run this command in the directory you will be working in

	echo "machine urs.earthdata.nasa.gov login <uid> password <password>" >> ~/.netrc
	chmod 0600 ~/.netrc
<uid> is your Earthdata username. Do not include the brackets <>.

https://nsidc.org/support/faq/what-options-are-available-bulk-downloading-data-https-earthdata-login-enabled

# 2. Build Conda Environment
Using the yaml file (.yml) create a new conda environment

    conda env create -f environment.yml
# 3. Install ipykernel
	source activate myenv
	python -m ipykernel install --user --name myenv --display-name "Python (myenv)"
# 4. Run Script
    source activate myenv
    python scriptname.py
  
# Troubleshooting

If encountering ‘image not found’ errors then one possible fix is to add theconda-forge channel on top of the defaults in your .condarc file. This is a hidden file, show hidden files and then edit the .condarc file and make your file look like this:

    $ cat .condarc
    channels:
    - conda-forge
    - defaults

After saving this file, update conda:

    conda update all

https://conda-forge.org/docs/conda-forge_gotchas.html#using-multiple-channels


# Function Summaries
Descriptions of included functions
## scrape(dates, path, path_data)
Parameters: date range,  
## get_xy(ll_ul, ll_lr)
Parameters: lists of latitude/longitude upper left, latitude/longitude lower right
Uses NSIDC scripts to convert user inputted lat/lon into Ease grid 2.0 coordinates
## subset(list6, path)
Parameters:
subset
## concatenate(path, outfile_19, outfile_37, final=False)
Parameters: path, output file, output file, final(optional)
The concatenate function 
## file_setup(path)
Parameters: 
setup files
## scrape_all(start, end, list3, path=None)
Parameters: start date, end date, list, path(optional)
Comp function
## plot_a_day(file1, file2, path, token)
Parameters: 
Plots a day in Mapbox
