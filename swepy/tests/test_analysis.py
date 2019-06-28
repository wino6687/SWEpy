from swepy.swepy import swepy
from swepy.process import process
from swepy.analysis import analysis
import datetime
import os
import pytest
import numpy as np 
import pandas as pd

@pytest.fixture
def a():
    swe = np.zeros((3000,50,50))
    return analysis.Analysis(datetime.date(1993,1,1), swe)

# START ANALYTICS TEST SUITE
def test_make_df_time():
    """
    Make sure timestamp is correctly created in dataframe
    """
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    t = a.make_df() 
    print(type(t.time[0]))
    assert t.time[0] == pd.Timestamp('1993-01-01 00:00:00')

def test_make_df_type():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    t = a.make_df()
    assert type(t) == pd.DataFrame


def test_create_splits():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    years = a.create_year_splits()
    assert years == [0, 365, 730, 1095, 1460, 1826, 2191, 2556, 2921, 3287]


def test_count_melt_onset_mp():
    """
    Note: right now making zero matrix swe values
    - should maybe make fixture that has an instantiated analysis object with the swe cube inside
    """
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    c = a.count_melt_onset_mp()
    assert type(c) == pd.DataFrame


def test_mask_year_df():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    df = a.make_df()
    df = a.mask_year_df(df, 1994)
    assert df.iloc[0].time.year == 1994


def test_melt_date_year():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    df = a.make_df()
    counts = a.melt_date_year(df)
    assert type(counts) == dict


def test_count_index():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    c = a.count_melt_onset_index(swe)
    assert type(c) == pd.DataFrame


def test_summer_length():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    c = a.summer_length(swe)
    assert type(c) == dict


def test_summer_length2():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    c = a.summer_length(swe)
    assert type(c[(1,1)]) == dict


def test_summer_diff1():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    c = a.summer_length(swe)
    diff, heatmap = a.summer_diff(c)
    assert diff == 0


def test_summer_diff1():
    swe = np.zeros((3000,50,50))
    a = analysis.Analysis(datetime.date(1993,1,1), swe)
    c = a.summer_length(swe)
    diff, heatmap = a.summer_diff(c)
    assert np.shape(heatmap) == (50,50)
