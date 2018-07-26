# Unit Testing for SWEpy
from swepy.swepy import swepy
import pytest

def test_get_grid_N():
    lat1 = 45
    lat2 = 80
    assert swepy.get_grid(lat1, lat2) == "N"

def test_get_grid_T():
    lat1 = 30
    lat2 = 30
    assert swepy.get_grid(lat1,lat2) == "T"

def test_get_grid_S():
    lat1 = -50
    lat2 = -80
    assert swepy.get_grid(lat1, lat2) == "S"

#def test_get_directories(tmpdir):
    #path = tmpdir.mkdir("data")
    #print(path)
