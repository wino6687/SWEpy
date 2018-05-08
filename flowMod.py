import datetime

import subprocess
import shlex
from subprocess import call

import numpy as np
from netCDF4 import Dataset
from skimage.measure import block_reduce

from mapboxgl.utils import *
from mapboxgl.viz import *

import pandas as pd
import ease2conv as e2
from nco import Nco
import os
from tqdm import tqdm
import glob
nco = Nco()


def scrape(dates, path, path_data):
    '''WGET web scraper. supposed to be temporary'''
    os.chdir(path_data)
    # store the path of the url before the data (the date is updated on the fly)
    file_pre = 'https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0630.001/'
    # noinspection PyInterpreter
    sensors = {1992: 'F11', 1993: 'F11', 1994: 'F11', 1995: 'F11', 1996: 'F13', 1997: 'F13', 1998: 'F13',
               1999: 'F13', 2000: 'F13', 2001: 'F13', 2002: 'F13', 2003: 'F15', 2004: 'F15', 2005: 'F15', 2006: 'F15',
               2007: 'F15', 2008: 'F16', 2009: 'F17', 2010: 'F17', 2011: 'F17', 2012: 'F17', 2013: 'F17', 2014: 'F18',
               2015: 'F19'}
    for date in tqdm(dates):
        stri = date.strftime('%Y.%m.%d')
        # convert datetimeindex to date time
        temp = date #
        # Store the year of the current date, convert to day of year
        year = temp.year
        temp = str(temp.timetuple().tm_yday)
        # pad front of day of year with zeroes to always be 3 char long
        temp = temp.rjust(3, '0')
        sensor = sensors[year]
        if sensor in ['F16', 'F17', 'F18', 'F19']:
            post_19 = '/NSIDC-0630-EASE2_N6.25km-' + sensor + '_SSMIS-'
            last_19 = '-19H-M-SIR-CSU-v1.2.nc'
            post_37 = '/NSIDC-0630-EASE2_N3.125km-' + sensor + '_SSMIS-'
            last_37 = '-37H-M-SIR-CSU-v1.2.nc'
        else:
            post_19 = '/NSIDC-0630-EASE2_N6.25km-' + sensor + '_SSMI-'
            last_19 = '-19H-M-SIR-CSU-v1.2.nc'
            post_37 = '/NSIDC-0630-EASE2_N3.125km-' + sensor + '_SSMI-'
            last_37 = '-37H-M-SIR-CSU-v1.2.nc'
        add = str(year)+temp
        # Combine constant file portions with dynamic portions
        new_file_19 = file_pre + stri + post_19 + add +last_19
        new_file_37 = file_pre + stri + post_37 + add + last_37
        # Call wget on this file
        cmd = 'wget -nd --load-cookies '+path+'/cookies.txt --save-cookies '+path+'/cookies.txt --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off -P '+path_data+' '+new_file_19
        cmd2 = 'wget -nd --load-cookies '+path+'/cookies.txt --save-cookies '+path+'/cookies.txt --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off -P '+path_data+' '+new_file_37
        subprocess.call(shlex.split(cmd), shell = False)
        subprocess.call(shlex.split(cmd2), shell = False)


def get_xy(ll_ul, ll_lr):
    '''Use NSIDC scripts to convert user inputted
    lat/lon into Ease grid 2.0 coordinates'''
    N6 = e2.Ease2Transform("EASE2_N6.25km")
    N3 = e2.Ease2Transform("EASE2_N3.125km")
    # get x,y for 6.25
    row, col = N6.geographic_to_grid(ll_ul[0], ll_ul[1])
    x6ul, y6ul = N6.grid_to_map(row,col)
    row, col = N6.geographic_to_grid(ll_lr[0], ll_lr[1])
    x6lr, y6lr = N6.grid_to_map(row, col)
    # get x,y for 3.125
    row, col = N6.geographic_to_grid(ll_ul[0], ll_ul[1])
    x3ul, y3ul = N6.grid_to_map(row, col)
    row, col = N6.geographic_to_grid(ll_lr[0], ll_lr[1])
    x3lr, y3lr = N6.grid_to_map(row, col)
    list_6 = [x6ul, y6ul, x6lr, y6lr]
    list_3 = [x3ul, y3ul, x3lr, y3lr]
    return list_3

## take a path to .nc dataset to subset and the coordinates
def subset(list6, path):
    '''pass geo-coord list and directory path
    script will get the files from wget directory
    and subset them geographically'''
    path19, path37, wget = file_setup(path)
    os.chdir(wget)
    # Make a list of the files to concatenate together for 19H
    list19 = sorted(glob.glob("*19H-M-SIR*"))
    # Make list for the 37GHz
    list37 = sorted(glob.glob("*37H-M-SIR*"))
    for file in tqdm(list19):
        outfile = path19 + file
        infile = wget + file
        opt = [
            "-d x,%f,%f" % (list6[0],list6[2]),
            "-d y,%f,%f" % (list6[3],list6[1]),
            "-v TB"
        ]
        nco.ncks(input=infile, output=outfile, options=opt)
        os.remove(infile)

    for file in tqdm(list37):
        outfile = path37 + file
        infile = wget + file
        opt = [
            "-d x,%f,%f" % (list6[0],list6[2]),
            "-d y,%f,%f" % (list6[3],list6[1]),
            "-v TB"
        ]
        nco.ncks(input=infile, output=outfile, options=opt)
        os.remove(infile)

