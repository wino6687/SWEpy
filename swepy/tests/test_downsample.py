import pytest
import swepy.downsample as downsample
import os
import numpy as np


@pytest.fixture
def swe():
    print(os.listdir())
    swe = np.load("swepy/tests/swe_testfile.npy")
    return swe
