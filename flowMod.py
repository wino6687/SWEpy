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
nco = Nco()

def scrape(sensor, dates, path, path_data):
    # store the path of the url before the data (the date is updated on the fly)
    file_pre = 'https://n5eil01u.ecs.nsidc.org/MEASURES/NSIDC-0630.001/'
    # noinspection PyInterpreter
    if sensor in ['F16', 'F17', 'F18', 'F19']:
        post_19 = '/NSIDC-0630-EASE2_N6.25km-'+sensor+'_SSMIS-'
        last_19 = '-19H-M-SIR-CSU-v1.2.nc'
        post_37 = '/NSIDC-0630-EASE2_N3.125km-'+sensor+'_SSMIS-'
        last_37 = '-37H-M-SIR-CSU-v1.2.nc'
    else:
        post_19 = '/NSIDC-0630-EASE2_N6.25km-'+sensor+'_SSMI-'
        last_19 = '-19H-M-SIR-CSU-v1.2.nc'
        post_37 = '/NSIDC-0630-EASE2_N3.125km-'+sensor+'_SSMI-'
        last_37 = '-37H-M-SIR-CSU-v1.2.nc'
    for date in tqdm(dates):
        # convert datetimeindex to date time
        temp = pd.datetime.strptime(date, '%Y.%m.%d')
        # Store the year of the current date, convert to day of year
        year = temp.year
        temp = str(temp.timetuple().tm_yday)
        # pad front of day of year with zeroes to always be 3 char long
        temp = temp.rjust(3, '0')
        add = str(year)+temp
        # Combine constant file portions with dynamic portions
        new_file_19 = file_pre + date + post_19 + add +last_19
        new_file_37 = file_pre + date + post_37 + add + last_37
        # Call wget on this file
        cmd = 'wget -nd --load-cookies '+path+'/cookies.txt --save-cookies '+path+'/cookies.txt --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off -P '+path_data+' '+new_file_19
        cmd2 = 'wget -nd --load-cookies '+path+'/cookies.txt --save-cookies '+path+'/cookies.txt --keep-session-cookies --no-check-certificate --auth-no-challenge=on -r --reject "index.html*" -np -e robots=off -P '+path_data+' '+new_file_37
        #print("Downloading the 19GHz and 37GHz files for: %s" % date)
        subprocess.call(shlex.split(cmd), shell = False)
        subprocess.call(shlex.split(cmd2), shell = False)
    print('Finished')

def get_xy(ll_ul, ll_lr):
    N6 = e2.Ease2Transform("EASE2_N6.25km")
    N3 = e2.Ease2Transform("EASE2_N3.125km")
    # get x,y for 6.25
    row, col = N6.geographic_to_grid(ll_ul[0], ll_ul[1])
    x6ul, y6ul = N6.grid_to_map(row,col)
    row, col = N6.geographic_to_grid(ll_lr[0], ll_lr[1])
    x6lr, y6lr = N6.grid_to_map(row, col)
    # get x,y for 3.125
    row, col = N6.geographic_to_grid(ll_ul[0], ll_ul[1])
    x3ul, y3ul = N6.grid_to_map(row, col)
    row, col = N6.geographic_to_grid(ll_lr[0], ll_lr[1])
    x3lr, y3lr = N6.grid_to_map(row, col)
    list_6 = [x6ul, y6ul, x6lr, y6lr]
    list_3 = [x3ul, y3ul, x3lr, y3lr]
    return list_3, list_6

def subset(list3, list6, path19, path37, wget):
    os.chdir(wget)
    # Make a list of the files to concatenate together for 19H
    list19 = sorted(glob.glob("*19H-M-SIR*"))
    # Make list for the 37GHz
    list37 = sorted(glob.glob("*37H-M-SIR*"))
    for file in tqdm(list19):
        outfile = path19 + file
        infile = wget + file
        opt = [
            "-d x,%f,%f" % (list6[0],list6[2]),
            "-d y,%f,%f" % (list6[3],list6[1]),
            "-v TB"
        ]
        nco.ncks(input=infile, output=outfile, options=opt)
        os.remove(infile)

    for file in tqdm(list37):
        outfile = path37 + file
        infile = wget + file
        opt = [
            "-d x,%f,%f" % (list6[0],list6[2]),
            "-d y,%f,%f" % (list6[3],list6[1]),
            "-v TB"
        ]
        nco.ncks(input=infile, output=outfile, options=opt)
        os.remove(infile)

def concatenate(path, outfile_19, outfile_37):
    os.chdir(path + '/data' + '/Subsetted_19H')
    list19 = glob.glob('NSIDC*nc')
    list19.sort()
    # Concatenate 19GHz files:
    if len(list19) != 0:
        nco.ncrcat(input=list19, output = outfile_19, options=["-O"])
    else:
        print("No 19Ghz Files to Concatenate")

    # Concatenate 37GHz files:
    os.chdir(path + '/data' + '/Subsetted_37H')
    list37 = glob.glob('NSIDC*nc')
    list37.sort()
    if len(list37) != 0:
        nco.ncrcat(input = list37, output = outfile_37, options = ["-O"])
    else:
        print("No 37Ghz Files to Concatenate")
