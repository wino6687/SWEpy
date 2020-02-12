import swepy.analysis as analysis
import pytest
import numpy as np
import pandas as pd
import matplotlib
import datetime


@pytest.fixture
def a():
    swe = np.zeros((3000, 50, 50))
    return analysis.Analysis(datetime.date(1993, 1, 1), swe)


def test_make_df_time():
    """
    Make sure timestamp is correctly created in dataframe
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    t = a.make_df()
    print(type(t.time[0]))
    assert t.time[0] == pd.Timestamp("1993-01-01 00:00:00")


def test_make_df_type():
    """
    Ensure make_df creates a proper dataframe (could be more meaningful)
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    t = a.make_df()
    assert type(t) == pd.DataFrame


def test_create_splits():
    """
    Ensure proper date splits are generated given specific date and size of array
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    years = a.create_year_splits()
    assert years == [0, 365, 730, 1095, 1460, 1826, 2191, 2556, 2921, 3000]


def test_count_melt_onset_mp():
    """
    Note: right now making zero matrix swe values
    - should maybe make fixture that has an instantiated analysis object with the swe cube inside
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    c = a.count_melt_onset()
    assert type(c) == pd.DataFrame


def test_mask_year_df():
    """
    Ensure proper structure of dataframe given a mask on 1994
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    df = a.make_df()
    df = a.mask_year_df(df, 1994)
    assert df.iloc[0].time.year == 1994


def test_melt_date_year():
    """
    Ensure a dictionary is returned for counting melt date by year
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    df = a.make_df()
    counts = a.melt_date_year(df)
    assert type(counts) == dict


def test_count_melt():
    """
    Ensure dataframe is returned by __count_melt (could be more meaningful?)
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    c = a._count_melt(swe)
    assert type(c) == pd.DataFrame


def test_summer_length():
    """
    Ensure summer length info is returned in a dictionary
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    c = a.summer_length(swe)
    assert type(c) == dict


def test_summer_length2():
    """
    Ensure proper dict of dicts from summer_length
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    c = a.summer_length(swe)
    assert type(c[(1, 1)]) == dict


def test_summer_diff1():
    """
    Ensure summer length difference is close to zero on test array
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    c = a.summer_length(swe)
    diff, heatmap = a.summer_diff(c)
    if diff < 0.1:
        diff = 0
    assert diff == 0


def test_summer_diff2():
    """
    Make sure heatmap is proper size
    """
    swe = np.zeros((1000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    c = a.summer_length(swe)
    diff, heatmap = a.summer_diff(c)
    assert np.shape(heatmap) == (50, 50)


def test_display_diffmap():
    """
    Ensure proper image type returned for summer diff map
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    c = a.summer_length(swe)
    diff, heatmap = a.summer_diff(c)
    im = a.display_summer_change(True)
    assert type(im) == matplotlib.image.AxesImage


def test_display_melt():
    """
    Ensure proper figure type returned for summer diff map
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    melt = a.melt_date_year(a._count_melt(swe))
    fig = a.display_melt_onset_change(melt, 1993, 1995, True)
    assert type(fig) == matplotlib.figure.Figure


def test_display_melt_fail1():
    """
    Ensure excpetion raised when dates are in reverse order
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    melt = a.melt_date_year(a._count_melt(swe))
    with pytest.raises(Exception):
        a.display_melt_onset_change(melt, 1944, 1993)


def test_display_melt_fail2():
    """
    Ensure exception is raised when dates are nonsensical
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 1, 1), swe)
    melt = a.melt_date_year(a._count_melt(swe))
    with pytest.raises(Exception):
        a.display_melt_onset_change(melt, 1993, 1944)


def test_create_splits_mid_year():
    """
    Make sure that year splits are properly generated when not using first day of year
    as start of time series
    """
    swe = np.zeros((3000, 50, 50))
    a = analysis.Analysis(datetime.date(1993, 5, 1), swe)
    years = a.create_year_splits()
    assert years[0] == 121
