import datetime
import time
import os
import warnings
import numpy as np
from numpy import newaxis
from numpy import shape
import pandas as pd
from netCDF4 import Dataset
from skimage.measure import block_reduce
import math
from scipy.signal import savgol_filter
from scipy.cluster.vq import *
from swepy.swepy import Swepy
from multiprocessing import Pool, Process, cpu_count


def get_array(file19, file37, high=True):
    """
    Take 19H and 37H netCDF files, open and store tb
    data in np arrays

    Parameters
    -----------
    file19: str
        filename for 19H file
    file37: str
        filename for 37H file
    high: bool
        true = high resolution imagery (3.125km/6.25km)
        false = low resolution imagery (25km)
    """
    fid_19H = Dataset(file19, "r", format="NETCDF4")
    fid_37H = Dataset(file37, "r", format="NETCDF4")
    tb_19H = fid_19H.variables["TB"][:]
    tb_37H = fid_37H.variables["TB"][:]
    if high:
        tb_37H = block_reduce(tb_37H, block_size=(1, 2, 2), func=np.mean)
    return tb_19H, tb_37H


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
        Note: can be used with other arrays,
        but is looking for patterns in 37H files
    """
    cube[cube == 0] = np.nan
    for i in range(np.shape(cube)[0]):
        arr = cube[i, :, :]
        mask = np.isnan(arr)
        idx = np.where(~mask, np.arange(mask.shape[1]), 0)
        np.maximum.accumulate(idx, axis=1, out=idx)
        cube[i, :, :] = arr[np.arange(idx.shape[0])[:, None], idx]
    return cube


def apply_filter(cube):
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


def apply_filter_mphelper(cube):
    """
    Helper function to apply the filter function in a parralel fashion
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
        parts = p.map(apply_filter, swe_parts)
        try:
            return np.concatenate(parts, axis=2)  # recombine split cube
        except ValueError:
            # FIND WAY TO GET HERE VIA TEST SUITE (1 CORE)
            print(
                "Array provided is smaller than # of cores available. Exiting"
            )


def auto_filter(file19, file37):  # filter_swe is either filter on tb or swe
    """
    Clean missing values and apply sav gol filter, return SWE cube

    Parameters
    -----------
    cube19: np.array
        size = (x,x,x)
    cube37: np.array
        size = (x,x,x)
    """
    cube19, cube37 = get_array(file19, file37)
    clean19 = vector_clean(cube19)
    clean37 = vector_clean(cube37)
    swe = Swepy.safe_subtract(clean19, clean37)
    return apply_filter_mphelper(swe)
