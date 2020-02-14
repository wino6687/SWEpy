SWEpy: A Python Library for Analyzing SWE via Passive Microwave Imagery
=======================================================================

SWEpy is a Python library designed to simplify access to a passive
microwave brightness temperature dataset available at the National
Snow and Ice Data Center (NSIDC). This dataset contains Northern/Southern 
hemisphere imagery and Equatorial imagery, and can be
quite useful in analyzing snow water equivalent (SWE) over large spatial extents.
SWEpy contains tools to web scrape, geographically subset, and concatenate files
into time cubes. SWEpy also contains tools to aid in the initial processing of
passive microwave data into proxy SWE information. 

SWEpy can be used as a full data pipeline for downloading, subsetting, and concatenating imagery.
However, SWEpy can also be used to accomplish any of these steps individually. See below for 
example usage of SWEpy on several different scenarios. 

SWEpy is comprised of 4 modules: 

``swepy.pipeline`` 
    The primary data pipeline for swepy. It manages the downloading, subsetting, and concatenation of passive microwave data.
``swepy.process``
    The processing module for SWEpy. It allows users to smooth spikes generated from the resampling process in the dataset.
``swepy.analysis``
    The analysis module for SWEpy. It allows users to find quick information about their study area, like understanding how the intial date of total melt changes through the time series
``swepy.nsidcDownloader``
    The web scraping module that powers the ``pipeline`` module. It can be used independently, but is completley interfaced in ``swepy.pipeline`` so there is little need to use it directly.

There are more in depth explanations of each module under their respective documentation page.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   installing_swepy
   getting_started
   pipeline_walkthrough
   processing_data
   advanced_use
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