## use list of paths as parameter to concatenate all paths in list
## ['/folder/file1.nc','/folder/file2.nc']
def concatenate(path, outfile_19, outfile_37, final=False):
    '''Function to concatenate files in the subsetted data
    folders.'''
    os.chdir(path + '/data' + '/Subsetted_19H')
    if final: # final we want to take diff file names
        list19 = glob.glob('19H*nc')
        list19.sort()
    else:
        list19 = glob.glob('NSIDC*nc')
        list19.sort()
    # Concatenate 19GHz files:
    if len(list19) != 0:
        nco.ncrcat(input=list19, output = outfile_19, options=["-O"])
        filelist = glob.glob('NSIDC*')
        for f in filelist:
            os.remove(f)
    else:
        print("No 19Ghz Files to Concatenate")

    # Concatenate 37GHz files:
    os.chdir(path + '/data' + '/Subsetted_37H')
    if final:
        list37 = glob.glob('37H*nc')
        list37.sort()
    else:
        list37 = glob.glob('NSIDC*nc')
        list37.sort()
    if len(list37) != 0:
        nco.ncrcat(input = list37, output = outfile_37, options = ["-O"])
        filelist = glob.glob('NSIDC*')
        for f in filelist:
            os.remove(f)
    else:
        print("No 37Ghz Files to Concatenate")
    return outfile_19, outfile_37


def file_setup(path):
    os.chdir(path)
    wget = path + "/data/wget/"
    path19 = path + "/data/Subsetted_19H/"
    path37 = path + "/data/Subsetted_37H/"

    if not os.path.exists(wget):
        os.makedirs(wget)
    if not os.path.exists(path19):
        os.makedirs(path19)
    if not os.path.exists(path37):
        os.makedirs(path37)
    return path19, path37, wget


def scrape_all(start, end, list3, path=None):
    '''Function to ensure we subset
     and concatenate every year!
     Implements the whole workflow!'''
    if path is None:   # if no directory path provided, find one
        path = os.getcwd()
    os.chdir(path)
    outfile19 = 'all_days_19H.nc'
    outfile37 = 'all_days_37H.nc'
    path19, path37, wget = file_setup(path)
    dates = pd.date_range(start, end)
    if len(dates) <= 133:
        scrape(dates, path, wget)
        subset(list3, path)
        return concatenate(path, outfile19, outfile37)
    else:
        comp_list = [dates[x:x + 100] for x in range(0, len(dates), 100)]
        temp = 1
        for subList in comp_list:
            tempfile19 = '19H' + str(temp) + 'temp.nc'
            tempfile37 = '37H' + str(temp) + 'temp.nc'
            temp += 1
            scrape(subList, path, wget)
            subset(list3, path)
            concatenate(path, tempfile19, tempfile37)
        return concatenate(path, outfile19, outfile37, final=True)



def plot_a_day(file1, file2, path, token):
    '''read tb,x,y data from final files,
    with the purpose of plotting.'''
    os.chdir(path + '/data/Subsetted_19H')
    fid_19H = Dataset(file1, "r", format="NETCDF4")
    os.chdir(path + '/data/Subsetted_37H')
    fid_37H = Dataset(file2, "r", format="NETCDF4")
    x = fid_19H.variables['x'][:]
    y = fid_37H.variables['y'][:]
    tb_19H = fid_19H.variables['TB'][:]
    tb_37H = fid_37H.variables['TB'][:]
    tb_37H = block_reduce(tb_37H, block_size = (1,2,2), func = np.mean)
    tb= tb_19H  - tb_37H
    lats = np.zeros((len(y), len(x)), dtype=np.float64)
    lons = np.zeros((len(y), len(x)), dtype=np.float64)
    grid = e2.Ease2Transform(gridname=fid_19H.variables["crs"].long_name)
    for i, xi in enumerate(x):
        for j, yj in enumerate(y):
            row, col = grid.map_to_grid(xi, yj)
            lat, lon = grid.grid_to_geographic(row, col)
            lats[j, i] = lat
            lons[j, i] = lon
    one_day = tb[0,:,:]
    df = pd.DataFrame(columns = ['lat', 'lon', 'swe'])
    for i in range(len(one_day[:,1])):
        for j in range(1,:):
            df = df.append({'lat': lats[i][j], 'lon': lons[i][j], 'swe':one_day[i][j]}, ignore_index = True)
    df_to_geojson(df, filename = 'swe_1day.geojson',properties = ['swe'],lat = 'lat', lon = 'lon')
    measure = 'swe'
    color_breaks = [round(df[measure].quantile(q=x*0.1), 2) for x in range(1,9)]
    color_stops = create_color_stops(color_breaks, colors='YlGnBu')

    # Create the viz from the dataframe
    viz = CircleViz('swe_1day.geojson',
                    access_token=token,
                    color_property = "swe",
                    color_stops = color_stops,
                    center = (-154, 67),
                    zoom = 3,
                    below_layer = 'waterway-label')

    viz.show()
