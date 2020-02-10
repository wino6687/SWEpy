"""
Alternate Ways to Use SWEpy's Pipeline
======================================

While the ``scrape_all()`` function is the bread and butter of SWEpy's pipeline, it
is not always practical to use the entire process at one time.

This guide covers how one would go about doing things like subsetting data that already
has been scraped or concatenating a set of files that were previously scraped.
"""

########################################################################################
# Scrape some files using SWEpy
# -----------------------------
# We don't always want to end up with one file that contains all of our data. Or we may
# not want to store subsetted data, since changing our subset would then require us to re-
# download the data. Let's look at how to use SWEpy without running the entire workflow at
# once.

########################################################################################
# Import Packages
# ---------------
#
# To begin, import needed packages

import os
import datetime
import swepy.pipeline as pipe

########################################################################################
# Instantiate the SWEpy Class and Set Info
# ----------------------------------------
#
# We are going to scrape the entire North grid to start

start = datetime.date(2005, 1, 1)
end = datetime.date(2005, 5, 1)

swe = pipe.Swepy(os.getcwd(), ul="N", lr="N")
swe.set_login("username", "password")
swe.set_dates(start, end)

########################################################################################
# Scrape files for North hemisphere
# ---------------------------------
#
# Using the ``scrape`` function, we can easily download files in our date range

swe.scrape()

########################################################################################
# Either Subset or Concatenate Scraped Files
# ------------------------------------------
#
# Now we have full North grid imagery stored in many files. We can either subset them down,
# or if we want to keep the full images, we can go ahead and just concatenate them together.

swe.concatenate()

# OR

swe.set_grid(ul=[60, -133], lr=[69, -147])
outfiles = swe.concatenate(swe.subset())

# NOTE: We have to set a new grid in order for ``subset``to work.

########################################################################################
# Convert output files to zarr
#
# Some users may want to convert their output files to zarr for storage in cloud. Zarr
# works better with AWS S3's object oriented storage structure. With a zarr file you
# can access portions of the file and read only parts of a file into memory from S3.

swe.convert_netcdf_zarr()
