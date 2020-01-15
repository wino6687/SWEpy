from mapboxgl.utils import create_color_stops, df_to_geojson
from mapboxgl.viz import CircleViz
import numpy as np
import swepy.process as process
from skimage.measure import block_reduce
import os
import swepy.easeReproject as easeReproject
import pandas as pd
import numpy.ma as ma


def plot_a_day(self, token, files, inday=None):
    """Plot swe subset with mapbox for confirmation of study area

    Takes final files from workflow, opens them, dumps info into geojson
    and plots via mapbox. It is recommended to use a jupyter notebook for viewing.

    Parameters
    ----------
    token: string
        mapbox token
    files: list
        list of file names ['19H', '37H']
    inday: int
        day of time series to plot on, defaults to 0
    """
    day = 0 if inday is None else inday
    # if no files passed, use final concatenated cubes
    fid_19H = process.get_array(files[0])
    fid_37H = process.get_array(files[1])

    # extract x,y, and tb from cubes
    x = fid_19H.variables["x"][:]
    y = fid_19H.variables["y"][:]

    tb_19H = fid_19H.variables["TB"][:]
    tb_37H = fid_37H.variables["TB"][:]
    if self.high_res is True:  # downsample tb37
        tb_37H[tb_37H.mask] = 0.00001
        tb_37H = block_reduce(tb_37H, block_size=(1, 2, 2), func=np.mean)
        tb_37H = ma.masked_values(tb_37H, 0.00001)

    tb = self.safe_subtract(tb_19H, tb_37H)
    lats = np.zeros((len(y), len(x)), dtype=np.float64)
    lons = np.zeros((len(y), len(x)), dtype=np.float64)
    grid = easeReproject.EaseReproject(
        gridname=fid_19H.variables["crs"].long_name
    )
    one_day = tb[day, :, :]
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
    os.chdir(self.working_dir)
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
        center=(self.center),
        zoom=3,
        below_layer="waterway-label",
    )

    viz.show()
