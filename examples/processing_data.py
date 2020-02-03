"""
Process SWE Data with SWEpy
===========================

Learn how to clean and process SWE data easily with SWEpy's built in tools.

This guide covers using the ``swepy.process`` module to open arrays, easily fill in missing data,
and smooth erroneous spikes. These functions are quite useful for eliminating swaths of missing
information by smoothing temporally.
"""

########################################################################################
# Smooth arrays that were recently downloaded
# -------------------------------------------
#
# .. note::
#   The exmaple below will show you how to use the ``swepy.process`` module for cleaning
#   messy arrays that come straight from the MEaSUREs database. Many arrays are missing some
#   information, which can make meaningful analysis difficult. Since many of the arrays
#   contain good information, it is reasonable to fill and smooth temporally to give us
#   better spatial slices of data. There will be some examples shown in a markdown folder
#   titled ``processing_data_examples.md`` in this same directory.
#
########################################################################################
# Import packages
# ---------------
#
# To begin, import needed packages.

import swepy.process as proc

########################################################################################
# Open arrays into memory using swepy's built in functionality
#
# The 37H band is a higher resolution (3.125km) compared to the 19H band (6.25km)
# SWEpy automatically downsamples the 37H band to match the size of the 19H band.

tb19 = proc.get_array("data/all_days_19H.nc")
tb37 = proc.get_array("data/all_days_37H.nc")

########################################################################################
# Forward fill missing data in the array
#
# In order to filter the data, we must clean out all of the missing points. SWEpy has
# a vectorized function for forward filling missing points temporally called ``vector_clean``
# Forward filling is done temporally since the same pixel is more similar to itself in the
# day prior than it is to the pixel next door.

tb19 = proc.vector_clean(tb19)
tb37 = proc.vector_clean(tb37)

########################################################################################
# Apply a Savitsky_Golay filter
#
# A sav-gol filter is designed to increase data precision without distorting the signal
# tendency of the data. It fits successive sub-sets of adjacent data points with a low
# degree polynomial with the method of linear least squares. This is an effective
# smoothing method here since our data is evenly spaced temporally.
#
# A new sav-gol filter is applied to every temporal array in the cube. The results generally
# make for significantlly cleaner imagery throughout the time series.
#
# Since ``apply_filter`` fits a sav-gol filter to every temporal vector, it can be quite
# slow. Due to this, there is a multiprocessing helper function available, ``apply_filter_mphelper``

tb19 = proc.apply_filter_mphelper(tb19)
tb37 = proc.apply_filter_mphelper(tb37)

########################################################################################
# Subtract the two arrays to get SWE
#
# By subtracting the tb37 vector from the tb19 vector, we obtain a proxy for snow
# water equivalent.
#
# There is a built in method called ``safe_subtract()`` to handle this operation.
# Since we must downscale the 37H band, the two cubes don't always align properly, and
# this function will chop off one or two rows to match the two arrays properly.

swe = proc.safe_subtract(tb19, tb37)

########################################################################################
# Reconstruct new NETCDF4 file from SWE array
#
# This step isn't mandatory, but to prevent repeating all of this compuation, we can
# save the array back to a NETCDF file. For this we copy the needed metadata from the 19H
# file since it has the same geographic coordinates as our new swe file.
