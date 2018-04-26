import datetime
import subprocess
import shlex
from subprocess import call
import pandas as pd
import ease2conv as e2
from nco import Nco
import os
from tqdm import tqdm
import glob
import flowMod
import sys
nco = Nco()


print("\n\n\nScript for downloading, subsetting, and concatenating the data you want!\n")
try:
    lat_ul, lon_ul = input('Enter the upper left latitude,longitude \n(comma seperated <62.27, -140.17>): ').split(",")#[62.27, -140.17]
    lat_ul = str(lat_ul)
    lat_ul = lat_ul.replace(" ", "").strip()
    lon_ul = str(lon_ul)
    lon_ul = lon_ul.replace(" ", "").strip()
except:
    print("Wrong input type detected")
    sys.exit(1)
try:
    lat_lr, lon_lr = input('\nEnter lower right latitude,longitude\n (comma seperated <73.64, -166.08>): ').split(",")#[73.64, -166.08]
    lat_lr = str(lat_lr)
    lat_lr = lat_lr.replace(" ", "").strip()
    lon_lr = str(lon_lr)
    lon_lr = lon_lr.replace(" ", "").strip()
except:
    print("Wrong input type detected")
    sys.exit(1)
try:
    startY, startM = input("\nEnter starting year and month \n(comma seperated <2001, 5>): ").split(",")
    startY = str(startY)
    startY = startY.replace(" ", "").strip()
    startM = str(startM)
    startM = startM.replace(" ", "").strip()
except:
    print("Wrong input type detected")
    sys.exit(1)
try:
    endY, endM = input("\nEnter ending year and month \n(comma seperated <2005, 10>): ").split(",")
    endY = str(endY)
    endY = endY.replace(" ","").strip()
    endM = str(endM)
    endM = endM.replace(" ","").strip()
except:
    print("Wrong input type detected")
    sys.exit(1)

print(lat_ul, lon_ul, lat_lr, lon_lr, startY, startM, endY, endM)
ul = [float(lat_ul), float(lon_ul)]
lr = [float(lat_lr), float(lon_lr)]
days = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

start = datetime.date(int(startY), int(startM), 1)
end = datetime.date(int(endY), int(endM), days[int(endM)])
#dates = pd.date_range(start, end)
#dates = dates.strftime('%Y.%m.%d')
#this correctly prints the dates! yay
list3  = flowMod.get_xy(ul, lr)
flowMod.scrape_all(start, end, list3)
print (start,end)
