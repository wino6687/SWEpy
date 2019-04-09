import os
from swepy.swepy import swepy
from swepy.nsidcDownloader import nsidcDownloader
from swepy.process import process
from swepy.ease2Transform import ease2Transform
import glob
import pytest
import datetime
import numpy as np
import pandas as pd

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
    list1 = glob.glob('*.nc')
    assert 'NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc' in list1


def test_get_auth():
    with pytest.raises(PermissionError):
        nD = nsidcDownloader.nsidcDownloader('room', 'backend')


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
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
            "grid": "K",
            "pass": "M",
            "algorithm": "SIR",
            "input": "CSU",
            "dataversion": "v1.3"
        }
        nD = nsidcDownloader.nsidcDownloader(no_auth = True)
        nD.download_file(**file)