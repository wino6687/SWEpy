import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from netCDF4 import Dataset
from swepy.swepy import swepy 
from swepy.process import process 
from jenks import jenks 


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
        self.time = pd.date_range(start_date, periods = np.shape(self.swe)[0], freq = "D")
        self.melt_df = self.make_df(start_date)
        self.year_splits = self.create_year_splits()

    
    def make_df(self, time):
        df = pd.DataFrame(columns=['time', 'count'])
        df.time = time 
        df['count'].values[:] = 0
        return df
    
    def create_year_splits(self):
        years = set(self.time.year)
        years = list(years)
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
                                self.melt_df.loc[d,'count'] += 1
                                bool_1[x,y] = True
        return


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
        

