# Unit Testing for SWEpy
import os
#print(os.environ['CONDA_DEFAULT_ENV'])
from swepy.swepy import swepy
from swepy.nsidcDownloader import nsidcDownloader
import glob
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

def test_check_params():
    start = datetime.date(2010,1,1)
    ul = [-145,66]
    lr = [-166,73]
    s1 = swepy(os.getcwd(), start, start, ul, lr)
    assert s1.check_params() == False

def test_get_grid_N():
    s1 = swepy(os.getcwd())
    lat1 = 45
    lat2 = 80
    assert s1.get_grid(lat1, lat2) == "N"

def test_get_grid_T():
    s1 = swepy(os.getcwd())
    lat1 = 30
    lat2 = 30
    assert s1.get_grid(lat1,lat2) == "T"

def test_get_grid_S():
    s1 = swepy(os.getcwd())
    lat1 = -50
    lat2 = -80
    assert s1.get_grid(lat1, lat2) == "S"

def test_get_directories(tmpdir):
    path = tmpdir.mkdir('tmp')
    s1 = swepy(path)
    list = os.listdir(".")
    assert list == ['data']

def test_get_xy_N():
    ll_ul = [ -140, 62]
    ll_lr = [-166, 73]
    s1 = swepy(os.getcwd(), ul = ll_ul, lr = ll_lr)
    list1 = s1.get_xy(ll_ul, ll_lr)
    assert list1 == [-1988822.728499157, 2370186.6317218887, -457544.84080317785, 1835112.123731079]

def test_get_xy_S():
    ll_lr = [9,-80]
    ll_ul = [-16, -69]
    s1 = swepy(os.getcwd(), ul = ll_ul, lr = ll_lr)
    list1 = s1.get_xy(ll_ul, ll_lr)
    assert list1 == [-642633.6942027326, 2241130.027261452,174488.418187805, 1101676.514626506]

def test_get_file():
    #path = tmpdir.mkdir("tmp")
    s1 = swepy(os.getcwd(), ul = 'N', lr = 'N', username = 'test', password = 'test')
    date = datetime.datetime(2010,1,1)
    file = s1.get_file(date, "19H")
    assert file == {'protocol':'https', 'server':'localhost:8000','resolution': '6.25km','platform': 'F17','sensor': 'SSMIS',
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

def test_connection():
    date = datetime.date(2010,1,1)
    file = {
        "protocol": "http",
        "server": "localhost:8000",
        "datapool": "MEASURES",
        "dataset": "NSIDC-0630",
        "version": "001",
        "projection": "EASE2",
        "resolution": "6.25km",
        "platform":"F17",
        "sensor": "SSMIS",
        'date1': datetime.date(2010, 1, 1),
        'date2': datetime.date(2010, 1, 1),
        "channel": '19H',
        "grid": "N",
        "pass": "M",
        "algorithm": "SIR",
        "input": "CSU",
        "dataversion": "v1.3"
    }
    nD = nsidcDownloader.nsidcDownloader(no_auth = True)
    resp = nD.download_file(**file)
    assert resp == True

def test_nD_local():
    date = datetime.date(2010,1,1)
    file = {
        "protocol": "http",
        "server": "localhost:8000",
        "datapool": "MEASURES",
        "dataset": "NSIDC-0630",
        "version": "001",
        "projection": "EASE2",
        "resolution": "6.25km",
        "platform":"F17",
        "sensor": "SSMIS",
        'date1': datetime.date(2010, 1, 1),
        'date2': datetime.date(2010, 1, 1),
        "channel": '19H',
        "grid": "N",
        "pass": "M",
        "algorithm": "SIR",
        "input": "CSU",
        "dataversion": "v1.3"
    }
    nD = nsidcDownloader.nsidcDownloader(no_auth = True)
    nD.download_file(**file)
    #os.chdir('tmp')
    list1 = glob.glob('*.nc')
    assert list1[0] == 'NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc'

def test_scrape():
    date = datetime.date(2010,1,1)
    ul = 'N'
    lr = 'N'
    s1 = swepy(os.getcwd(),start = date, end = date, ul = 'N', lr = 'N', username = 'test', password = 'test')
    s1.scrape()
    list1 = glob.glob("*.nc")
    assert list1 == ['NSIDC-0630-EASE2_N3.125km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc','NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc']
