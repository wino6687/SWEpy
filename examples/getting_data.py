"""
Download SWE Data with SWEpy
========================

Learn how to download temperature brighntess data from MEaSUREs with SWEpy.

This guide coveres only data that pertains to SWE analysis, there will be another guide
regarding scraping any data from MEaSUREs using the included tool.

"""

########################################################################################
# Download SWE Data with SWEpy
# ----------------------------
#
# .. note::
#   The example below will show you how to use the ''swepy.pipeline.scrape_all()``
#   function to donwload data from MEaSUREs directly. This function is
#   designed to only grab files that pertain to estimating SWE (19H and 37H).
#   This workflow has been optimized to find the cleanest and most accurate files
#   of the available options for each day of the time series
#
# The example below will walk you through the needed steps to start using
# SWEpy to scrape, subset, and concatenate TB data for SWE analysis.
#
# By default, SWEpy will store files in a ``data`` directory that is created
# when the class is instantiated.
#
# If you would like to download specific files from the MEaSUREs data set,
# see the examples of using ``nsidcDownloader``.

########################################################################################
# Import Packages
# ---------------
#
# To begin, import needed packages.

import os
import datetime
import swepy.pipeline as pipe

########################################################################################
# Instantiate the SWEpy class
# ---------------------------
#
# The first thing to do with SWEpy is instantiate the class with your desired
# bounding box of coordinates and your working directory.

swe = pipe.Swepy(os.getcwd(), ul=[60, -133], lr=[69, -147])

########################################################################################
# Set other class information
# ---------------------------
#
# Now that the class is instantiated, we are ready to login to EarthData and
# set our desired date range.
#
# These functions aren't a part of class instantiation to simplify the process
# of changing them later.

start = datetime.date(2005, 1, 1)
end = datetime.date(2006, 1, 1)
swe.set_dates(start, end)

swe.set_login("username", "password")

########################################################################################
# Download Data from EarthData with automatic subsetting and concatenation
# ------------------------------------------------------------------------
#
# We are ready to scrape data. These files can be quite large in longer time series.
# To help manage this data quantity there is an automated workflow contained in the function
# ''scrape_all()``. This lets us scrape some data, subset it down, and concatenate them into one
# file to reduce metadata storage. Using this workflow limits disc usage closer to 10GB, depending
# on area of interest size, which is fine for most laptops.

swe.scrape_all()

# Now your ``data`` directory will have two files in it: ``all_days_19H.nc`` and ``all_days_37H.nc``.
# To pre-process these files, see the next example script titled ``processing_data.py``
