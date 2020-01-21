from mapboxgl.utils import create_color_stops, df_to_geojson
from mapboxgl.viz import CircleViz
import numpy as np
import swepy.process as process
from skimage.measure import block_reduce
import os
import swepy.easeReproject as easeReproject
import pandas as pd
import numpy.ma as ma
from netCDF4 import Dataset


def extract_arrays(file):
    """
    Extract TB, x, y arrays from either 19H or 37H files.

    Parameters
    ----------
    file: str
        filename for 19H or 37H file
    """
    fid = Dataset(file, "r", format="NETCDF4")
    tb = fid.variables["TB"][:]
    x = fid.variables["x"][:]
    y = fid.variables["y"][:]
    if fid.variables["crs"].long_name == "EASE2_N3.125km":
        tb[tb.mask] = 0.00001
        tb = block_reduce(tb, block_size=(1, 2, 2), func=np.mean)
        fid.close()
        return ma.masked_values(tb, 0.00001)
    else:
        fid.close()
        return tb, x, y


def plot_a_day(token, files, working_dir=os.getcwd(), inday=None):
    """Plot swe subset with mapbox for confirmation of study area

    Takes final files from workflow, opens them, dumps info into geojson
    and plots via mapbox. It is recommended to use a jupyter notebook for viewing.

    Parameters
    ----------
    token: string
        mapbox token
    files: list
        list of file names ['19H', '37H']
    working_dir: str
        the location you would like to store geojson data
    inday: int
        day of time series to plot on, defaults to 0
    """
    # DATE SETUP
    day = 0 if inday is None else inday

    tb19, x, y = extract_arrays(files[0])
    tb37 = extract_arrays(files[1])

    tb = process.safe_subtract(tb19, tb37)
    lats = np.zeros((len(y), len(x)), dtype=np.float64)
    lons = np.zeros((len(y), len(x)), dtype=np.float64)
    grid = easeReproject.EaseReproject(gridname="EASE2_N6.25km")
    one_day = tb[day, :, :]
    row_c, col_c = grid.map_to_grid(x[0], y[0])
    lat_c, lon_c = grid.grid_to_geographic(row_c, col_c)
    # DATAFRAME CREATION (SLOW)
    df = pd.DataFrame(columns=["lat", "lon", "swe"])
    for i, xi in enumerate(x):
        for j, yj in enumerate(y):
            row, col = grid.map_to_grid(xi, yj)
            lat, lon = grid.grid_to_geographic(row, col)
            lats[j, i] = lat
            lons[j, i] = lon
    for i in range(len(one_day[:, 1])):
        for j in range(len(one_day[1, :])):
            df = df.append(
                {"lat": lats[i][j], "lon": lons[i][j], "swe": one_day[i][j]},
                ignore_index=True,
            )

    # SAVE DATAFRAME AS GEOJSON
    os.chdir(working_dir)
    df_to_geojson(
        df,
        filename="swe_1day.geojson",
        properties=["swe"],
        lat="lat",
        lon="lon",
    )
    measure = "swe"
    color_breaks = [
        round(df[measure].quantile(q=x * 0.1), 2) for x in range(1, 9)
    ]
    color_stops = create_color_stops(color_breaks, colors="YlGnBu")
    # Create the viz from the dataframe
    viz = CircleViz(
        "swe_1day.geojson",
        access_token=token,
        color_property="swe",
        color_stops=color_stops,
        center=(lon_c, lat_c),  # FIX CENTER, GET FROM INPUT FILES
        zoom=3,
        below_layer="waterway-label",
    )

    viz.show()
