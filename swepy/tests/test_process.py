from swepy.swepy import Swepy
from swepy.process import process
import datetime
import os
import pytest
import numpy as np


@pytest.fixture
def scraped_files():
    date = datetime.date(2010, 1, 1)
    s1 = Swepy(
        os.getcwd(),
        start=date,
        end=date,
        ul="N",
        lr="N",
        username="test",
        password="test",
    )
    files = s1.scrape()
    return (files[0][0], files[1][0])


@pytest.fixture
def arrays(scraped_files):
    tb19, tb37 = process.get_array(scraped_files[0], scraped_files[1])
    return (tb19, tb37)


@pytest.fixture
def swe(arrays):
    tb19 = process.vector_clean(arrays[0])
    tb37 = process.vector_clean(arrays[1])
    swe = Swepy.safe_subtract(tb19=tb19, tb37=tb37)
    return swe


def test_get_array(arrays):
    assert type(arrays[0]) == np.ma.core.MaskedArray


def test_vector_clean(arrays):
    cleantb19 = process.vector_clean(arrays[0])
    bool1 = True
    if not np.isnan(cleantb19.all()):
        bool1 = False
    assert bool1 is False


def test_pandas_fill(arrays):
    clean = process.pandas_fill(arrays[0][:, 1, 1])
    bool1 = True
    if not np.isnan(clean).all():
        bool1 = False
    assert bool1 is False


def test_apply_filter_success(arrays):
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
    swe = process.apply_filter(swe)
    assert swe.min() == 0


def test_apply_filter_fail(arrays):
    tb19 = process.vector_clean(arrays[0])
    clean19 = process.apply_filter(tb19)
    assert clean19 == ValueError


def test_apply_filter_large():
    tb19 = np.zeros((100, 5, 5))
    clean19 = process.apply_filter(tb19)
    assert np.shape(clean19) == (100, 5, 5)


def test_apply_filter_mp():
    tb19 = np.zeros((100, 50, 50))
    clean19 = process.apply_filter_mphelper(tb19)
    assert np.shape(clean19) == (100, 50, 50)


def test_apply_filter_mp_fail():
    tb19 = np.zeros((100, 1))
    with pytest.raises(Exception):
        process.apply_filter_mphelper(tb19)


# def test_auto_filter(scraped_files):
#     swe = process.auto_filter(scraped_files[0], scraped_files[1])
#     assert swe.min() == 0
