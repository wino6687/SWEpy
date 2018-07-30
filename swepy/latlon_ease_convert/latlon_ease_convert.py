from affine import Affine
from osgeo import ogr, osr
import re
import sys

# list of available resolutions in dataset
resolutions = ["25", "12.5", "6.25", "3.125"]
class convert():
    '''
    This class was developed to convert between lat/lon and ease 2.0 coordinates.
    It was developed by Mary Jo Brodzik at the National Snow and Ice Data Center.
    The original source code can be found at https://bitbucket.org/nsidc/cetbtools
    It was included here with permission from the original author
    because of conda channel dependency issues with using the original package.
    '''
    grid = None
    epsg4326_proj4 = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
    def __init__(self, grid=None):
        self.grid = grid
        # use regular expressions to build gridname with projection
        g = re.match(r'(EASE2_[NST])([0-9\.]+)km', grid)
        # get projection and resolution from the constructed gridname
        projection = g.group(1)
        resolution = g.group(2)
        # set affine parameters based on projection
        if projection == "EASE2_N":
            # (map_UL_x, scale_x, b, map_UL_y,d,scale_y)
            self.proj4text = "+proj=laea +lat_0=90 +lon_0=0 +x_0=0 + y_0=0 +ellps=WGS84 +datum=WGS84 +units=m"
            self.map_UL_x = -9000000.
            self.map_UL_y = 9000000.
            self.b = 0.
            self.d = 0.
            self.scale_x = float(resolution) * 1000. #1000 m_per_km
            self.scale_y = -1 * float(resolution) * 1000.
        elif projection == "EASE2_S":
            self.proj4text = "+proj=laea +lat_0=-90 +lon_0=0 +x_0=0 + y_0=0 +ellps=WGS84 +datum=WGS84 +units=m"
            self.map_UL_x = -9000000.
            self.map_UL_y = 9000000.
            self.b = 0.
            self.d = 0.
            self.scale_x = float(resolution) * 1000.
            self.scale_y = -1 * float(resolution) * 1000.
        elif projection == "EASE2_T":
            self.proj4text = "+proj=laea +lat_0=0 +lon_0=0 +lat_ts=30 +x_0=0 + y_0=0 +ellps=WGS84 +datum=WGS84 +units=m"
            self.map_UL_x = -17367530.44
            self.map_UL_y = 6756820.20000
            self.b = 0.
            self.d = 0.
            base_res_m = 25025.26000
            factor = resolutions.index(resolution)
            self.scale_x = base_res_m / (2. ** factor)
            self.scale_y = -1 * base_res_m / (2. ** factor)
        else:
            print("%s is not a recognized projection"%(projection))
        # create the geotransform params
        # https://github.com/sgillies/affine/blob/master/README.rst
        geotrans = (self.map_UL_x + self.scale_x / 2.,
                    self.scale_x,
                    self.b,
                    self.map_UL_y + self.scale_y / 2.,
                    self.d,
                    self.scale_y)
        # pass geotransform params to affine
        self.fwd = Affine.from_gdal(*geotrans)

        # initialize and save coord transformation for this proj
        self.gridSpatialRef = osr.SpatialReference()
        self.gridSpatialRef.SetFromUserInput(self.proj4text)

        # Initialize and save coordinate transformation for EPSG4326 (lat/lon)
        self.epsg4326SpatialRef = osr.SpatialReference()
        self.epsg4326SpatialRef.SetFromUserInput(self.epsg4326_proj4)

        # Initialize and save the forward and reverse transformations
        self.projToGeog = osr.CoordinateTransformation(
            self.gridSpatialRef, self.epsg4326SpatialRef)
        self.geogToProj = osr.CoordinateTransformation(
            self.epsg4326SpatialRef, self.gridSpatialRef)

    def grid_to_map(self, row, col):
        '''
        Parameters: row, col
            grid origin is defined as (row, col) = (0., 0.) at center of UL grid cell

        Returns: (x,y) map coordinates in meters
        '''
        x1, y1 = self.fwd * (col, row)
        return (x1, y1)

    def grid_to_geographic(self, row, col):
        '''
        Parameters: row, col
            grid origin is defined as (row, col) = (0., 0.) at center of UL grid cell

        Returns: (lat, lon) geographic coordinates in degrees
        '''
        # get map coordiates of row, col
        x, y = self.grid_to_map(row, col)

        # make a geom w/ map coordinates
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x,y)

        point.Transform(self.projToGeog)

        return (point.GetY(), point.GetX())

    def map_to_grid(self, x, y):
        '''
        Parameters: x, y
            Map locations (meters) to convert

        Returns: (row, col) grid coordinates
            grid origin is defined as (row, col) = (0., 0.) at center of UL grid cell
        '''
        col, row = ~self.fwd*(x,y)
        return (row, col)

    def geographic_to_grid(self,lat,lon):
        '''
        Parameters: lat, lon
            geographic coordinates (degrees) to convert
        Returns: (row, col) converted grid locations
            grid origin is defined as (row, col) = (0., 0.) at center of UL grid cell
        '''
        # create point at lat/lon coordinate
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(lon, lat)
        # transform the projection
        point.Transform(self.geogToProj)
        # use the point's x,y coordinate and map_to_grid to obtain row,col
        row, col = self.map_to_grid(point.GetX(), point.GetY())
        return (row,col)
