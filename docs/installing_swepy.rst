Installing SWEpy
================

Installing SWEpy
----------------

SWEpy is published and maintained on both ``pip`` and ``conda-forge``. It is reccomended that you stick with ``conda-forge`` as dependency issues can be a problem in pip.

You can create a conda environemnt using the provided yml file, ``swepy_env.yml`` to get up and running right away. 

In your terminal, navigate to the directory containing your yml file and run the following command:

``conda env create -f swepy_env.yml``

``conda activate swepy_env``

or 

``source activate swepy_env``

Installing ipykernel for Jupyter
---------------------------------

In order for jupyter to find your kernel, you need to install ipykernel. First activate your new environment, then enter the following: 

``python -m ipykernel install --user --name <env name> --display-name "<display name>"``

Make sure that you do not include the brackets "<>" in your environment name and display name!

Importing SWEpy in Python
-------------------------

Now in Python you will be able to import SWEpy and its submodules. 

    >>> import swepy
    >>> import swepy.pipeline as pipeline
    >>> import swepy.process as process
    >>> import swepy.analysis as analysis
    >>> import swepy.nsidcDownloader as nD
    

Installation Troubleshooting
----------------------------

Many of the issues that can arise when importing SWEpy for the first time are related to dependency conflicts in your conda environment. 
GDAL in particular tends to produce dependency issues. Since open source python libraries are always evolving, it is common for the "links" between the to be broken after updates occur. 

To solve this, activate your conda environment: 

``conda activate swepy_env``

Then update all of the libraries in your environment: 

``conda update --all``

Generally this will solve most dependency issues, but if it does not, try checking if any critical dependencies have been updated recently. 
If something was recently updated, rolling it back to the second latest release may fix issues in your environment. 
