# author: Will Norris --> wino6687@colorado.edu
from datetime import datetime, timedelta
import requests
from swepy.nsidcDownloader import nsidcDownloader
import numpy as np
from netCDF4 import Dataset
from skimage.measure import block_reduce
import pandas as pd
from nco import Nco
import os
from tqdm import tqdm
import glob
import cartopy.crs as ccrs

nco = Nco()

class swepy():
    def __init__(self, working_dir=None, start=None, end=None, ul=None, lr=None, username=None, password=None,
                outfile19 = 'all_days_19H.nc', outfile37 = 'all_days_37H.nc', high_res = True):
        '''User instantiates the class with working directory,
        date ranges, and lat/lon bounding coords. constructor gets
        the datetime list, x/y coords, and file directories'''
        # set whether we are scraping resampled data or not
        if high_res:
            self.high_res = True
        else:
            self.high_res = False

        # set the working directory
        if working_dir is None:
            self.working_dir = os.getcwd()
        else:
            self.working_dir = working_dir

        # create directories for data
        self.path19, self.path37, self.wget = self.get_directories(self.working_dir)

        self.outfile_19 = outfile19
        self.outfile_37 = outfile37

        self.username = username
        self.password = password

        self.geod = None
        self.e2n = None

        self.geo_list = None
        self.grid = None

        # if user gave date range, store it
        if start is not None and end is not None:
            self.dates = pd.date_range(start, end)
        else:
            self.dates = None

        # if user inputs a grid name, then scrape whole grid
        # otherwise find the grid that fits coordinates
        if ul is not None and lr is not None:
            if ul == "N" and lr == "N":
                self.grid = "N"
                self.subBool = False
                self.geo_list = "N"
            elif ul == "T" and lr == "T":
                self.grid = "T"
                self.subBool = False
                self.geo_list = "T"
            elif ul == "S" and lr == "S":
                self.grid = "S"
                self.subBool = False
                self.geo_list = "S"
            else:
                self.subBool = True
                self.get_grid(ul[1], lr[1])
                self.geo_list = self.get_xy(ul, lr)
                self.center = [ul[1], ul[0]]

        self.down19list = []
        self.down37list = []
        self.sub19list = []
        self.sub37list = []
        self.concatlist = [None, None]
        self.concat19list = []
        self.concat37list = []
        if username == 'test' and password == 'test':
            self.local_session = True
            self.nD = nsidcDownloader.nsidcDownloader(folder = os.getcwd(), no_auth=True)
        elif username is not None and password is not None:
            self.local_session = False
            self.nD = nsidcDownloader.nsidcDownloader(folder = self.wget, username = username, password = password)
        else:
            print("No Earthdata credentials given")
            # do i want to create directories if no credentials are passed??
            self.nD = None

    def set_params(self, start=None, end=None, username=None, password=None, ul=None, lr=None):
        '''
        Function to allow users to add information to the class after already instantiating.
        Allows user to instantiate class with just date range and credentials, then add coordinates
        for subsetting later without losing the download lists
        '''
        if start is not None and end is not None:
            print("Setting the date range...")
            self.dates = pd.date_range(start, end)
            print("Success!")
        if username is not None and password is not None:
            print("Checking your credentials...")
            if username == 'test' and password == 'test':
                self.username = username
                self.password = password
                self.local_session = True
                self.nD = nsidcDownloader.nsidcDownloader(folder = os.getcwd(), no_auth=True)
            else:
                self.username = username
                self.password = password
                self.local_session = False
                self.nD = nsidcDownloader.nsidcDownloader(folder = self.wget, username = username, password = password)
            print("Success!")
        if ul is not None and lr is not None:
            print("Setting the bounding coordinates...")
            self.subBool = True
            self.get_grid(ul[1], lr[1])
            self.geo_list = self.get_xy(ul,lr)
            self.center = [ul[1], ul[0]]
            print("Success!")
        return


    def check_params(self):
        '''
        Helper function to check that all the class members are set before
        attempting to web scrape or subset.
        '''
        proceed = True
        params = {"dates":self.dates, "bounding coordinates":self.geo_list, "grid":self.grid, "username":self.username, "password":self.password}
        for key, value in params.items():
            if value is None:
                print("{} needs to be set by 'set_params'".format(key))
                proceed = False
        if proceed == False:
            print("Please use the set_params function to set missing parameters,\
                    see the documentation for guidance")
        return proceed


    def get_grid(self, lat1, lat2):
        '''Check which regions the lats fall into. based
        on the grid, instantiate the ease grid conversion object.

        Parameters: Upper Left Latitude, Lower Right Latitude
        '''
        if (lat1 < 50 and lat2 < 50) and (lat1 > -50 and lat2 > -50): # mid lat
            self.grid = "T"
            print("SWEpy 1.1.2 does not currently support subsetting Equatorial images \n The entire image will be scraped")
        elif (lat1 > 40 and lat2 > 40) and (lat1 <90 and lat2 < 90): # north
            self.grid = "N"
            self.geod = ccrs.Geodetic()
            self.e2n = ccrs.LambertAzimuthalEqualArea(central_latitude=90.0)
        elif (lat1 < -40 and lat2 < -40) and (lat1 > -90 and lat2 > -90): # South
            self.grid = "S"
            self.geod = ccrs.Geodetic()
            self.e2n = ccrs.LambertAzimuthalEqualArea(central_latitude=-90.0)
        else:
            print("SWEpy currently only supports subsetting study areas with a study area in the North or South imagery \
            \nOverlappig study areas can cause erros, and require more than one region of imagery")
            raise ValueError
        return self.grid


    def get_directories(self, path):
        '''Given a working directory, Check
        for the proper sub-directories and
        then make them if absent'''
        os.chdir(path)
        wget = path + "/data/wget/"
        path19 = path + "/data/Subsetted_19H/"
        path37 = path + "/data/Subsetted_37H/"

        if not os.path.exists(wget):
            os.makedirs(wget)
        if not os.path.exists(path19):
            os.makedirs(path19)
        if not os.path.exists(path37):
            os.makedirs(path37)
        return path19, path37, wget


    def get_xy(self, ll_ul, ll_lr):
        '''Use cartopy scripts to convert user inputted
        lat/lon into Ease grid 2.0 coordinates'''
        if ll_ul is None or ll_lr is None:
            print("You must enter bounding coordinates when instantiating the class")
            raise ValueError
        xul,yul = self.e2n.transform_point(
                x = ll_ul[0],
                y = ll_ul[1],
                src_crs = self.geod)
        xlr, ylr = self.e2n.transform_point(
                x = ll_lr[0],
                y = ll_lr[1],
                src_crs = self.geod)
        return [xul, yul, xlr, ylr]


    def subset(self, scrape = False, in_dir=None,out_dir19=None,out_dir37=None):
        '''get the files from wget directory
        and subset them geographically based on
        coords from constructor'''
        os.chdir(self.working_dir + "/data")
        for file in tqdm(self.down19list):
            outfile = self.path19 + file if out_dir19 is None else out_dir19 + file
            infile = self.wget + file if in_dir is None else in_dir + file
            opt = [
                "-d x,%f,%f" % (self.geo_list[0],self.geo_list[2]),
                "-d y,%f,%f" % (self.geo_list[3],self.geo_list[1]),
                "-v TB"
            ]
            nco.ncks(input=infile, output=outfile, options=opt)
            self.sub19list.append(outfile)
            os.remove(infile)

        for file in tqdm(self.down37list):
            outfile = self.path37 + file if out_dir37 is None else out_dir37 + file
            infile = self.wget + file if in_dir is None else in_dir + file
            opt = [
                "-d x,%f,%f" % (self.geo_list[0],self.geo_list[2]),
                "-d y,%f,%f" % (self.geo_list[3],self.geo_list[1]),
                "-v TB"
            ]
            nco.ncks(input=infile, output=outfile, options=opt)
            self.sub37list.append(outfile)
            os.remove(infile)
        self.down19list = []
        self.down37list = []
        return


    def scrape_all(self):
        '''Function to ensure we subset
         and concatenate every year!
         Implements the whole workflow!'''
        if self.check_params() == False:
            return
        if len(self.dates) <= 300:
            self.scrape()
            if self.subBool:
                self.subset()
            return self.concatenate()
        else:
            comp_list = [self.dates[x:x + 300] for x in range(0, len(self.dates), 300)]
            for count, subList in enumerate(comp_list):
                name19 = 'temp19_' + str(count) + '.nc'
                name37 = 'temp37_' + str(count) + '.nc'
                self.scrape(subList)
                self.subset()
                self.concatenate(name19, name37, all = True)
            return self.final_concat()


    def get_file(self, date, channel): # add more defaulting params
        '''Function that uses date and channel to
        find optimal file composition and return the
        file params for the web scraper's use.'''
        sensors = {1992: 'F11', 1993: 'F11', 1994: 'F11', 1995: 'F11', 1996: 'F13', 1997: 'F13', 1998: 'F13',
                1999: 'F13', 2000: 'F13', 2001: 'F13', 2002: 'F13', 2003: 'F15', 2004: 'F15', 2005: 'F15', 2006: 'F15',
                2007: 'F15', 2008: 'F16', 2009: 'F17', 2010: 'F17', 2011: 'F17', 2012: 'F17', 2013: 'F17', 2014: 'F18',
                2015: 'F19',2016: 'F18'}
        sensor = sensors[date.year]
        ssmi_s = "SSMIS" if sensors[date.year] in ['F16', 'F17', 'F18', 'F19'] else "SSMI"
        if self.high_res:
            resolution = '6.25km' if channel == '19H' else '3.125km'
            algorithm = 'SIR'
            date2 = date
        else:
            resolution = '25km'
            algorithm = 'GRD'
            if datetime(2003,1,1) <= date < datetime(2004,4,9):
                date2 = date - timedelta(days = 1)
            else:
                date2 = date
        file = {
            "protocol": "http" if self.local_session else "https",
            "server": "localhost:8000" if self.local_session else "n5eil01u.ecs.nsidc.org",
            "datapool": "MEASURES",
            "resolution": resolution,
            "platform": sensor,
            "sensor": ssmi_s,
            "date1": date,
            "date2": date2,
            "channel": channel,
            "grid": self.grid,
            "dataversion": 'v1.3',
            "pass": "A" if self.grid == "T" else "M",
            "algorithm": algorithm
        }
        return file


    def concatenate(self, outname19 = None, outname37 = None, all = False):
        '''Function to concatenate files in the subsetted data
        folders. Input parameter is simply to allow for nesting of
        functions.'''
        if self.subBool == False:
            self.sub19list = self.down19list
            self.sub37list = self.down37list
            os.chdir(self.wget)
        outname19 = self.outfile_19 if outname19 is None else outname19
        outname37 = self.outfile_37 if outname37 is None else outname37
        # Concatenate 19GHz files:
        if len(self.sub19list) != 0:
            nco.ncrcat(input=self.sub19list, output = outname19, options=["-O"])
            for file in self.sub19list: os.remove(file)
            self.sub19list = []
            if all:
                self.concat19list.append(outname19)
            else:
                self.concatlist[0] = outname19
        else:
            print("No 19Ghz Files to Concatenate")
        # Concatenate 37GHz files:
        if len(self.sub37list) != 0:
            nco.ncrcat(input = self.sub37list, output = outname37, options = ["-O"])
            for file in self.sub37list: os.remove(file)
            self.sub37list = []
            if all:
                self.concat37list.append(outname37)
            else:
                self.concatlist[1] = outname37
        else:
            print("No 37Ghz Files to Concatenate")
        return


    def final_concat(self):
        '''
        function to manage the final concatenation for scrape_all
        '''
        if len(self.concat19list) != 0:
            nco.ncrcat(input=self.concat19list, output = self.outfile_19, options=["-O"])
            self.concatlist[0] = self.outfile_19
        else:
            print("No 19Ghz Files to Concatenate")
        if len(self.concat37list) != 0:
            nco.ncrcat(input = self.concat37list, output = self.outfile_37, options = ["-O"])
            self.concatlist[1] = self.outfile_37
        else:
            print("No 37Ghz Files to Concatenate")

        # clean out files that were concat
        for file in self.concat19list: os.remove(file)
        for file in self.concat37list: os.remove(file)
        self.concat19list = []
        self.concat37list = []
        return self.outfile_19, self.outfile_37


    def scrape(self, dates = None):
        '''
        Wrapper function to interface between swepy and nD
        '''
        if self.local_session == False:
            if self.check_params() == False:
                return
        if dates is None: # letting class choose all dates
            dates = self.dates
        for date in tqdm(dates):
            file19 = self.get_file(date, "19H")
            file37 = self.get_file(date, "37H")
            result1 = self.nD.download_file(**file19)
            if result1 == False:
                try:
                    result1 = self.nD.download_file(**file19)
                except:
                    print('failing on 19H {}'.format(date))
                    pass
            result2 = self.nD.download_file(**file37)
            if result2 == False:
                try:
                    result2 = self.nD.download_file(**file37)
                except:
                    print('failing on 37H on {}'.format(date))
                    pass
            self.down19list.append(result1[0])
            self.down37list.append(result2[0])
        return (result1, result2)


    def safe_subtract(self, tb19, tb37):
        '''Check size of each file, often the 19 and 37
            files are one unit off of eachother. This will
            chop the larger one to match the smaller one.'''
        shape1 = np.shape(tb19)
        shape2 = np.shape(tb37)
        s1 = [shape1[0], shape1[1], shape1[2]]
        s2 = [shape2[0], shape2[1], shape2[2]]
        if s1[1] < s2[1]:
            s2[1] = s1[1]
        elif s1[1] > s2[1]:
            s1[1] = s2[1]
        if s1[2] < s2[2]:
            s2[2] = s1[2]
        elif s1[2] > s2[2]:
            s1[2] = s2[2]
        tb19 = tb19[:, :s1[1]-1, :s1[2]-1]
        tb37 = tb37[:, :s2[1]-1, :s2[2]-1]
        tb  = tb19 - tb37
        return tb


    def clean_dirs(self):
        os.chdir(self.wget)
        files = glob.glob("*")
        for f in files:
            os.remove(f)
        os.chdir(self.path19)
        files = glob.glob("*")
        for f in files:
            os.remove(f)
        os.chdir(self.path37)
        files = glob.glob("*")
        for f in files:
            os.remove(f)
        return
