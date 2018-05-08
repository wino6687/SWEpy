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
    startY, startM, startD = input("\nEnter starting year, month, and day \n(comma seperated <2001, 5, 1>): ").split(",")
    startY = str(startY)
    startY = startY.replace(" ", "").strip()
    startM = str(startM)
    startM = startM.replace(" ", "").strip()
    startD = str(startD)
    startD = startD.replace(" ", "").strip()
except:
    print("Wrong input type detected")
    sys.exit(1)
try:
    endY, endM, endD = input("\nEnter ending year, month, and day \n(comma seperated <2005, 10, 15>): ").split(",")
    endY = str(endY)
    endY = endY.replace(" ","").strip()
    endM = str(endM)
    endM = endM.replace(" ","").strip()
    endD = str(endD)
    endD = endD.replace(" ", "").strip()
except:
    print("Wrong input type detected")
    sys.exit(1)

print(lat_ul, lon_ul, lat_lr, lon_lr, startY, startM, endY, endM)
ul = [float(lat_ul), float(lon_ul)]
lr = [float(lat_lr), float(lon_lr)]

start = datetime.date(int(startY), int(startM), int(startD))
end = datetime.date(int(endY), int(endM), int(endD))
#dates = pd.date_range(start, end)
#dates = dates.strftime('%Y.%m.%d')
#this correctly prints the dates! yay
list3  = flowMod.get_xy(ul, lr)
flowMod.scrape_all(start, end, list3)
print (start,end)
