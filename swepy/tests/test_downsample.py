import pytest
import swepy.downsample as downsample
import os
import numpy as np


@pytest.fixture
def swe():
    print(os.listdir())
    swe = np.load("swepy/tests/swe_testfile.npy")
    return swe


def test_tuple_block_fail(swe):
    with pytest.raises(TypeError):
        downsample.downsample(swe, ([1, 2, 2]), np.mean)
