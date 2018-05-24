import datetime
import requests
from swepy.nsidcDownloader import nsidcDownloader
import numpy as np
from netCDF4 import Dataset
from skimage.measure import block_reduce
from mapboxgl.utils import *
from mapboxgl.viz import *
import pandas as pd
from swepy.Ease2Transform import Ease2Transform
from nco import Nco
import os
from tqdm import tqdm
nco = Nco()

class swepy():
    '''Class Members'''
    def __init__(self, working_dir, start, end, ul, lr,
                outfile19 = 'all_days_19H.nc', outfile37 = 'all_days_37H.nc',
                username = 'wino6687', password = 'Desmo12@'):
        '''User instantiates the class with working directory,
        date ranges, and lat/lon bounding coords. constructor gets
        the datetime list, x/y coords, and file directories'''
        self.working_dir = working_dir
        self.path19, self.path37, self.wget = self.get_directories(working_dir)

        self.N3 = Ease2Transform.Ease2Transform("EASE2_N3.125km")

        self.outfile_19 = outfile19
        self.outfile_37 = outfile37

        self.username = username
        self.password = password

        self.dates = pd.date_range(start, end)
        self.geo_list = self.get_xy(ul, lr)

        self.down19list = []
        self.down37list = []
        self.sub19list = []
        self.sub37list = []
        self.concatlist = [None, None]

        self.nD = nsidcDownloader.nsidcDownloader(folder = self.wget, username = username, password = password)


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
        '''Use NSIDC scripts to convert user inputted
        lat/lon into Ease grid 2.0 coordinates'''
        row, col = self.N3.geographic_to_grid(ll_ul[0], ll_ul[1])
        xul, yul = self.N3.grid_to_map(row, col)
        row, col = self.N3.geographic_to_grid(ll_lr[0], ll_lr[1])
        xlr, ylr = self.N3.grid_to_map(row, col)
        geo_list = [xul, yul, xlr, ylr]
        return geo_list


    def subset(self, scrape = False):
        '''get the files from wget directory
        and subset them geographically based on
        coords from constructor'''
        os.chdir(self.working_dir + "/data")
        for file in tqdm(self.down19list):
            outfile = self.path19 + file
            infile = self.wget + file
            opt = [
                "-d x,%f,%f" % (self.geo_list[0],self.geo_list[2]),
                "-d y,%f,%f" % (self.geo_list[3],self.geo_list[1]),
                "-v TB"
            ]
            nco.ncks(input=infile, output=outfile, options=opt)
            self.sub19list.append(outfile)
            os.remove(infile)

        for file in tqdm(self.down37list):
            outfile = self.path37 + file
            infile = self.wget + file
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
        outfile19 = 'all_days_19H.nc'
        outfile37 = 'all_days_37H.nc'
        if len(self.dates) <= 133:
            for date in self.dates:
                file19 = self.get_file(date, "19H")
                file37 = self.get_file(date, "37H")
                self.down19list.append(self.nD.download_file(**file19))
                self.down37list.append(self.nD.download_file(**file37))
            self.subset()
            return self.concatenate()
        else:
            comp_list = [self.dates[x:x + 100] for x in range(0, len(self.dates), 100)]
            for count, subList in enumerate(comp_list):
                for date in subList:
                    file19 = get_file(date, "19H")
                    file37 = get_file(date, "37H")
                    self.down19list.append(self.nD.download_file(**file19))
                    self.down37list.append(self.nD.download_file(**file37))
                self.subset()
            return self.concatenate()


    def get_file(self, date, channel): # add more defaulting params
        '''Function that uses date and channel to
        find optimal file composition and return the
        file params for the web scraper's use.'''
        sensors = {1992: 'F11', 1993: 'F11', 1994: 'F11', 1995: 'F11', 1996: 'F13', 1997: 'F13', 1998: 'F13',
                1999: 'F13', 2000: 'F13', 2001: 'F13', 2002: 'F13', 2003: 'F15', 2004: 'F15', 2005: 'F15', 2006: 'F15',
                2007: 'F15', 2008: 'F16', 2009: 'F17', 2010: 'F17', 2011: 'F17', 2012: 'F17', 2013: 'F17', 2014: 'F18',
                2015: 'F19'}
        ssmi_s = "SSMIS" if sensors[date.year] in ['F16', 'F17', 'F18', 'F19'] else "SSMI"
        resolution = '6.25km' if channel == '19H' else '3.125km'
        file = {
            "resolution": resolution,
            "platform": sensors[date.year],
            "sensor": ssmi_s,
            "date": date,
            "channel": channel,
            "dataversion": 'v1.3' if date.year == 2015 else 'v1.2'
        }
        return file

    def concatenate(self, subset = False):
        '''Function to concatenate files in the subsetted data
        folders. Input parameter is simply to allow for nesting of
        functions.'''
        # Concatenate 19GHz files:
        if len(self.sub19list) != 0:
            nco.ncrcat(input=self.sub19list, output = self.outfile_19, options=["-O"])
            self.concatlist[0] = self.outfile_19
        else:
            print("No 19Ghz Files to Concatenate")
        # Concatenate 37GHz files:
        if len(self.sub37list) != 0:
            nco.ncrcat(input = self.sub37list, output = self.outfile_37, options = ["-O"])
            self.concatlist[1] = self.outfile_37
        else:
            print("No 37Ghz Files to Concatenate")

        # clean out files that were concat
        for file in self.sub19list: os.remove(file)
        for file in self.sub37list: os.remove(file)
        self.sub19list = []
        self.sub37list = []
        return self.outfile_19, self.outfile_37


    def scrape(self):
        '''Wrapper function to allow more selective use of just the
            web scraper'''
        for date in self.dates:
            file19 = self.get_file(date, "19H")
            file37 = self.get_file(date, "37H")
            self.down19list.append(self.nD.download_file(**file19))
            self.down37list.append(self.nD.download_file(**file37))
        return




    def plot_a_day(self, token):
        '''read tb,x,y data from final files,
        with the purpose of plotting.'''
        #os.chdir(path + '/data/Subsetted_19H')
        fid_19H = Dataset(self.concatlist[0], "r", format="NETCDF4")
        #os.chdir(path + '/data/Subsetted_37H')
        fid_37H = Dataset(self.concatlist[1], "r", format="NETCDF4")
        x = fid_19H.variables['x'][:]
        y = fid_37H.variables['y'][:]
        tb_19H = fid_19H.variables['TB'][:]
        tb_37H = fid_37H.variables['TB'][:]
        tb_37H = block_reduce(tb_37H, block_size = (1,2,2), func = np.mean)
        tb= tb_19H  - tb_37H
        lats = np.zeros((len(y), len(x)), dtype=np.float64)
        lons = np.zeros((len(y), len(x)), dtype=np.float64)
        grid = Ease2Transform.Ease2Transform(gridname=fid_19H.variables["crs"].long_name)
        for i, xi in enumerate(x):
            for j, yj in enumerate(y):
                row, col = grid.map_to_grid(xi, yj)
                lat, lon = grid.grid_to_geographic(row, col)
                lats[j, i] = lat
                lons[j, i] = lon
        one_day = tb[0,:,:]
        df = pd.DataFrame(columns = ['lat', 'lon', 'swe'])
        for i in range(len(one_day[:,1])):
            for j in range(len(one_day[1,:])):
                df = df.append({'lat': lats[i][j], 'lon': lons[i][j], 'swe':one_day[i][j]}, ignore_index = True)
        df_to_geojson(df, filename = 'swe_1day.geojson',properties = ['swe'],lat = 'lat', lon = 'lon')
        measure = 'swe'
        color_breaks = [round(df[measure].quantile(q=x*0.1), 2) for x in range(1,9)]
        color_stops = create_color_stops(color_breaks, colors='YlGnBu')
        print(color_stops)
        # Create the viz from the dataframe
        viz = CircleViz('swe_1day.geojson',
                        access_token=token,
                        color_property = "swe",
                        color_stops = color_stops,
                        center = (-154, 67),
                        zoom = 3,
                        below_layer = 'waterway-label')

        viz.show()
