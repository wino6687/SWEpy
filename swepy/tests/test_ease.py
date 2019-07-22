import os
from swepy.ease2Transform import ease2Transform
import glob
import pytest


def test_ease_nogrid():
    with pytest.raises(ValueError):
        ease2Transform.ease2Transform("From Sea to Summit")


def test_ease_incorrect_res():
    with pytest.raises(ValueError):
        ease2Transform.ease2Transform("EASE2_N3.126km")


def test_ease_incorrect_proj():
    with pytest.raises(ValueError):
        ease2Transform.ease2Transform("EASE3_W25km")


def test_grid_to_geo():
    row = 359.5
    col = 359.5
    n25g = ease2Transform.ease2Transform("EASE2_N25km")
    assert n25g.grid_to_geographic(row, col) == pytest.approx((90.0, 0.0), 0.1)


def test_verbose():
    n25g = ease2Transform.ease2Transform("EASE2_N25km", verbose=True)
    assert isinstance(n25g, ease2Transform.ease2Transform)
