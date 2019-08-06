# author: Will Norris --> wino6687@colorado.edu, Earth Lab, CU Boulder
from datetime import datetime, timedelta
from swepy.nsidcDownloader import nsidcDownloader
from swepy.ease2Transform import ease2Transform
import numpy as np
from netCDF4 import Dataset
from skimage.measure import block_reduce
import pandas as pd
from nco import Nco
import os
from tqdm import tqdm
import glob

nco = Nco()


class Swepy:
    """
    Class to facilitate the scraping/subsetting/concatenating of tB files for SWE analysis.
    """

    def __init__(
        self,
        working_dir=None,
        start=None,
        end=None,
        ul=None,
        lr=None,
        username=None,
        password=None,
        outfile19="all_days_19H.nc",
        outfile37="all_days_37H.nc",
        high_res=True,
    ):
        """
        Parameters
        ----------
        working_dir: str
            directory to store data directory
        start: datetime
            start date for scraping
        end: datetime
            end date for scraping
        ul: List[int, int]
            upper left bounding coordinates [lat, lon]
        lr: List[int, int]
            lower right bounding coordinates [lat,lon]
        username: str
            username for Earth Data login
        password: str
            password for Earth Data login
        outfile19: str
            name of final output file, 19 19GHz
        outfile37: str
            name of final output file, 37 GHz
        high_res: bool
            True: scrape high resolution files, False: low resolution
        """

        # set whether we are scraping resampled data or not
        if high_res:
            self.high_res = True
        else:
            self.high_res = False

        # set the working directory
        if working_dir is None:
            print(
                "No working directory passed, using current working directory: {}".format(
                    os.getcwd()
                )
            )
            self.working_dir = os.getcwd()
        else:
            self.working_dir = working_dir

        # create directories for data
        self.wget, self.path19, self.path37 = self.get_directories(
            self.working_dir
        )

        self.outfile_19 = outfile19
        self.outfile_37 = outfile37

        self.ease = None
        self.geo_list = None
        self.grid = None

        self.set_dates(start, end)

        self.set_grid(ul, lr)

        self.down19list = []
        self.down37list = []
        self.sub19list = []
        self.sub37list = []
        self.concatlist = [None, None]
        self.concat19list = []
        self.concat37list = []

        self.set_login(username, password)

    def set_dates(self, start=None, end=None):
        """
        Set date range using start and end datetime objects

        Parameters
        ----------
        start: datetime
            start date for scraping
        end: datetime
            end date for scraping
        """

        try:
            self.dates = pd.date_range(start, end)
        except ValueError:
            self.dates = None
            print("No valid dates given")
        return

    def set_login(self, username=None, password=None):
        """
        Set login credentials and login to earth data

        Parameters
        ----------
        username: String
            Earthdata username
        password: String
            Earthdata password
        """

        if username is not None and password is not None:
            print("Logging you into Earth Data...")
            self.local_session = False
            self.nD = nsidcDownloader.nsidcDownloader(
                folder=self.wget, username=username, password=password
            )
            print("Success!")
        else:
            print(
                "No credentials given, please use 'set_login' to login when ready."
            )
            self.nD = None
        return

    def set_grid(self, ul=None, lr=None):
        """
        Set grid corners, and convert to xy

        Parameters
        ----------
        ul: char or [float,float]
            upper left bounding coordinates or grid name (N,S,T)
        lr: [float, float]
            lower right bounding coordinates (not needed for entire grid)
        """

        if ul is not None and lr is not None:
            # if ul is an entire grid, that is the grid we want to scrape
            if ul in ["N", "S", "T"]:
                self.grid = ul
                self.subBool = False
                self.geo_list = ul
            else:  # if specific coords, we want to get the x_y ease coords that correspond
                self.subBool = True
                self.get_grid(ul[0], lr[0])
                self.geo_list = self.get_xy(ul, lr)
                self.center = [ul[1], ul[0]]
        else:
            print(
                "No usable bounding coordinates or grid given, \
             please specify bounds or a grid to scrape."
            )
        return

    def get_grid(self, lat1, lat2):
        """
        Check which regions the lats fall into. Based on the grid, instantiate the ease
        grid conversion object.

        Parameters
        ----------
        lat1: int
            Upper Left Latitude
        lat2: int
            Lower Right Latitude
        """

        if (lat1 < 50 and lat2 < 50) and (
            lat1 > -50 and lat2 > -50
        ):  # mid lat
            self.grid = "T"
            self.ease = ease2Transform.ease2Transform("EASE2_T3.125km")
        elif (lat1 > 40 and lat2 > 40) and (lat1 < 90 and lat2 < 90):  # north
            self.grid = "N"
            self.ease = ease2Transform.ease2Transform("EASE2_N3.125km")
        elif (lat1 < -40 and lat2 < -40) and (
            lat1 > -90 and lat2 > -90
        ):  # South
            self.grid = "S"
            self.ease = ease2Transform.ease2Transform("EASE2_S3.125km")
        else:
            print(
                "SWEpy currently only supports subsetting study areas with a study area in the North, South, or Equatorial imagery \
            \nOverlappig study areas can cause errors, and require more than one region of imagery"
            )
            raise ValueError
        return self.grid

    def get_directories(self, path):
        """
        Given a working directory, create data
        directories if non-existent

        Parameters
        ----------
        path: str
            working directory to create data directories
        """
        os.chdir(path)
        paths = [
            path + "/data/wget/",
            path + "/data/Subsetted_19H/",
            path + "/data/Subsetted_37H/",
        ]
        for path1 in paths:
            if not os.path.exists(path1):
                os.makedirs(path1)
        return paths[0], paths[1], paths[2]

    def get_xy(self, ll_ul, ll_lr):
        """
        Use nsidc scripts to convert user inputted
        lat/lon into Ease grid 2.0 coordinates

        Parameters
        -----------

        ll_ul: [float, float]
            Latitude and longitude for upper left coordinates
        ll_lr: [float, float]
            Latitude and longitude for lower right coordinates
        """

        if ll_ul is None or ll_lr is None:
            print(
                "You must enter bounding coordinates, please use 'set_grid()' to add coordinates"
            )
            raise ValueError
        row, col = self.ease.geographic_to_grid(ll_ul[0], ll_ul[1])
        xul, yul = self.ease.grid_to_map(row, col)
        row, col = self.ease.geographic_to_grid(ll_lr[0], ll_lr[1])
        xlr, ylr = self.ease.grid_to_map(row, col)
        return [xul, yul, xlr, ylr]

    def subset(
        self, scrape=False, in_dir=None, out_dir19=None, out_dir37=None
    ):
        """
        Get the files from wget directory
        and subset them geographically based on
        coords from constructor

        Parameters
        ----------

        scrape: Boolean
            Under the hood variable to allow for auto workflow

        in_dir: str
            (Optional) directory with wget data stored in it.
            Default: "working_dir/data/wget"

        out_dir19: str
            (Optional) directory to store output 19GHz files
            Default: "working_dir/data/Subsetted_19H/"

        out_dir37: str
            (Optional) directory to store output 37GHz files
            Default: "working_dir/data/Subsetted_37H"
        """

        os.chdir(self.working_dir + "/data")
        for file in tqdm(self.down19list):
            outfile = (
                self.path19 + file if out_dir19 is None else out_dir19 + file
            )
            infile = self.wget + file if in_dir is None else in_dir + file
            opt = [
                "-d x,%f,%f" % (self.geo_list[0], self.geo_list[2]),
                "-d y,%f,%f" % (self.geo_list[3], self.geo_list[1]),
                "-v TB",
            ]
            nco.ncks(input=infile, output=outfile, options=opt)
            self.sub19list.append(outfile)
            os.remove(infile)

        for file in tqdm(self.down37list):
            outfile = (
                self.path37 + file if out_dir37 is None else out_dir37 + file
            )
            infile = self.wget + file if in_dir is None else in_dir + file
            opt = [
                "-d x,%f,%f" % (self.geo_list[0], self.geo_list[2]),
                "-d y,%f,%f" % (self.geo_list[3], self.geo_list[1]),
                "-v TB",
            ]
            nco.ncks(input=infile, output=outfile, options=opt)
            self.sub37list.append(outfile)
            os.remove(infile)
        self.down19list = []
        self.down37list = []
        return

    def scrape_all(self):
        """
        Function to ensure we subset and concatenate every year!
        Implements the whole workflow!
        """

        if self.check_params() is False:
            return
        if len(self.dates) <= 300:
            self.scrape()
            if self.subBool:
                self.subset()
            return self.concatenate()
        else:
            comp_list = [
                self.dates[x : x + 300] for x in range(0, len(self.dates), 300)
            ]
            for count, subList in enumerate(comp_list):
                name19 = "temp19_" + str(count) + ".nc"
                name37 = "temp37_" + str(count) + ".nc"
                self.scrape(subList)
                if self.subBool:
                    self.subset()
                self.concatenate(name19, name37, all=True)
            return self.final_concat()

    def get_sensor(self, date):
        """
        Helper function to return optimal sensor for a given date

        Parameters
        -----------
        date: datetime.date()
            date to find sensor information
        """
        sensors = {
            1978: "NIMBUS7",
            1979: "NIMBUS7",
            1980: "NIMBUS7",
            1981: "NIMBUS7",
            1982: "NIMBUS7",
            1983: "NIMBUS7",
            1984: "NIMBUS7",
            1985: "NIMBUS7",
            1986: "NIMBUS7",
            1987: "NIMBUS7",
            1988: "F08",
            1989: "F08",
            1990: "F08",
            1991: "F10",
            1992: "F11",
            1993: "F11",
            1994: "F11",
            1995: "F11",
            1996: "F13",
            1997: "F13",
            1998: "F13",
            1999: "F13",
            2000: "F13",
            2001: "F13",
            2002: "F13",
            2003: "F15",
            2004: "F15",
            2005: "F15",
            2006: "F16",
            2007: "F16",
            2008: "F16",
            2009: "F17",
            2010: "F17",
            2011: "F17",
            2012: "F17",
            2013: "F17",
            2014: "F18",
            2015: "F19",
            2016: "F18",
        }

        sensor_dict = {
            "F16": "SSMIS",
            "F17": "SSMIS",
            "F18": "SSMIS",
            "F19": "SSMIS",
            "NIMBUS7": "SMMR",
            "F08": "SSMI",
            "F10": "SSMI",
            "F11": "SSMI",
            "F13": "SSMI",
            "F14": "SSMI",
            "F15": "SSMI",
        }

        sensor = sensors[date.year]
        ssmi_s = sensor_dict[sensor]
        # NIMBUS drops off on aug 21, 1987 and F08 starts
        if datetime(1987, 8, 21) <= date <= datetime(1988, 1, 1):
            sensor = "F08"
            ssmi_s = "SSMI"

        if not self.high_res:
            if date in [datetime(2003, 11, 6), datetime(2004, 4, 9)]:
                sensor = "F14"
            if date in [
                datetime(2006, 11, 4),
                datetime(2006, 12, 1),
                datetime(2008, 2, 26),
            ]:
                sensor = "F15"
                ssmi_s = "SSMI"
            if date in pd.date_range(
                datetime(2008, 3, 6), datetime(2008, 12, 31)
            ):
                sensor = "F17"

        return sensor, ssmi_s

    def get_file(self, date, channel):  # add more defaulting params
        """
        Function that uses date and channel to find optimal file composition
        and return the file params for the web scraper's use.
        Parameters
        ----------
        date: datetime
            date to find file path for
        channel: str
            19H vs 37H channel
        """
        # JPL curated the data up to (1987,8,21) then CSU
        input_org = "JPL" if date < datetime(1987, 8, 21) else "CSU"
        # there is no 19H on NIMBUS7, scrape 18H (similar)
        if channel == "19H" and date < datetime(1987, 8, 21):
            channel = "18H"

        # determine if high res or not
        if self.high_res:
            resolution = "6.25km" if channel in ["19H", "18H"] else "3.125km"
            algorithm = "SIR"
            date2 = date
        else:  # low res data has problems with file paths, these were manually fixed
            resolution = "25km"
            algorithm = "GRD"
            if datetime(2003, 1, 1) <= date <= datetime(2008, 3, 5):
                date2 = date - timedelta(days=1)
            else:
                date2 = date

        if self.grid == "T":
            pass1 = "A"
        elif date in [
            datetime(2005, 5, 12),
            datetime(2006, 2, 4),
            datetime(2008, 1, 2),
            datetime(2008, 2, 26),
        ]:
            pass1 = "E"
        else:
            pass1 = "M"

        sensor, ssmi_s = self.get_sensor(date)
        file = {
            "protocol": "http" if self.local_session else "https",
            "server": "localhost:8000"
            if self.local_session
            else "n5eil01u.ecs.nsidc.org",
            "datapool": "MEASURES",
            "resolution": resolution,
            "platform": sensor,
            "sensor": ssmi_s,
            "date1": date,
            "date2": date2,
            "channel": channel,
            "grid": self.grid,
            "dataversion": "v1.3",
            "pass": pass1,
            "algorithm": algorithm,
            "input": input_org,
        }
        return file

    def concatenate(self, outname19=None, outname37=None, all=False):
        """
        Function to concatenate files in the subsetted data folders.
        Input parameter is simply to allow for nesting of functions.

        Parameters
        ----------
        outname19 : str
            output file name for 19Ghz
        outname37 : str
            output file name for 37GHz
        all : Boolean
        """

        if self.subBool is False:
            self.sub19list = (
                self.down19list
            )  # sublist is getting reset back to the full download list
            self.sub37list = self.down37list
            os.chdir(self.wget)
        outname19 = self.outfile_19 if outname19 is None else outname19
        outname37 = self.outfile_37 if outname37 is None else outname37
        # Concatenate 19GHz files:
        if len(self.sub19list) != 0:
            nco.ncrcat(input=self.sub19list, output=outname19, options=["-O"])
            for file in self.sub19list:
                os.remove(file)
            self.sub19list = []
            self.down19list = []
            if all:
                self.concat19list.append(outname19)
            else:
                self.concatlist[0] = outname19
        else:
            print("No 19Ghz Files to Concatenate")
        # Concatenate 37GHz files:
        if len(self.sub37list) != 0:
            nco.ncrcat(input=self.sub37list, output=outname37, options=["-O"])
            for file in self.sub37list:
                os.remove(file)
            self.sub37list = []
            self.down37list = []
            if all:
                self.concat37list.append(outname37)
            else:
                self.concatlist[1] = outname37
        else:
            print("No 37Ghz Files to Concatenate")
        return outname19, outname37

    def final_concat(self):
        """
        Manage the final concatenation for scrape_all
        """
        if len(self.concat19list) != 0:
            nco.ncrcat(
                input=self.concat19list, output=self.outfile_19, options=["-O"]
            )
            self.concatlist[0] = self.outfile_19
        else:
            print("No 19Ghz Files to Concatenate")
        if len(self.concat37list) != 0:
            nco.ncrcat(
                input=self.concat37list, output=self.outfile_37, options=["-O"]
            )
            self.concatlist[1] = self.outfile_37
        else:
            print("No 37Ghz Files to Concatenate")

        # clean out files that were concatenated
        for file in self.concat19list:
            os.remove(file)
        for file in self.concat37list:
            os.remove(file)
        self.concat19list = []
        self.concat37list = []
        return self.outfile_19, self.outfile_37

    def scrape(self, dates=None):
        """
        Wrapper function to interface between swepy and nD

        Parameters
        ----------
        dates: List(datetime*)
            list of dates to scrape from
        """

        if self.local_session is False:
            if self.check_params() is False:
                return
        if dates is None:  # letting class choose all dates
            dates = self.dates
        for date in tqdm(dates):
            file19 = self.get_file(date, "19H")
            file37 = self.get_file(date, "37H")
            result1 = self.nD.download_file(**file19)
            if result1 is False:
                try:
                    result1 = self.nD.download_file(**file19)
                except:
                    print("failing on 19H {}".format(date))
                    pass
            result2 = self.nD.download_file(**file37)
            if result2 is False:
                try:
                    result2 = self.nD.download_file(**file37)
                except:
                    print("failing on 37H on {}".format(date))
                    pass
            self.down19list.append(result1[0])
            self.down37list.append(result2[0])
        return (result1, result2)

    @staticmethod
    def safe_subtract(tb19, tb37):
        """
        Check size of each file, often the 19 and 37
        matrices are one unit off of eachother.

        Chops the larger matrix to match the smaller matrix
        """

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
        tb19 = tb19[:, : s1[1] - 1, : s1[2] - 1]
        tb37 = tb37[:, : s2[1] - 1, : s2[2] - 1]
        tb = tb19 - tb37
        return tb

    def clean_dirs(self):
        """
        Delete files in directory
        Useful for cleaning up with repeated testing
        """

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

    def check_params(self):
        """
        Helper function to check that all the class members are set before
        attempting to web scrape or subset.

        Used by test suite and to check params are set before scraping.
        """

        proceed = True
        try:
            params = {
                "dates": self.dates,
                "bounding coordinates": self.geo_list,
                "grid": self.grid,
                "username": self.nD.username,
                "password": self.nD.password,
            }
        except AttributeError:
            print(
                "You are not logged in! Please enter your EarthData credentials with 'set_login()'"
            )
            return False
        for key, value in params.items():
            if value is None:
                print("{} needs to be set by 'set_params'".format(key))
                proceed = False
        if proceed is False:
            print(
                "Please use the set_() functions to set missing parameters,\
                    see the documentation for guidance"
            )
        return proceed
