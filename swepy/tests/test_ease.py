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

def test_ease_nogrid():
    with pytest.raises(Exception):
        ease = ease2Transform.ease2Transform()

def test_ease_incorrect_res():
    with pytest.raises(Exception):
        ease = ease.ease2Transform("EASE2_N3.126km")

def test_ease_incorrect_proj():
    with pytest.raises(Exception):
        ease = ease.ease2Transform("EASE2_W3.125km")