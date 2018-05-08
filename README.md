# 1. Setup Earthdata Login
Create an Earthdata account to be able to download data - https://urs.earthdata.nasa.gov/

# 2. Build Conda Environment
Using the yaml file (.yml) create a new conda environment

    conda env create -f environment.yml
# 3. Install ipykernel
	source activate myenv
	python -m ipykernel install --user --name myenv
     --display-name "Python (myenv)"
# 4. Run Script
    source activate myenv
    python scriptname.py
  
# Troubleshooting

If encountering ‘image not found’ errors then one possible fix is to add the
conda-forge channel on top of the defaults in your .condarc file. This is a
hidden file, show hidden files and then edit the .condarc file and
make your file look like this:

    $ cat .condarc
    channels:
    - conda-forge
    - defaults

After saving this file, update conda:

    conda update all

https://conda-forge.org/docs/conda-forge_gotchas.html#using-multiple-channels
