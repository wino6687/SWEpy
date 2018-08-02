# Unit Testing for SWEpy
import os
#print(os.environ['CONDA_DEFAULT_ENV'])
from swepy.swepy import swepy
from swepy.nsidcDownloader import nsidcDownloader
import pytest
#import nose
import datetime
import numpy as np
import pandas as pd


'''
def test_set_params(tmpdir):
    path = tmpdir.mkdir("tmp")
    start = datetime.date(2010,1,1)
    dates = pd.date_range(start,start)

'''

def test_check_params(tmpdir):
    path = tmpdir.mkdir("tmp")
    start = datetime.date(2010,1,1)
    ul = [-145,66]
    lr = [-166,73]
    s1 = swepy(path, start, start, ul, lr)
    assert s1.check_params() == False

def test_get_grid_N(tmpdir):
    path = tmpdir.mkdir("tmp")
    s1 = swepy(path)
    lat1 = 45
    lat2 = 80
    assert s1.get_grid(lat1, lat2) == "N"

def test_get_grid_T(tmpdir):
    path = tmpdir.mkdir("tmp")
    s1 = swepy(path)
    lat1 = 30
    lat2 = 30
    assert s1.get_grid(lat1,lat2) == "T"

def test_get_grid_S(tmpdir):
    path = tmpdir.mkdir("tmp")
    s1 = swepy(path)
    lat1 = -50
    lat2 = -80
    assert s1.get_grid(lat1, lat2) == "S"

def test_get_directories(tmpdir):
    path = tmpdir.mkdir("tmp")
    s1 = swepy(path)
    list = os.listdir(".")
    assert list == ['data']

def test_get_xy(tmpdir):
    path = tmpdir.mkdir("tmp")
    ll_ul = [ -140, 62]
    ll_lr = [-166, 73]
    s1 = swepy(path, ul = ll_ul, lr = ll_lr)
    list1 = s1.get_xy(ll_ul, ll_lr)
    assert list1 == [-1988822.728499157, 2370186.6317218887, -457544.84080317785, 1835112.123731079]

# need one for subset

def test_get_file(tmpdir):
    path = tmpdir.mkdir("tmp")
    s1 = swepy(path, ul = 'N', lr = 'N')
    date = datetime.datetime(2010,1,1)
    file = s1.get_file(date, "19H")
    assert file == {'resolution': '6.25km','platform': 'F17','sensor': 'SSMIS',
                    'date1': datetime.datetime(2010, 1, 1, 0, 0),
                    'date2': datetime.datetime(2010, 1, 1, 0, 0),
                    'channel': '19H','grid': 'N','dataversion': 'v1.3',
                    'pass': 'M','algorithm': 'SIR'}

# scrape_all

# concatenate

# final concat

def test_safe_subtract(tmpdir):
    path = tmpdir.mkdir("tmp")
    s1 = swepy(path)
    tb19 = np.ones((1,152,153))
    tb37 = np.ones((1,154,153))
    tb = s1.safe_subtract(tb19,tb37)
    assert np.shape(tb) == (1,151,152)


def test_scrape_local(tmpdir):
    date = datetime.date(2010,1,1)
    dates = pd.date_range(date, date)
    path = tmpdir.mkdir("tmp")
    file = {
        "protocol": "https",
        "server": "localhost:8000",
        "datapool": "MEASURES",
        "dataset": "NSIDC-0630",
        "version": "001",
        "projection": "EASE2",
        "resolution": "6.25km",
        "platform":"F17",
        "sensor": "SSMIS",
        'date1': datetime.date(2010, 1, 1, 0, 0),
        'date2': datetime.date(2010, 1, 1, 0, 0),
        "channel": '19H'
        "grid": "N",
        "pass": "M",
        "algorithm": "SIR",
        "input": "CSU",
        "dataversion": "v1.3"
    }
    nD = nsidcDownloader.nsidcDownloader(folder = "tmp", no_auth = True, **file)
    nD.download_file(**file)
    list1 = os.listdir('.')
    assert list1 == 'MEASURES/NSIDC-0630.001/2010.01.01/NSIDC-0630-\
                    EASE2_N6.25km-F15_SSMI-2010001-19H-M-SIR-CSU-v1.3.nc'


# clean clean_dirs
