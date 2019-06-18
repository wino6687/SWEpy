from swepy.swepy import swepy
from swepy.process import process
from swepy.analysis import analysis
import datetime
import os
import pytest
import numpy as np 
import pandas as pd


@pytest.fixture
def scraped_files():
    date = datetime.date(2010,1,1)
    ul = 'N'
    lr = 'N'
    s1 = swepy(os.getcwd(),start = date, end = date, ul = 'N', lr = 'N', username = 'test', password = 'test')
    files = s1.scrape()
    return (files[0][0], files[1][0])


@pytest.fixture
def arrays(scraped_files):
    tb19, tb37 = process.get_array(scraped_files[0], scraped_files[1])
    return (tb19,tb37)


@pytest.fixture
def swe(arrays):
    tb19 = process.vector_clean(arrays[0])
    tb37 = process.vector_clean(arrays[1])
    swe = swepy.safe_subtract(tb19=tb19,tb37=tb37)
    return swe


@pytest.fixture
def a():
    swe = np.zeros((3000,50,50))
    return analysis.Analysis(datetime.date(1993,1,1), swe)


def test_get_array(arrays):
    assert type(arrays[0]) == np.ma.core.MaskedArray


def test_vector_clean(arrays):
    cleantb19 = process.vector_clean(arrays[0])
    assert np.isnan(cleantb19).all() == False


def test_pandas_fill(arrays):
    clean = process.pandas_fill(arrays[0][:,1,1])
    assert np.isnan(clean).all() == False


def test_apply_filter_success(arrays):
    tb19 = process.vector_clean(arrays[0])
    tb37 = process.vector_clean(arrays[1])
    swe = swepy.safe_subtract(tb19 = tb19,tb37 = tb37)
    swe = np.concatenate((np.concatenate((np.concatenate((swe, swe), axis=0), swe), axis = 0), swe), axis=0)
    swe = swe[:,1:2,1:2]
    swe = process.apply_filter(swe)
    assert swe.min() == 0


def test_apply_filter_fail(arrays):
    tb19 = process.vector_clean(arrays[0])
    clean19 = process.apply_filter(tb19)
    assert clean19 == ValueError


def test_apply_filter_large():
    tb19 = np.zeros((100,5,5))
    clean19 = process.apply_filter(tb19)
    assert np.shape(clean19) == (100,5,5)


def test_apply_filter_mp():
    tb19 = np.zeros((100,50,50))
    clean19 = process.apply_filter_mphelper(tb19)
    assert np.shape(clean19) == (100,50,50)


# def test_auto_filter(scraped_files):
#     swe = process.auto_filter(scraped_files[0], scraped_files[1])
#     assert swe.min() == 0


# START ANALYTICS TEST SUITE
def test_make_df(a):
    # date = datetime.date(2013,1,1)
    # a = analysis.Analysis(date, swe)
    t = a.make_df() # needs to refer back to class
    print(type(t.time[0]))
    assert t.time[0] == pd.Timestamp('1993-01-01 00:00:00')

def test_make_df_type(swe):
    date = datetime.date(2013,1,1)
    a = analysis.Analysis(date, swe)
    t = a.make_df()
    assert type(t) == pd.DataFrame


def test_create_splits():
    array_zeros = np.zeros((3000,30,30),dtype=int)
    date = datetime.date(1993,1,1)
    a = analysis.Analysis(date, array_zeros)
    years = a.create_year_splits()
    assert years == [0, 365, 730, 1095, 1460, 1826, 2191, 2556, 2921, 3287]


def test_count_melt_onset_mp(a):
    """
    Note: right now making zero matrix swe values
    - should maybe make fixture that has an instantiated analysis object with the swe cube inside
    """
    array_zeros = np.zeros((300,50,50), dtype=int)
    #a = analysis.Analysis(1993,1,1, array_zeros)
    c = a.count_melt_onset_mp()
    assert type(c) == pd.DataFrame


# def test_mask_year_df():


    






