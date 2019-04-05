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


def test_set_login():
    swep = swepy()
    swep.set_login('test', 'test')
    assert swep.nD.username == 'test' and swep.nD.password == 'test'

