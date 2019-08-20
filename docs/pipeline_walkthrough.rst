Obtaining, Subsetting, Concatenating Data
=========================================

SWEpy's Pipeline
----------------

SWEpy's data ``pipeline`` is built around three functions: 

- ``scrape()``

- ``subset()``

- ``concatentate()``

These functions can be used independently. However, SWEpy also has
a function ``scrape_all()`` that runs the entire worflow of
scraping, subsetting, and concatenating data into a single cube. 

Like we have seen before, in order to use SWEpy, we must first instantiate our class: 

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

Once your class is instantiated we can do two things: 

.. code-block:: python 
    swepy.scrape()
    swepy.subset()
    swepy.concatentate()

or

.. code-block:: python
    swepy.scrape_all()


The key difference of using ``scrape_all()`` versus each individual function is that
``scrape_all()`` is desinged to manage disc space. It will always stop scraping to subset and concatenate every
300 days. This will keep disc impact below 10Gb at all times, which makes scraping on a local machine much easier.
