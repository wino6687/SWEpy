import datetime
import time
import os
import warnings
import numpy as np
from numpy import newaxis
from numpy import shape
import pandas as pd
import swepy.downsample as down
import math
from scipy.signal import savgol_filter
from scipy.cluster.vq import *
import jenkspy
import numpy.ma as ma
from netCDF4 import Dataset
from multiprocessing import Pool, Process, cpu_count
import netCDF4


def get_array(file, downsample=True):
    """
    Take 19H and 37H netCDF files, open and store tb
    data in np arrays

    Parameters
    -----------
    file: str
        filename for 19H or 37H file
    high: bool
        true = high resolution imagery (3.125km/6.25km)
        false = low resolution imagery (25km)
    """
    fid = Dataset(file, "r", format="NETCDF4")
    tb = fid.variables["TB"][:]
    if downsample and fid.variables["crs"].long_name == "EASE2_N3.125km":
        tb[tb.mask] = 0.00001
        tb = down.downsample(tb, block_size=(1, 2, 2), func=np.mean)
        fid.close()
        return ma.masked_values(tb, 0.00001)
    else:
        fid.close()
        return tb


def pandas_fill(arr):
    """
    Given 2d array, convert to pd dataframe
    and ffill missing values in place

    Parameters
    ----------
    arr: np.array
        Ideally time vector of swe cube
    """
    df = pd.DataFrame(arr)
    df.fillna(method="ffill", inplace=True)
    out = df.values
    return out


def vector_clean(cube):
    """
    Clean erroneous spikes out of 37Ghz cube

    Parameters
    -----------
    cube: np.array(t,x,y)
        np array time cube of 37GHz tb data
    Note: "cube" can be used with other arrays but is looking for patterns in 37H files
    """
    cube[cube == 0] = np.nan
    for i in range(np.shape(cube)[0]):
        arr = cube[i, :, :]
        mask = np.isnan(arr)
        idx = np.where(~mask, np.arange(mask.shape[1]), 0)
        np.maximum.accumulate(idx, axis=1, out=idx)
        cube[i, :, :] = arr[np.arange(idx.shape[0])[:, None], idx]
    return cube


def __filter(cube):
    """
    Apply a sav-gol filter from scipy to time vector's of cube

    Parameters
    -----------
    cube: np.array(t,x,y)
        np array time cube of swe for passive microwave data
    """
    shapecube = np.shape(cube)
    smooth_cube = np.empty((shapecube[0], shapecube[1], shapecube[2]))
    if shapecube[0] == 1:
        print("Cannot smooth a cube with time vector of length 1.")
        return ValueError
    elif (
        shapecube[0] < 51
    ):  # when time vector is len(1) --> concat over itself to make len(3)
        window = shapecube[0] - 1 if shapecube[0] % 2 == 0 else shapecube[0]
        poly = 3 if window > 3 else window - 1
    else:
        window = 51
        poly = 3
    for x in range(shapecube[1]):
        for y in range(shapecube[2]):
            pixel_drill = cube[:, x, y]
            pixel = pandas_fill(pixel_drill)
            yhat = savgol_filter(np.squeeze(pixel), window, poly)
            yhat[yhat < 2] = 0
            smooth_cube[:, x, y] = yhat
    return smooth_cube


def apply_filter(cube):
    """
    Function to apply the filter function in a parralel fashion
    Makes use of a Pool to process on every available core

    Parameters
    -----------
    cube: np.array
        numpy array of data, should be 3d (x,x,x)
    """
    cpus = cpu_count()
    try:
        swe_parts = np.array_split(cube, cpus, axis=2)
    except IndexError:
        print(
            "Array Provided does not have a 2nd axis to split on. Please provide a 3 dimensional cube."
        )
    with Pool(cpus) as p:
        parts = p.map(__filter, swe_parts)
        try:
            return np.concatenate(parts, axis=2)  # recombine split cube
        except ValueError:
            # FIND WAY TO GET HERE VIA TEST SUITE (1 CORE)
            print(
                "Array provided is smaller than # of cores available. Exiting"
            )


def mask_ocean_winter(swe_matrix, day=0, nclasses=3):
    """
    Use a winter day to mask ocean pixels out of coastal imagery in arctic.

    There is a clear difference between winter land pixels and ocean pixels
    that classification can sort out for us using a simple jenks classification.
    Data should have already moved through "vector_clean" and "apply_filter"

    Parameters
    ----------
    swe_matrix: np.array
        swe time cube
    day: int
        julian date of time series to use for classification (should be winter)
    nclasses: int
        number of classes to use in jenks classification, defaults to 3
    """
    winter_day = swe_matrix[day, :, :]
    classes_jenk = jenkspy.jenks_breaks(winter_day.ravel(), nclasses)
    mask = classes_jenk == 1
    winter_day[mask] = -8888
    matrix_mask = np.zeros(swe_matrix.shape, dtype=bool)
    matrix_mask[:, :, :] = winter_day[np.newaxis, :, :] == -8888
    swe_matrix[matrix_mask] = -8888
    return swe_matrix


def safe_subtract(tb19, tb37):
    """
    Check size of each file, often the 19 and 37
    matrices are one unit off of eachother.

    Chops the larger matrix to match the smaller matrix
    """

    shape1 = np.shape(tb19)
    shape2 = np.shape(tb37)
    s1 = [shape1[0], shape1[1], shape1[2]]
    s2 = [shape2[0], shape2[1], shape2[2]]
    if s1[1] < s2[1]:
        s2[1] = s1[1]
    elif s1[1] > s2[1]:
        s1[1] = s2[1]
    if s1[2] < s2[2]:
        s2[2] = s1[2]
    elif s1[2] > s2[2]:
        s1[2] = s2[2]
    tb19 = tb19[:, : s1[1] - 1, : s1[2] - 1]
    tb37 = tb37[:, : s2[1] - 1, : s2[2] - 1]
    tb = tb19 - tb37
    return tb


def save_file(metafile, array, outname):
    """
    Save processed array back out to a new netCDF file

    Metadata is copied from the un-processed file, evertyhing but TB

    Parameters
    ----------
    metafile: str
        old file to copy metadata from
    array: np.array
        processed TB array
    outname: str
        name for output file
    """
    toexclude = ["TB"]
    # Open old file and get info
    with netCDF4.Dataset(metafile) as src, netCDF4.Dataset(
        outname, "w"
    ) as dst:
        # copy global atributes all at once via dict
        dst.setncatts(src.__dict__)
        # copy dimensions
        for name, dimension in src.dimensions.items():
            dst.createDimension(
                name, (len(dimension) if not dimension.isunlimited() else None)
            )
        # copy all file data
        for name, variable in src.variables.items():
            if name not in toexclude:
                dst.createVariable(
                    name, variable.datatype, variable.dimensions
                )
                dst[name][:] = src[name][:]
                # copy variable attributes all at once via dict
                dst[name].setncatts(src[name].__dict__)
        dst.createVariable(
            "TB", src.variables["TB"].datatype, src.variables["TB"].dimensions
        )
        dst["TB"][:] = array[:]
    return outname
