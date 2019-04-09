# Unit Testing for SWEpy
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

def set_login_test(self, username = 'test', password = 'test'):
        """
        Monkey patched set_login function 
        """
        self.local_session = True
        self.nD = nsidcDownloader.nsidcDownloader(folder = os.getcwd(), no_auth=True)
        self.nD.username = 'test'
        self.nD.password = 'test'


swepy.set_login = set_login_test

    

def test_check_params_false():
    start = datetime.date(2010,1,1)
    ul = [66,-145]
    lr = [73,-166]
    s1 = swepy(os.getcwd(), start, start, ul)
    assert s1.check_params() == False
    

def test_check_params_true():
    start = datetime.date(2010,1,1)
    ul = [66,-145]
    lr = [76,-166]
    s1 = swepy(os.getcwd(), start, start, ul, lr, username = 'test', password = 'test')
    assert s1.check_params() == True


def test_set_params_bounds():
    start = datetime.date(2010,1,1)
    s1 = swepy(os.getcwd(), start, start, username = 'test', password = 'test')
    s1.set_grid(ul = [66, -145], lr = [73,-166])
    assert s1.check_params() == True


def test_set_params_auth():
    start = datetime.date(2010,1,1)
    s1 = swepy(os.getcwd(), start, start, ul = [66,-145], lr = [73,-166])
    s1.set_login(username = 'test', password = 'test')
    assert s1.check_params() == True


def test_set_params_dates():
    s1 = swepy(os.getcwd(), ul = [66,-145], lr = [73,-166], username = 'test', password = 'test')
    s1.set_dates(start = datetime.date(2010,1,1), end = datetime.date(2010,1,1))
    assert s1.check_params() == True


def test_get_grid_N():
    s1 = swepy(os.getcwd())
    lat1 = 45
    lat2 = 80
    assert s1.get_grid(lat1, lat2) == "N"


def test_get_grid_T():
    s1 = swepy(os.getcwd())
    lat1 = 30
    lat2 = 30
    assert s1.get_grid(lat1,lat2) == "T"


def test_get_grid_S():
    s1 = swepy(os.getcwd())
    lat1 = -50
    lat2 = -80
    assert s1.get_grid(lat1, lat2) == "S"


def test_get_grid_fails():
    s1 = swepy(os.getcwd())
    lat1 = -62
    lat2 = 70
    with pytest.raises(Exception):
        s1.get_grid(lat1,lat2)

def test_get_xy_N():
    ll_ul = [ 62, -140]
    ll_lr = [73, -166]
    s1 = swepy(os.getcwd(), ul = ll_ul, lr = ll_lr)
    list1 = s1.get_xy(ll_ul, ll_lr)
    assert list1 == [-1988822.7284991546, 2370186.631721887, -457544.8408031743, 1835112.1237310767]

def test_get_xy_S():
    ll_lr = [-80,9]
    ll_ul = [-69, -16]
    s1 = swepy(os.getcwd(), ul = ll_ul, lr = ll_lr)
    list1 = s1.get_xy(ll_ul, ll_lr)
    assert list1 == [-642633.6942027304, 2241130.027261448,174488.41818780638, 1101676.5146265002]

def test_get_xy_none():
    ll_lr = None
    ll_ul = None
    s1 = swepy(os.getcwd())
    with pytest.raises(Exception):
        s1.get_xy(ll_ul, ll_lr)


def test_get_file_high():
    #path = tmpdir.mkdir("tmp")
    s1 = swepy(os.getcwd(), ul = 'N', lr = 'N', username = 'test', password = 'test')
    date = datetime.datetime(2010,1,1)
    file = s1.get_file(date, "19H")
    assert file == {'protocol':'http', 'server':'localhost:8000','datapool':'MEASURES','resolution': '6.25km','platform': 'F17','sensor': 'SSMIS',
                    'date1': datetime.datetime(2010, 1, 1),
                    'date2': datetime.datetime(2010, 1, 1),
                    'channel': '19H','grid': 'N','dataversion': 'v1.3',
                    'pass': 'M','algorithm': 'SIR'}


def test_get_file_low():
    s1 = swepy(os.getcwd(), ul = 'N', lr = 'N', username = 'test', password = 'test', high_res=False)
    date = datetime.datetime(2010,1,1)
    file = s1.get_file(date, "19H")
    assert file == {'protocol':'http', 'server':'localhost:8000','datapool':'MEASURES','resolution': '25km','platform': 'F17','sensor': 'SSMIS',
                    'date1': datetime.datetime(2010, 1, 1),
                    'date2': datetime.datetime(2010, 1, 1),
                    'channel': '19H','grid': 'N','dataversion': 'v1.3',
                    'pass': 'M','algorithm': 'GRD'}


def test_gf_low_var1():
    s1 = swepy(os.getcwd(), ul = 'N', lr = 'N', username = 'test', password = 'test', high_res=False)
    date = datetime.datetime(2003,11,6)
    file = s1.get_file(date, "19H")
    assert file == {'protocol':'http', 'server':'localhost:8000','datapool':'MEASURES','resolution': '25km','platform': 'F14','sensor': 'SSMI',
                    'date1': datetime.datetime(2003,11,6),
                    'date2': datetime.datetime(2003,11,5),
                    'channel': '19H','grid': 'N','dataversion': 'v1.3',
                    'pass': 'M','algorithm': 'GRD'}

