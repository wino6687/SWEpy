from swepy.pipeline import Swepy
import swepy.process as process
import datetime
import os
import pytest
import numpy as np
from netCDF4 import Dataset


@pytest.fixture
def scraped_files():

    date = datetime.date(2010, 1, 1)
    s1 = Swepy(os.getcwd(), ul="N", lr="N")
    s1.set_dates(date, date)
    s1.set_login("test", "test")
    files = s1.scrape()
    return (files[0][0], files[1][0])


@pytest.fixture
def arrays(scraped_files):
    tb19 = process.get_array(scraped_files[0])
    tb37 = process.get_array(scraped_files[1])
    return (tb19, tb37)


@pytest.fixture
def swe(arrays):
    tb19 = process.vector_clean(arrays[0])
    tb37 = process.vector_clean(arrays[1])
    swe = Swepy.safe_subtract(tb19=tb19, tb37=tb37)
    return swe


def test_get_array(arrays):
    """
    Ensure proper object is created by arrays fixture
    """
    assert type(arrays[0]) == np.ma.core.MaskedArray


def test_vector_clean(arrays):
    """
    Ensure vector clean removes all nan's from arrays
    """
    cleantb19 = process.vector_clean(arrays[0])
    bool1 = True
    if not np.isnan(cleantb19.all()):
        bool1 = False
    assert bool1 is False


def test_pandas_fill(arrays):
    """
    Ensure pands_fill removes missing values from arrays
    """
    clean = process.pandas_fill(arrays[0][:, 1, 1])
    bool1 = True
    if not np.isnan(clean).all():
        bool1 = False
    assert bool1 is False


def test_apply_filter_success(arrays):
    """
    Ensure arrays processed with apply_filter have a min of 0
    """
    tb19 = process.vector_clean(arrays[0])
    tb37 = process.vector_clean(arrays[1])
    swe = Swepy.safe_subtract(tb19=tb19, tb37=tb37)
    swe = np.concatenate(
        (
            np.concatenate((np.concatenate((swe, swe), axis=0), swe), axis=0),
            swe,
        ),
        axis=0,
    )
    swe = swe[:, 1:2, 1:2]
    swe = process.__filter(swe)
    assert swe.min() == 0


def test_apply_filter_fail(arrays):
    """
    Ensure an uncleaned array returns ValueError when processed
    with apply_filter
    """
    tb19 = process.vector_clean(arrays[0])
    clean19 = process.__filter(tb19)
    assert clean19 == ValueError


def test_apply_filter_large():
    """
    Ensure apply_filter properly preserves array size when len > 51
    """
    tb19 = np.zeros((100, 5, 5))
    clean19 = process.__filter(tb19)
    assert np.shape(clean19) == (100, 5, 5)


def test_apply_filter_mp():
    """
    ensure array is preserved when fed into multiprocessing apply_filter
    """
    tb19 = np.zeros((100, 50, 50))
    clean19 = process.apply_filter(tb19)
    assert np.shape(clean19) == (100, 50, 50)


def test_apply_filter_mp_fail():
    """
    Ensure array with len(shape) < 3 raises Exception in mp filter
    """
    tb19 = np.zeros((100, 1))
    with pytest.raises(Exception):
        process.apply_filter(tb19)


def test_ocean_mask():
    """
    Ensure proper type is returned by ocean mask
    """
    array = np.ones((1, 142, 130))
    arr = process.mask_ocean_winter(array)
    assert type(arr) is np.ndarray


def test_safe_subtract1():
    """
    Test axis s1[1] < s2[1] & s1[2] == s2[2]
    """
    tb19 = np.ones((1, 152, 153))
    tb37 = np.ones((1, 154, 153))
    tb = process.safe_subtract(tb19, tb37)
    assert np.shape(tb) == (1, 151, 152)


def test_safe_subtract2():
    """
    Test s1[1] > s2[1] & s1[2] < s1[2]
    """
    tb19 = np.ones((1, 154, 152))
    tb37 = np.ones((1, 152, 153))
    tb = process.safe_subtract(tb19, tb37)
    assert np.shape(tb) == (1, 151, 151)


def test_save(arrays, scraped_files):
    """
    Test saving files results in proper structure
    """
    out = process.save_file(scraped_files[0], arrays[0], "process19.nc")
    fid = Dataset(out)
    assert fid.variables["TB"][:].all() == arrays[0].all()
