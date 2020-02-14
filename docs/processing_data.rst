Cleaning and Filtering SWE Data with ``process``
================================================

SWEpy's ``process`` module is built to allow fast access to your temperature brightness files.
It also facilitates the cleaning of missing values and smoothing of messy data. 

.. image:: smoothing.png

Opening SWE Arrays with ``get_array``
-------------------------------------

netCDF files are great for storing data, but they aren't always the easiest to work with. Especially 
since we store our 19GHz band at a lower resolution than the 37GHz band, we have to downsample one array 
to match the other anytime we want to find SWE. 

In order to save time, ``get_array`` looks at metadata of a given file to determine whether to donwsample or not.
This way, with one function call we can extract the temperature brightness and immediatly begin working with our data.

.. code-block:: python 

    tb19 = process.get_array("my_19ghz_file.nc")
    tb37 = process.get_array("my_37ghz_file.nc")


Cleaning Missing Data Values in TB Arrays
-----------------------------------------


