Getting Started with SWEpy
==========================

SWEpy has a range of functionality, but the main use case is obtaining SWE data within a given study region
without needing massive amounts of disc space. 

SWEpy needs four key things to be instantiated: 

1. Upper Left and Lower Right Bounding Coordinates (EASE Grid 2.0 orientation)

2. Start and End Dates 

3. Working Directory Path

4. Earthdata username and password 

Basic Use for Scraping Area of Interest Cubes
---------------------------------------------

The ``swepy.pipeline`` module contains the ``Swepy`` class, which is our main tool for getting and subsetting SWE data. 

In order to scrape, subset, and concatenate imagery into a single time cube, we only need to give ``Swepy`` the four parameters listed above.  

.. code-block:: python 

    from swepy.pipeline import Swepy

    upper_left = [lon_upleft, lat_upleft]
    lower_right = [lon_lowright, lat_lowright]

    start = datetime.date(startY, startM, startD)
    end = datetime.date(endY, endM, endD)

    path = os.getcwd()

    username = <username>
    password = <password>

    swepy = Swepy(path, start, end, upper_left, lower_right, username, password, high_res = True)


Scraping Entire Grid Imagery
----------------------------
Instead of subsetting data based on an area of interest, SWEpy also supports scraping entire grids instead.
In order to do this, all you need to change is set the bounding corners to the grid name: 

- North: "N"

- South: "S"

- Equator: "T"

.. code-block:: python 

    upper_left = "N"
    lower_right = "N"


Preset Information Stored in SWEpy
----------------------------------

SWEpy is optimized to get SWE data in the hands of researchers as quickly as possible.
This means that in order to reduce the number of parameters you need to pass to the class
we had to make some decisions for you: 

- Morning Imagery will be used (as oppposed to evening) to reduce wet snow impacts

- 19H and 37H 6.25km and 3.125km images will be downloaded respectively

- SWEpy will choose a grid (N,S,T) based on the provided bounding coordinates 

- Optimal Sensor (Nimbus7 through F19) for each year will be used 

    - Many years have more than one available sensor, and they vary in quality


