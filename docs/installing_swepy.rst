Getting started with SWEpy
==========================

SWEpy is comprised of 4 modules: 

``swepy.pipeline`` 
    The primary data processing module for swepy. It manages the downloading, subsetting, and concatenation of passive microwave data.
``swepy.process``
    The processing module for SWEpy. It allows users to smooth spikes generated from the resampling process in the dataset.
``swepy.analysis``
    The analysis module for SWEpy. It allows users to find quick information about their study area, like understanding how the intial date of total melt changes through the time series
``swepy.nsidcDownloader``
    The web scraping module that powers the ``pipeline`` module. It can be used independently, but is completley interfaced in ``swepy.pipeline`` so there is little need to use it directly.

There are more in depth explanations of each module under their respective documentation page.

Installing SWEpy
----------------

SWEpy is published and maintained on both ``pip`` and ``conda-forge``. It is reccomended that you stick with ``conda-forge`` as dependency issues can be a problem in pip.

You can create a conda environemnt using the provided yml file, ``swepy_env.yml`` to get up and running right away. 

In your terminal, navigate to the directory containing your yml file and run the following command:

``conda env create -f swepy_env.yml``

``source activate swepy_env``

or 

``conda activate swepy_env``

Importing SWEpy in Python
-------------------------

Now in Python you will be able to import SWEpy and its submodules. 

    >>> import swepy
    >>> import swepy.pipeline as pipe
    >>> import swepy.process as sp
    >>> import swepy.analysis as sa
    >>> import swepy.nsidcDownloader as sd

