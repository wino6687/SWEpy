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


    
def get_array(file19, file37, high = True):
    """
    --Data Processing--
    Take 19H and 37H netCDF files, open and store tb 
    data in np arrays

    Parameters: 
    -----------
    file19: str
        filename for 19H file 
    file37: str
        filename for 37H file 
    high: bool
        true = high resolution imagery (3.125km/6.25km)
        false = low resolution imagery (25km)
    """
    fid_19H = Dataset(file19,"r", format = "NETCDF4")
    fid_37H = Dataset(file37, "r", format = "NETCDF4")
    tb_19H = fid_19H.variables["TB"][:]
    tb_37H = fid_37H.variables["TB"][:]
    if high:
        tb_37H = block_reduce(tb_37H, block_size = (1,2,2), func = np.mean)
    return tb_19H, tb_37H


def get_count(classes):
    """
    Given class  boundaries, return a dict of counts within 
    each class 

    Parameters: 
    -----------
    classes: list 
        list of class boundaries to compute counts on
    """
    unique, counts = np.unique(classes, return_counts=True)
    return dict(zip(unique, counts))

def pandas_fill(arr):
    """
    --INEFFICIENT--
    --Data Processing--
    Given 2d array, convert to pd dataframe
    and ffill missing values in place

    Parameters: 
    -----------
    arr: np.array 
        Ideally time vector of swe cube
    """
    df = pd.DataFrame(arr)
    df.fillna(method='ffill', inplace = True)
    out = df.values
    return out

def get_df(df,year):
    """
    --Yearly Analysis--
    Given full time series df, subset and return only 
    the data from a given year

    Parameters: 
    df: pd.DataFrame
        full time series to subset 
    year: int
        year to subset dataframe on 
    """
    mask_year = df['time'].dt.year == year
    new_df = df[mask_year]
    counts = new_df['count'].values
    return counts


def vector_clean(cube):
    """
    --Data Processing--
    Clean erroneous spikes out of 37Ghz cube

    Parameters: 
    cube: np.array(t,x,y)
        np array time cube of 37GHz tb data 
        Note: can be used with other arrays, 
        but is looking for patterns in 37H files
    """
    cube[cube == 0] = np.nan
    for i in range(np.shape(cube)[0]):
        arr = cube[i,:,:]
        mask = np.isnan(arr)
        idx = np.where(~mask,np.arange(mask.shape[1]),0)
        np.maximum.accumulate(idx,axis=1, out=idx)
        cube[i,:,:] = arr[np.arange(idx.shape[0])[:,None], idx]
    return cube

def apply_filter(cube): 
    '''
    --Data Processing--
    Apply a sav-gol filter from scipy to time vector's of cube
    Can be used with either tb files or differences SWE values 

    Parameters: 
    ----------
    cube: np.array(t,x,y)
        np array time cube of swe for passive microwave data 
    '''
    shape = np.shape(cube)
    smooth_cube = np.empty((shape[0],shape[1],shape[2]))
    for x in range(shape[1]):
        for y in range(shape[2]):
            pixel_drill = cube[:,x,y]
            pixel = pandas_fill(pixel_drill)
            yhat = savgol_filter(np.squeeze(pixel), 51, 3) 
            yhat[yhat<2] = 0
            smooth_cube[:,x,y] = yhat
    return smooth_cube

# def auto_filter(file19, file37): # filter_swe is either filter on tb or swe
#     """
#     Clean missing values and apply sav gol filter, return SWE cube
    
#     Parameters: 
#     -----------
#     cube19: np.array
#         size = (x,x,x)
#     cube37: np.array
#         size = (x,x,x)
#     """
#     cube19, cube37 = get_array(file19,file37)
#     cube19 = vector_clean(cube19)
#     cube37 = vector_clean(cube37)
#     swe = swepy.safe_subtract(cube19, cube37)
#     return apply_filter(swe)