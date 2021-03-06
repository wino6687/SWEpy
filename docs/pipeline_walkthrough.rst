Accessing Data with SWEpy ``pipeline``
======================================

Obtaining, Subsetting, Concatenating Data
-----------------------------------------

SWEpy's data ``pipeline`` is built around three functions: 

- ``scrape()``

- ``subset()``

- ``concatentate()``

These functions can be used independently. However, SWEpy also has
a function ``scrape_all()`` that runs the entire worflow of
scraping, subsetting, and concatenating data into a single cube. 

Like we have seen before, in order to use SWEpy, we must first instantiate our class: 

.. code-block:: python 

    import swepy.pipeline as pipe

    upper_left = [lon_upleft, lat_upleft]
    lower_right = [lon_lowright, lat_lowright]

    start = datetime.date(startY, startM, startD)
    end = datetime.date(endY, endM, endD)

    path = os.getcwd()

    username = <username>
    password = <password>

    swepy = Swepy(path, upper_left, lower_right, high_res = True)
    swepy.set_login(username, password)
    swepy.set_dates(start, end)

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

Subsetting Existing Data
------------------------

Sometimes we need to subset data that we have previously stored. This means SWEpy doesn't have the filepaths saved from scraping them.
The important step of subsetting files on your machine is to put them in a folder inside your data directory. See the following example: 

Data Directory: 

.. code-block::

    data/
        wget/
        Subsetted_19H/
        Subsetted_37H/
        <Your_Data_Here>/

**Your data can go in two places:**
1. Existing ''wget/'' folder 
2. New folder you've created

Example use after data is put in ``wget/`` folder:

.. code-block:: python

    ul = [60,-133]
    lr = [69,-147]
    swe = pipe.Swepy(ul=ul, lr=lr)
    swe.subset(in_dir='wget/')