def test_gf_low_var2():
    s1 = swepy(os.getcwd(), ul = 'N', lr = 'N', username = 'test', password = 'test', high_res=False)
    date = datetime.datetime(2006,11,4)
    file = s1.get_file(date, "19H")
    assert file == {'protocol':'http', 'server':'localhost:8000','datapool':'MEASURES','resolution': '25km','platform': 'F15','sensor': 'SSMI',
                    'date1': datetime.datetime(2006,11,4),
                    'date2': datetime.datetime(2006,11,3),
                    'channel': '19H','grid': 'N','dataversion': 'v1.3',
                    'pass': 'M','algorithm': 'GRD'}

def test_gf_low_TA():
    s1 = swepy(os.getcwd(), ul = 'T', lr = 'T', username = 'test', password = 'test', high_res=False)
    date = datetime.datetime(2006,11,4)
    file = s1.get_file(date, "19H")
    assert file == {'protocol':'http', 'server':'localhost:8000','datapool':'MEASURES','resolution': '25km','platform': 'F15','sensor': 'SSMI',
                    'date1': datetime.datetime(2006,11,4),
                    'date2': datetime.datetime(2006,11,3),
                    'channel': '19H','grid': 'T','dataversion': 'v1.3',
                    'pass': 'A','algorithm': 'GRD'}


def test_safe_subtract1():
    s1 = swepy(os.getcwd())
    tb19 = np.ones((1,152,153))
    tb37 = np.ones((1,154,153))
    tb = s1.safe_subtract(tb19,tb37)
    assert np.shape(tb) == (1,151,152)


def test_safe_subtract2():
        s1 = swepy(os.getcwd())
        tb19 = np.ones((1,154,152))
        tb37 = np.ones((1,152,153))
        tb = s1.safe_subtract(tb19,tb37)
        assert np.shape(tb) == (1,151,151)



def test_scrape_fail():
    date = datetime.date(2010,1,1)
    ul = 'N'
    lr = 'N'
    s1 = swepy(os.getcwd(),start = date, end = date, ul = 'N', lr = 'N', username = 'test', password = 'test')
    list1 = glob.glob("*.nc")
    assert list1 != ['NSIDC-0630-EASE2_N3.125km-F17_SSMIS-2010002-37H-M-SIR-CSU-v1.3.nc','NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010002-19H-M-SIR-CSU-v1.3.nc']

def test_scrape():
    date = datetime.date(2010,1,1)
    ul = 'N'
    lr = 'N'
    s1 = swepy(os.getcwd(),start = date, end = date, ul = 'N', lr = 'N', username = 'test', password = 'test')
    s1.scrape()
    list1 = glob.glob("*.nc")
    assert (list1 == ['NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc','NSIDC-0630-EASE2_N3.125km-F17_SSMIS-2010001-37H-M-SIR-CSU-v1.3.nc'] or 
        list1 == ['NSIDC-0630-EASE2_N3.125km-F17_SSMIS-2010001-37H-M-SIR-CSU-v1.3.nc','NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc'])

def test_subset():
    if not os.path.exists('sub'):
        os.mkdir('sub')
    date = datetime.date(2010,1,1)
    s1 = swepy(os.getcwd(),ul = [66,-145], lr = [71,-166])
    setattr(s1,'down19list',['NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc'])
    setattr(s1,'down37list',['NSIDC-0630-EASE2_N3.125km-F17_SSMIS-2010001-37H-M-SIR-CSU-v1.3.nc'])
    path = os.getcwd()+'/'#'/tests/data/MEASURES/NSIDC-0630.001/2010.01.01/'
    out_dir = path + '/sub/'
    s1.subset(in_dir=path,out_dir19=out_dir,out_dir37=out_dir)
    os.chdir(out_dir)
    list1 = glob.glob('*.nc')
    assert os.stat(list1[0]).st_size < 100000

def test_concat():
    date = datetime.date(2010,1,1)
    s1 = swepy(os.getcwd(),ul = [66,-145], lr = [73,-166])
    setattr(s1,'sub19list',['NSIDC-0630-EASE2_N6.25km-F17_SSMIS-2010001-19H-M-SIR-CSU-v1.3.nc'])
    setattr(s1,'sub37list',['NSIDC-0630-EASE2_N3.125km-F17_SSMIS-2010001-37H-M-SIR-CSU-v1.3.nc'])
    s1.concatenate()
    list1 = glob.glob("*all*")
    assert 'all_days_19H.nc' in list1

def test_get_directories():
    s1 = swepy(os.getcwd())
    assert os.path.exists(os.getcwd()+'/data') == True



def test_grid_to_geo():
        row = 359.5
        col = 359.5
        n25g = ease2Transform.ease2Transform("EASE2_N25km")
        assert n25g.grid_to_geographic(row,col) == (89.99999999999997,0.)


def test_clean_dirs():
    s1 = swepy(os.getcwd())
    try:
        s1.clean_dirs()
        list1 = glob.glob("*nc")
        assert list1 == []
    except PermissionError: 
        assert True

def test_final_concat_fail():
     s1 = swepy(os.getcwd())
     res = s1.final_concat()
     assert res == ('all_days_19H.nc', 'all_days_37H.nc')

# def test_scrape_all():
#     date = datetime.datetime(2010,1,1)
#     s1 = swepy(os.getcwd(), start = date, end = date,ul = 'N', lr = 'N', username = 'test', password='test')
#     res = s1.scrape_all()
#     assert res == ['all_days_19H.nc', 'all_days_37H.nc']
    