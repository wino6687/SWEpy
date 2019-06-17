import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from netCDF4 import Dataset
from swepy.swepy import swepy 
from swepy.process import process 
from multiprocessing import Pool, Process, cpu_count


class Analysis():

    def __init__(self, start_date, swe):
        """
        Parameters
        ----------
        start_date: datetime
            Day to start building time series off of 
            Infer length from number of days in data
        """
        self.swe = swe 
        self.start_date = start_date
        self.time = pd.date_range(start_date, periods = np.shape(self.swe)[0], freq = "D")
        #self.melt_df = self.make_df(time)
        self.year_splits = self.create_year_splits()


    def make_df(self, time):
        df = pd.DataFrame(columns=['time', 'count'])
        df.time = time 
        df['count'].values[:] = 0
        return df


    def create_year_splits(self):
        years = set(self.time.year)
        years = list(years)
        print(years)
        leap_years = [1992, 1996, 2000, 2004, 2008, 2012, 2016]
        year_splits = [0]
        for i,year in enumerate(years):
            if years[i-1] in leap_years:
                year_splits.append(year_splits[-1]+366)
            else: 
                year_splits.append(year_splits[-1]+365)
        return year_splits

    
    def count_melt_onset(self):
        """
        Count the number of pixels to reach zero on a given date. 
        Useful for comparison between years of a given region.
        """
        melt_df = self.make_df(self.time)
        for i, year in enumerate(self.year_splits[0:len(self.year_splits)-1]):
        # generate melt date boolean matrix
            bool_1 = np.zeros((np.shape(self.swe)[1], np.shape(self.swe)[2]), dtype=bool)
            # loop through the days of this year 
            for d in range(self.year_splits[i],self.year_splits[i+1]-1):
                # loop through x and then y of the image 
                for x in range(np.shape(self.swe)[1]):
                    for y in range(np.shape(self.swe)[2]):
                        if bool_1[x,y] == False: 
                            if self.swe[d,x,y] == 0: # less than 5mm is zero (error)
                                melt_df.loc[d,'count'] += 1
                                bool_1[x,y] = True
        self.melt_df =  melt_df # should this be stored in the class??
        return melt_df
    

    def count_melt_onset_index(self, swe):
        """
        Count the number of pixels to reach zero on a given date. 
        Useful for comparison between years of a given region.
        """
        melt_df = self.make_df(self.time)
        for i, year in enumerate(self.year_splits[0:len(self.year_splits)-1]):
        # generate melt date boolean matrix
            bool_1 = np.zeros((np.shape(swe)[1], np.shape(swe)[2]), dtype=bool)
            # loop through the days of this year 
            for d in range(self.year_splits[i],self.year_splits[i+1]-1):
                # loop through x and then y of the image 
                for x in range(np.shape(swe)[1]):
                    for y in range(np.shape(swe)[2]):
                        if bool_1[x,y] == False: 
                            if swe[d,x,y] == 0: # less than 5mm is zero (error)
                                melt_df.loc[d,'count'] += 1
                                bool_1[x,y] = True
        return melt_df


    def count_melt_onset_mp(self):
        """
        Helper function to manage multi-processing pool for counting 
        melt onset date. 

        Parralelize on the 2nd axis (spatially)

        Returns:
        --------
        df: pandas DataFrame 
                Count of melt dates of every pixel in image 
        """
        cpus = cpu_count()
        swe_parts = np.array_split(self.swe, cpus, axis=2)
        with Pool(cpus) as p:
            parts = p.map(self.count_melt_onset_index, swe_parts)
            df = parts[0] # recombine parts 
            for i in range(1,len(parts)):
                df['count'] = df['count'].add(parts[i]['count'])
            return df


    def mask_year_df(self, year):
        mask = self.melt_df["time"].dt.year == year 
        return df[mask]


    def melt_date_year(self):
        df_dict = {}
        counts_dict = {}
        for i in set(self.time.year):
            df_dict[i] = mask_year_df(self.melt_df, i)
            counts_dict[i] = df_dict[i]['count'].values
        return counts_dict

"""
Need to decide on a flow here. Do i want the user to have to pick and choose the analysis they want, or do they just instantiate the class and it all happens? 

Only reason not to do it all is each piece is slow and there is a lot of computation to each piece
"""
        

