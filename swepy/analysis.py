import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from multiprocessing import Pool, Process, cpu_count
import math


class Analysis:
    def __init__(self, start_date, swe):
        """
        Parameters
        ----------
        start_date: datetime
            Day to start building time series off of
            Infer length from number of days in data
        """
        self.leap_years = [1992, 1996, 2000, 2004, 2008, 2012, 2016]
        self.swe = swe
        self.start_date = start_date
        self.time = pd.date_range(
            start_date, periods=np.shape(self.swe)[0], freq="D"
        )
        # self.melt_df = self.make_df(time)
        self.year_splits = self.create_year_splits()

    def make_df(self, time=None, columns=["time", "count"]):
        """
        Given a time array, create dateframe with time and count columns

        Tool for melt onset workflow

        Parameters
        ----------
        time: pd.series
            time series of datetime.date() objects
        columns: list (Optional)
            column names to add in returned dataframe

        Returns
        -------
        df: pd.DataFrame
            dataframe with time and count for melt onset analysis
        """
        if time is None:
            time = self.time
        df = pd.DataFrame(columns=columns)
        df.time = time
        df["count"].values[:] = 0
        return df

    def create_year_splits(self):
        """
        Take time array from class and create an array of year split indexes

        Returns
        -------
        year_splits: list
            list of julian dates for the start of each year in time series
        """
        years = set(self.time.year)
        years = list(years)
        print("Years in time series: {}".format(years))
        tt = self.start_date.timetuple()
        if tt.tm_yday != 1:
            year_splits = [tt.tm_yday]
        else:
            year_splits = [0]
        for i, year in enumerate(years):
            if years[i - 1] in self.leap_years:
                year_splits.append(year_splits[-1] + 366)
            else:
                year_splits.append(year_splits[-1] + 365)
        if year_splits[-1] > np.shape(self.swe)[0]:
            year_splits[-1] = np.shape(self.swe)[0]
        return year_splits

    def count_melt_onset_index(self, swe):  # RENAME __COUNT
        """
        Count the date that each pixel reaches zero for first time of season on a given date.
        Useful for comparison between years of a given region.

        Parameters
        ----------
        swe: np.array
            swe cube (should be clean and relatively smooth)
        """
        melt_df = self.make_df(self.time)
        for i, year in enumerate(
            self.year_splits[0 : len(self.year_splits) - 1]
        ):
            # generate melt date boolean matrix
            bool_1 = np.zeros((np.shape(swe)[1], np.shape(swe)[2]), dtype=bool)
            # loop through the days of this year
            for d in range(self.year_splits[i], self.year_splits[i + 1] - 1):
                # loop through x and then y of the image
                for x in range(np.shape(swe)[1]):
                    for y in range(np.shape(swe)[2]):
                        if bool_1[x, y] is False:
                            if (
                                swe[d, x, y] == 0
                            ):  # less than 5mm is zero (error)
                                melt_df.loc[d, "count"] += 1
                                bool_1[x, y] = True
        return melt_df

    def count_melt_onset_mp(self):  # RENAME, get rid of mp
        """
        Count the date that each pixel reaches zero for first time of season on a given date.
        Useful for comparison between years of a given region.

        Helper function to manage multi-processing pool for counting
        melt onset date. Use __count to use a single core

        Parralelize on the 2nd axis (spatially)

        Returns
        -------
        df: pandas DataFrame
                Count of melt dates of every pixel in image
        """
        cpus = cpu_count()
        swe_parts = np.array_split(self.swe, cpus, axis=2)
        with Pool(cpus) as p:
            parts = p.map(self.count_melt_onset_index, swe_parts)
            df = parts[0]  # recombine parts
            for i in range(1, len(parts)):
                df["count"] = df["count"].add(parts[i]["count"])
            return df

    def mask_year_df(self, df, year):
        """
        Mask single year out of pandas dataframe based on "time" column

        Parameters
        ----------
        df: pd.DataFrame
            dataframe containing a "time" column
        year: datetime.date
            desired year to get from df
        """
        mask = df["time"].dt.year == year
        return df[mask]

    def melt_date_year(self, df):
        """
        Grab the counts of each year and stick them in own key of dictionary
        Makes for easy comparison of melt times each year.

        Parameters
        ----------
        df: pd.DataFrame
            dataframe with columns ["time", "count"]

        Returns
        -------
        counts_dict: dict
            dictionary with key=year : value=sum(count in year)
        """
        df_dict = {}
        counts_dict = {}
        for i in set(self.time.year):
            df_dict[i] = self.mask_year_df(df, i)
            counts_dict[i] = df_dict[i]["count"].values
        return counts_dict

    def summer_length(self, smooth_cube):
        """
        Function to track summer length for a pixel over each year
        Generates hash table of key:value = (x,y): summer length in days

        Parameters
        ----------
        smooth_cube: np.array
            smoothed (temporally) swe cube

        Returns
        -------
        store: dict
            dict using tuple (x,y) as hash key and list of summer lengths by year as key
        """
        shape = np.shape(smooth_cube)
        store = {}
        for x in range(shape[1]):
            for y in range(shape[2]):
                lengths = {}
                firstofyear = True
                f = 0
                lastofyear = True
                time = smooth_cube[:, x, y].tolist()
                for index, val in enumerate(time, start=1):
                    if index % 365 != 0:
                        if val == 0 and firstofyear:
                            f = index % 365
                            firstofyear = False
                        if val != 0 and firstofyear is False and lastofyear:
                            summerlength = ((index - 1) % 365) - f
                            lengths[math.floor((index / 365) + 1993)] = (
                                lengths.get(
                                    math.floor((index / 365) + 1993), 0
                                )
                                + summerlength
                            )
                            lastofyear = False
                    else:
                        firstofyear = True
                        lastofyear = True
                store[(x, y)] = lengths
        return store

    def summer_diff(self, summer_dict, smooth_cube=None):
        """
        Find the average change in summer length by pixel and overall

        Parameters
        ----------
        summer_dict: dict
            dictionary containing the summer lengths of each year by pixel
        smooth_cube: np.array(x,x,x)
            swe cube of clean swe data, OPTIONAL
        """
        if smooth_cube is None:
            smooth_cube = self.swe
        shape = np.shape(smooth_cube)
        diffmap = np.zeros((shape[1], shape[2]))
        total_diff = 0
        for key in summer_dict:  # grab new pixel dict
            keys = list(summer_dict[key].keys())
            diff = sum(
                [
                    summer_dict[keys[i]] - summer_dict[keys[i - 1]]
                    for i in range(1, len(keys))
                ]
            )
            diffmap[key[0], key[1]] = diff / 12
            total_diff += diff / 6
        self.diffmap = diffmap
        return total_diff / len(summer_dict.keys()), diffmap

    def display_summer_change(self, interactive=False):
        """
        Simple built in function for displaying the generated summer change heat map

        Parameters
        ----------
        interactive: bool
            boolean switch for unit testing to help close plots (would like to remove)
        """
        im = plt.imshow(self.diffmap)
        plt.colorbar()
        if interactive:
            plt.ion()
            plt.show()
            plt.pause(0.001)
            plt.close()
        else:
            plt.show()
        return im

    def display_melt_onset_change(self, dict, year1, year2, interactive=False):
        """
        CURRENTLY ONLY WORKS IF FULL YEARS ARE SCRAPED
        Given a dictionary of melt onset counts by date, viz two years against eachother

        Parameters
        ----------
        dict: dict
            dictionary of year:list(counts by year) pairs
        year1: datetime.date
            first year to plot on bar graph
        year2: datetime.date
            second year to plot on bar graph
        interactive: bool
            Unit testing parameter to help closing plots

        Returns
        -------
        fig: matplotlib.figure.Figure
            figure for future viz if desired
        """
        len1 = 366 if year1 in self.leap_years else 365
        len2 = 366 if year2 in self.leap_years else 365
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        try:
            plt.bar(
                np.arange(len1),
                dict[year1],
                ec="black",
                width=1,
                zorder=2,
                label=str(year1),
            )
        except KeyError:
            print("Year 1 is not in the time series, please try again")
            raise KeyError
        try:
            plt.bar(
                np.arange(len2),
                dict[year2],
                ec="black",
                fc="red",
                width=1,
                zorder=4,
                alpha=0.50,
                label=str(year2),
            )
        except KeyError:
            print("Year 2 is not in the time series, please try again")
            raise KeyError
        plt.title(
            "Initial Zero SWE Date: {} and {}".format(str(year1), str(year2)),
            fontsize=20,
        )
        plt.xlabel("Day of Year", fontsize=16)
        plt.ylabel("Count of Pixels to Reach Zero", fontsize=16)
        plt.grid(0.25, zorder=1)
        plt.xlim([50, 200])
        plt.legend()
        if interactive:
            plt.ion()
            plt.show()
            plt.pause(0.001)
            plt.close()
        else:
            plt.show()
        return fig
