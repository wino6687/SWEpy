# Unit Testing for SWEpy
from swepy.swepy import swepy
import os
import pytest
import datetime
import numpy as np

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
    ll_ul = [62, -140]
    ll_lr = [73, -166]
    s1 = swepy(path, ul = ll_ul, lr = ll_lr)
    list1 = s1.get_xy(ll_ul, ll_lr)
    assert list1 == ([-1988822.7284991546,2370186.631721887,-457544.8408031743,
                    1835112.1237310767],[-1988822.7284991546,2370186.631721887,-457544.8408031743,
                    1835112.1237310767])

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

# scrape

def test_safe_subtract(tmpdir):
    path = tmpdir.mkdir("tmp")
    s1 = swepy(path)
    tb19 = np.ones((1,152,153))
    tb37 = np.ones((1,154,153))
    tb = s1.safe_subtract(tb19,tb37)
    assert np.shape(tb) == (1,151,152)
