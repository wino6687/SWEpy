Advanced Use Cases
==================

Set/Change Parameters after Instantiating Class 
-----------------------------------------------

If you need to add or change class parameters that are set during class instantiation
you can use their given ``set`` functions. 

With the following ``set`` functions you can: 

- ``set_grid``: alter the bounding coordinates of AOI

- ``set_login``: login to Earthdata or change credentials

- ``set_dates``: change/add the start/end times of the time series

.. code-block:: python 

    swepy = Swepy(os.getcwd())

    swepy.set_grid(ul = [-145, 66], lr = [-166, 73])

    swepy.set_login(username = "Test", password = "Test")

    swepy.set_dates(start=datetime.date(2010,1,1), end=datetime.date(2010,2,1))