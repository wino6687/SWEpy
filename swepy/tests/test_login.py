import os
from swepy.pipeline import Swepy
from swepy.nsidcDownloader import nsidcDownloader
import glob
import pytest
import datetime
import numpy as np


def test_login():
    s1 = Swepy(os.getcwd())
    s1.set_login("test", "test")
    assert s1.nD is not None
