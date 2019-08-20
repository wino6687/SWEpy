Getting Started with SWEpy
==========================

SWEpy has a range of functionality, but the main use case is obtaining SWE data within a given study region
without needing massive amounts of disc space. 

SWEpy needs four key things to be instantiated: 

1. Upper Left and Lower Right Bounding Coordinates (EASE Grid 2.0 orientation)

2. Start and End Dates 

3. Working Directory Path

4. Earthdata username and password 

Basic Use
---------

In order to scrape, subset, and concatenate imagery into a single time cube, we only need to give ``Swepy`` these four things: 

``
upper_left = [lon_upleft, lat_upleft]
lower_right = [lon_lowright, lat_lowright]

start = datetime.date(startY, startM, startD)
end = datetime.date(endY, endM, endD)

path = os.getcwd()

username = <username>
password = <password>

swepy = swepy(path, start, end, upper_left, lower_right, username, password, high_res = True)
``