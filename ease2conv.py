#!/usr/bin/env python


from affine import Affine   # noqa
from osgeo import ogr, osr   # noqa
import re   # noqa
import sys   # noqa

m_per_km = 1000.
resolutions = ["25", "12.5", "6.25", "3.125"]


class Ease2Transform():
    """
    The Ease2Transform class provides map projection conversion routines
    for geographic (lat/lon), grid (row/col), and map (x,y) locations in
    EASE-Grid 2.0 projections.

    2016-02-27 M. J. Brodzik brodzik@nsidc.org 303-492-8263
    National Snow & Ice Data Center, Boulder CO
    Copyright (C) 2016 Regents of the University of Colorado at Boulder
    """
    gridname = None
    epsg4326Proj4text = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"

    def __init__(self, gridname=None, verbose=False):
        """
        cetbtools.ease2conv.EASE2Transform(gridname)

        Returns a Transform object for the specified gridname.

        Parameters: gridname : string
                        EASE-Grid 2.0 gridname, following the pattern:
                        "EASE2-<proj><res>km", where:
                        <proj> is "N", "S" or "T"
                        <res> is "25", "12.5", "6.25" or "3.125"
                    verbose: bool, optional
                        If set to True, write verbose output to stderr

        Returns: initialized transformer for gridname

        Example:

        from cetbtools.ease2conv import Ease2Transform
        N25grid = Ease2Transform("EASE2_N25km")

        """
        self.gridname = gridname
        g = re.match(r'(EASE2_[NST])([0-9\.]+)km', gridname)
        if g is None:
            print("%s : error parsing gridname %s" % (__name__, gridname),
                  file=sys.stderr,
                  flush=True)
            raise ValueError
        projection = g.group(1)
        resolution = g.group(2)

        # Check for typos in resolution
        if resolution not in resolutions:
            print("%s : unrecognized resolution %s" % (__name__, resolution),
                  file=sys.stderr,
                  flush=True)
            raise ValueError

        # The geotransform information
        # is the set of GDAL affine transform parameters:
        # (map_UL_x, scale_x, b, map_UL_y, d, scale_y)
        if projection == "EASE2_N":
            # The geotransform is the set of GDAL affine transform parameters:
            # (map_UL_x, scale_x, b, map_UL_y, d, scale_y)
            self.proj4text = "+proj=laea +lat_0=90 +lon_0=0 " + \
                "+x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m"
            self.map_UL_x = -9000000.
            self.map_UL_y = 9000000.
            self.b = 0.
            self.d = 0.
            self.scale_x = float(resolution) * m_per_km
            self.scale_y = -1 * float(resolution) * m_per_km

        elif projection == "EASE2_S":
            self.proj4text = "+proj=laea +lat_0=-90 +lon_0=0 " + \
                "+x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m"
            self.map_UL_x = -9000000.
            self.map_UL_y = 9000000.
            self.b = 0.
            self.d = 0.
            self.scale_x = float(resolution) * m_per_km
            self.scale_y = -1 * float(resolution) * m_per_km

        elif projection == "EASE2_T":
            self.proj4text = "+proj=cea +lat_0=0 +lon_0=0 +lat_ts=30 " \
                "+x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m"
            self.map_UL_x = -17367530.44
            self.map_UL_y = 6756820.20000
            self.b = 0.
            self.d = 0.
            base_resolution_m = 25025.26000
            factor = resolutions.index(resolution)
            self.scale_x = base_resolution_m / (2. ** factor)
            self.scale_y = -1 * base_resolution_m / (2. ** factor)

        else:
            print("%s : unrecognized projection %s" % (__name__, projection),
                  file=sys.stderr,
                  flush=True)
            raise ValueError

        # Thanks to affine help pages at
        # https://github.com/sgillies/affine/blob/master/README.rst
        # http://www.perrygeo.com/python-affine-transforms.html
        geotransform = (self.map_UL_x + self.scale_x / 2.,
                        self.scale_x,
                        self.b,
                        self.map_UL_y + self.scale_y / 2.,
                        self.d,
                        self.scale_y)
        self.fwd = Affine.from_gdal(*geotransform)

        # Initialize and save coordinate transformation
        # for this projection
        self.gridSpatialRef = osr.SpatialReference()
        self.gridSpatialRef.SetFromUserInput(self.proj4text)

        # Initialize and save coordinate transformation
        # for EPSG4326 (lat/lon)
        self.epsg4326SpatialRef = osr.SpatialReference()
        self.epsg4326SpatialRef.SetFromUserInput(self.epsg4326Proj4text)

        # Initialize and save the forward and reverse transformations
        self.projToGeog = osr.CoordinateTransformation(
            self.gridSpatialRef, self.epsg4326SpatialRef)
        self.geogToProj = osr.CoordinateTransformation(
            self.epsg4326SpatialRef, self.gridSpatialRef)

        if verbose:
            print("%s : initialized new Ease2Transform object" % (__name__),
                  file=sys.stderr,
                  flush=True)

    def grid_to_map(self, row, col):
        """
        cetbtools.ease2conv.Ease2Transform.grid_to_map(row, col)

        Parameters: row, col : scalars
                        grid locations to convert, grid origin defined as
                        (row, col) = (0., 0.) at center of UL grid cell

        Returns: (x, y) map coordinates in meters

        Example:

        from cetbtools.ease2conv import Ease2Transform

        N25grid = Ease2Transform("EASE2_N25km")
        (x, y) = N25grid.grid_to_map(-0.5, -0.5)

        Returns (x, y) = (-9000000., 9000000), UL corner of UL cell

        """
        ax, ay = self.fwd * (col, row)

        return (ax, ay)

    def grid_to_geographic(self, row, col):
        """
        cetbtools.ease2conv.Ease2Transform.grid_to_geographic(row, col)

        Parameters: row, col : scalars
                        grid locations to convert, grid origin defined as
                        (row, col) = (0., 0.) at center of UL grid cell

        Returns: (lat, lon) geographic coordinates in degrees

        Example:

        from cetbtools.ease2conv import Ease2Transform

        N25grid = Ease2Transform("EASE2_N25km")
        (lat, lon) = N25grid.grid_to_geographic(359.5, 359.5)

        Returns (lat, lon) = (90., 0.), North pole

        """
        # Get map coordinates of row, col
        x, y = self.grid_to_map(row, col)

        # Create a geometry with the map coordinates
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)

        point.Transform(self.projToGeog)

        return (point.GetY(), point.GetX())

    def map_to_grid(self, x, y):
        """
        cetbtools.ease2conv.Ease2Transform.map_to_grid(x, y)

        Parameters: x, y : scalars
                        map locations (in meters) to convert

        Returns: (row, col) grid coordinates, grid origin defined as
                        (row, col) = (0., 0.) at center of UL grid cell

        Example:

        from cetbtools.ease2conv import Ease2Transform

        N25grid = Ease2Transform("EASE2_N25km")
        (row, col) = N25grid.map_to_grid(-9000000., 9000000.)

        Returns (row, col) = (-0.5, -0.5), UL corner of UL cell

        """
        col, row = ~self.fwd * (x, y)

        return (row, col)

    def geographic_to_grid(self, lat, lon):
        """
        cetbtools.ease2conv.Ease2Transform.geographic_to_grid(lat, lon)

        Parameters: lat, lon : scalars
                        geographic coordinates (in degrees) to convert

        Returns: (row, col) converted grid location, grid origin defined as
                        (row, col) = (0., 0.) at center of UL grid cell

        Example:

        from cetbtools.ease2conv import Ease2Transform

        N25grid = Ease2Transform("EASE2_N25km")
        (row, col) = N25grid.geographic_to_grid(90., 0.)

        Returns (row, col) = (359.5, 359.5), grid location of North pole

        """
        # Create a geometry with the geographic coordinates
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)

        point.Transform(self.geogToProj)

        # Returned values are in meters, convert to grid
        row, col = self.map_to_grid(point.GetX(), point.GetY())

        return (row, col)
